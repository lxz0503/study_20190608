/* $Id: blasterTCPvx.c,v 1.1 2010-12-06 23:17:16 ctang Exp $ */

/* blasterTCPvx.c - TCP ethernet transfer benchmark for VxWorks */

/* Copyright 1986-1999 Wind River Systems, Inc. */

/*
modification history
--------------------
02c,20May99,gow  Split off from blaster.c
02b,17May99,gow  Extended to zero-copy sockets
02a,02Mar99,gow  Better documentation. Tested Linux as "blastee".
01b,15May95,ism  Added header
01a,24Apr95,ism  Unknown Date of origin
*/

/*
DESCRIPTION
   With this module, VxWorks transmits blasts of TCP packets to
   a specified target IP/port.

SYNOPSIS
   blasterTCP (targetname, port, size, bufsize, zbuf)

   where:

   targetname = network address of "blasteeTCP"
   port = TCP port to connect with on "blasteeTCP"
   size = number of bytes per "blast"
   bufsize = size of transmit-buffer for blasterTCP's BSD socket
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
#include "types.h"
#include "socket.h"
#include "sockLib.h"
#include "inetLib.h"
#include "ioLib.h"
#include "string.h"
#include "stdio.h"
#include "stdlib.h"
#include "errno.h"

static int quitFlag;    /* set to 1 to quit blasterUDP gracefully */

void blasterTCPQuit(void);   /* global for shell accessibility */

/*****************************************************************
 *
 * blasterTCP - Transmit blasts of TCP packets to blasteeTCP
 * 
 * blasterTCP (targetname, port, size, bufsize, zbuf)
 * 
 * where:
 * 
 * targetname = network address of "blasteeTCP"
 * port = TCP port on "blasteeTCP" to receive packets
 * size = number of bytes per "blast"
 * bufsize = size of transmit-buffer for blasterTCP's BSD socket
 * 
 * RETURNS:  N/A
 */


void blasterTCP (char *targetAddr, int port, int size, int blen)
    {
    struct sockaddr_in	sin;
    int 		s;      /* socket descriptor */
    int                 nsent; /* how many bytes sent */
    char 		*buffer;

    /* setup BSD socket for transmitting blasts */

    bzero ((void *)&sin, sizeof (sin));

    if ((s = socket (AF_INET, SOCK_STREAM, 0)) < 0)
        {
	printf ("cannot create socket\n");
        return;
        }

    sin.sin_addr.s_addr	= inet_addr (targetAddr);
    sin.sin_port	= htons (port);
    sin.sin_family 	= AF_INET;

    if ((buffer = (char *) malloc (size)) == NULL)
	{
	printf ("cannot allocate buffer of size %d\n", size);
        close (s);
        return;
	}

    if (setsockopt (s, SOL_SOCKET, SO_SNDBUF, (void *)&blen,
                    sizeof (blen)) < 0)
	{
	printf ("setsockopt SO_SNDBUF failed\n");
	free (buffer);
        close (s);
        return;
	}

    if (connect (s, (struct sockaddr *)&sin, sizeof (sin)) < 0)
	{
    	printf ("connect failed: host %s port %d\n",
                inet_ntoa (sin.sin_addr), ntohs (sin.sin_port));
	free (buffer);
        close (s);
        return;
	}
    
    quitFlag = 0;

    /* Loop that transmits blasts */

    for (;;)
	{
	if (quitFlag == 1)
	    break;
        
        nsent = write(s, buffer, size);
        if (nsent < 0)
	    {
	    printf ("blasterTCP write error %d\n", errno);
	    break;
	    }
	}
    
    /* cleanup */

    free (buffer);
    close (s);
    printf ("blasterTCP exit.\n");
    }

/* make blasterTCP stop */

void blasterTCPQuit(void)
    {
    quitFlag = 1;
    }
