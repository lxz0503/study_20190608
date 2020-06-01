/* $Id: blasteeTCPvx.c,v 1.1 2010-12-06 23:17:16 ctang Exp $ */

/* blasteeTCPvx.c - TCP ethernet transfer benchmark for VxWorks */
                    
/* Copyright 1986-1999 Wind River Systems, Inc. */

/*               
modification history
--------------------
03c,20May99,gow  Split off from blastee.c
03b,17May99,gow  Extended to zero-copy sockets
03a,02Mar99,gow  Better documentation. Tested Linux as "blastee".
02a,19dec96,lej  Fitted formatting to Wind River convention
01b,15May95,ism  Added header
01a,24Apr95,ism  Unknown Date of origin
*/                               
                                 
/*
DESCRIPTION
   With this module, a VxWorks target ("blasteeTCP") receives
   blasts of TCP packets and reports network throughput on 10
   second intervals.

SYNOPSIS
   blasteeTCP (port, size, bufsize)

   where:

   port = port that "blasterTCP" should connect with
   size = number of bytes per "blast"
   bufsize = size of receive-buffer for blasteeTCP's BSD socket
             (usually, size == bufsize)

EXAMPLE
   To start this test, issue the following VxWorks command on the
   target:

   sp blasteeTCP,5000,16000,16000

   then issue the following UNIX commands on the host:

   gcc -O -Wall -o blasterTCP blasterTCPux.c -lsocket   (solaris)
   gcc -O -Wall -DLINUX -o blasterTCP blasterTCPux.c    (linux)
   blasterTCP 10.255.255.8 5000 16000 16000  (use appropriate IP address)

   Note: blasteeTCP should be started before blasterTCP because
   blasterTCP needs a port to connect to.

   To stop this test, call blasteeTCPQuit() in VxWorks or kill
   blasterTCP on UNIX with a control-c.

   The "blasterTCP"/"blasteeTCP" roles can also be reversed. That is,
   the VxWorks target can be the "blasterTCP" and the UNIX host can
   be the "blasteeTCP". In this case, issue the following UNIX
   commands on the host:

   gcc -O -Wall -o blasteeTCP blasteeTCPux.c -lsocket    (solaris)
   gcc -O -Wall -DLINUX -o blasteeTCP blasteeTCPux.c     (linux)
   blasteeTCP 5000 16000 16000

   and issue the following VxWorks command on the target
   (use appropriate IP address):

   sp blasterTCP,"10.255.255.4",5000,16000,16000

   To stop the test, call blasterTCPQuit() in VxWorks or kill
   blasteeTCP on Unix with a control-c.

CAVEATS
   Since this test loads the network heavily, the target and host
   should have a dedicated ethernet link.

*/

#include "vxWorks.h"
#include "ioLib.h"
#include "logLib.h"
#include "memLib.h"
#include "socket.h"
#include "sockLib.h"
#include "stdio.h"		
#include "stdlib.h"
#include "string.h"
#include "sysLib.h"
#include "tftpLib.h"
#include "wdLib.h"
#include "taskLib.h"

static WDOG_ID blastWd;  /* for periodic throughput reports */
static unsigned long long blastNum;     /* number of bytes read per 10 second interval */
static char *buffer;            /* receive buffer */
static int sock;      /* server socket descriptor */
static int snew;      /* per-client socket descriptor */
static int tid;                 /* task ID for cleanup purposes */
static int quitFlag;     /* flag for stopping test */

/* forward declarations */

static void blastRate ();
void blasteeTCPQuit(void);       /* global for shell accessibility */

/*****************************************************************
 *
 * blasteeTCP - Accepts blasts of TCP packets from blasterTCP
 * 
 * This program accepts blasts of TCP packets from blasterTCP
 * and prints out the throughput every 10 seconds.
 * 
 * blasteeTCP (port, size, bufsize, zbuf)
 * 
 * where:
 * 
 * port = TCP port to connect with on "blasterTCP"
 * size = number of bytes per "blast"
 * bufsize = size of receive-buffer for blasteeTCP's BSD socket
 * 
 * RETURNS:  N/A
 */

void blasteeTCP (int port, int size, int blen)
    {
    struct sockaddr_in		serverAddr, clientAddr;
    int                 len;    /* sizeof(clientAddr) */
    int                 nrecv;  /* number of bytes received */

    tid = taskIdSelf();
    if ((buffer = (char *) malloc (size)) == NULL)
	{
	printf ("cannot allocate buffer of size %d\n", size);
	return;
	}

    /* setup watchdog to periodically report network throughput */

    if ((blastWd = wdCreate ()) == NULL)
	{
	printf ("cannot create blast watchdog\n");
	free (buffer);
	return;
	}
    wdStart (blastWd, sysClkRateGet () * 10, (FUNCPTR) blastRate, 0);

    /* setup BSD socket to read blasts from */

    bzero ((char *) &serverAddr, sizeof (serverAddr));
    bzero ((char *) &clientAddr, sizeof (clientAddr));

    if ((sock = socket (AF_INET, SOCK_STREAM, 0)) < 0)
	{
	printf ("cannot open socket\n");
        wdDelete (blastWd);
	free (buffer);
        return;
	}

    serverAddr.sin_family       = AF_INET;
    serverAddr.sin_port = htons (port);

    if (bind(sock, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0)
	{
    	printf ("bind error\n");
        close (sock);
        wdDelete (blastWd);
	free (buffer);
        return;
	}

    if (listen (sock, 5) < 0)
	{
    	printf ("listen failed\n");
        close (sock);
        wdDelete (blastWd);
	free (buffer);
        return;
	}
    
    len = sizeof (clientAddr);

    while ((snew = accept(sock, (struct sockaddr *)&clientAddr, &len)) == -1)
        ;

    blastNum = 0;
    quitFlag = 0;

    if (setsockopt (snew, SOL_SOCKET, SO_RCVBUF,
                    (char *) &blen, sizeof (blen)) < 0)
	{
	printf ("setsockopt SO_RCVBUF failed\n");
        close (sock);
        close (snew);
        wdDelete (blastWd);
	free (buffer);
        return;
	}

    /* loop that reads TCP blasts */

    for (;;)
	{
	if (quitFlag == 1)
	    break;
        
        nrecv = read (snew, buffer, size);
        if (nrecv < 0)
            {
	    printf ("blasteeTCP read error\n");
	    break;
	    }
	
	blastNum += nrecv;
	}

    /* cleanup */

    wdDelete (blastWd);
    close (sock);
    close (snew);
    free (buffer);
    printf ("blasteeTCP end.\n");
    }


/* watchdog handler. reports network throughput */

static void blastRate ()
    {
    if (blastNum > 0)
	{
	logMsg ("Recv %d bytes message, %d Mbps\n", blastNum, (blastNum * 8) / (1024 * 1024 * 10),0,0,0,0);
	blastNum = 0;
	}
    else
	logMsg ("No bytes read in the last 10 seconds.\n", 0,0,0,0,0,0);

    wdStart (blastWd, sysClkRateGet () * 10, (FUNCPTR) blastRate, 0);
    }

/* make blasteeTCP stop */

void blasteeTCPQuit(void)
    {
    quitFlag = 1;
    taskDelay(60);               /* try to end gracefully */
    if (taskIdVerify(tid) == OK) /* blasteeTCP still trying to read() */
        {
        close (sock);
        close (snew);
        wdDelete (blastWd);
        free (buffer);
        taskDelete (tid);
        printf ("blasteeTCP forced stop.\n");
        }
    }
