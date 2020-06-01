/* blasteeTCPux.c - TCP ethernet transfer benchmark for Unix */
                    
/*
 * Copyright (c) 1986-2001, 2010 Wind River Systems, Inc.
 *
 * The right to copy, distribute, modify or otherwise make use
 * of this software may be licensed only pursuant to the terms
 * of an applicable Wind River license agreement.
 */

/*               
modification history
--------------------
04b,27jan10,x_z  remove zbuf and add support for multiple interfaces.
04a,10may01,jgn  Checkin for AE
03c,20May99,gow  Split off from blastee.c
03b,17May99,gow  Extended to zero-copy sockets
03a,02Mar99,gow  Better documentation. Tested Linux as "blastee".
02a,19dec96,lej  Fitted formatting to Wind River convention
01b,15May95,ism  Added header
01a,24Apr95,ism  Unknown Date of origin
*/                               
                                 
/*
DESCRIPTION
   With this module, a Unix target ("blasteeTCP") receives
   blasts of TCP packets and reports network throughput on 10
   second intervals.

SYNOPSIS
   blasteeTCP (port, size, bufsize, bindaddr)

   where:

   port = port that "blasterTCP" should connect with
   size = number of bytes per "blast"
   bufsize = size of receive-buffer for blasteeTCP's BSD socket
             (usually, size == bufsize)
   bindaddr = address to be bound

EXAMPLE
   To start this test, issue the following VxWorks command on the
   target:

   sp blasteeTCP,5000,16000,16000                   (for default interface)

   or

   sp blasteeTCP,5000,16000,16000,"10.255.255.8"    (for "10.255.255.8")

   then issue the following UNIX commands on the host:

   gcc -O -Wall -o blasterTCP blasterTCPux.c -lsocket   (solaris)
   gcc -O -Wall -DLINUX -o blasterTCP blasterTCPux.c    (linux)
   blasterTCP 10.255.255.8 5000 16000 16000  (use appropriate IP address)

   Note: blasteeTCP should be started before blasterTCP because
   blasterTCP needs a port to connect to.

   To stop this test, call blasteeTCPQuit(index) in VxWorks or kill
   blasterTCP on UNIX with a control-c.

   The "blasterTCP"/"blasteeTCP" roles can also be reversed. That is,
   the VxWorks target can be the "blasterTCP" and the UNIX host can
   be the "blasteeTCP". In this case, issue the following UNIX
   commands on the host:

   gcc -O -Wall -o blasteeTCP blasteeTCPux.c -lsocket    (solaris)
   gcc -O -Wall -DLINUX -o blasteeTCP blasteeTCPux.c     (linux)
   blasteeTCP 5000 16000 16000                (for default interface)

   or

   blasteeTCP 5000 16000 16000 "10.255.255.4" (for "10.255.255.4")

   and issue the following VxWorks command on the target
   (use appropriate IP address):

   sp blasterTCP,"10.255.255.4",5000,16000,16000

   To stop the test, call blasterTCPQuit() in VxWorks or kill
   blasteeTCP on Unix with a control-c.

CAVEATS
   Since this test loads the network heavily, the target and host
   should have a dedicated ethernet link.
*/

#include <sys/types.h>
#include <sys/socket.h>
#ifndef LINUX
#include <sys/filio.h>          /* solaris header */
#endif /* !LINUX */
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/time.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <unistd.h>
#include <errno.h>

static int blastNum;     /* number of bytes read per 10 second interval */

/* forward declarations */

static void blastRate ();
static void blasteeTCPQuit(int);

/*****************************************************************
 *
 * blasteeTCP - Accepts blasts of TCP packets from blasterTCP
 * 
 * This program accepts blasts of TCP packets from blasterTCP
 * and prints out the throughput every 10 seconds.
 * 
 * blasteeTCP port size bufsize bindaddr
 * 
 * where:
 * 
 * port = TCP port to connect with on "blasterTCP"
 * size = number of bytes per "blast"
 * bufsize = size of receive-buffer for blasteeTCP's BSD socket
 * bindaddr = address to be bound
 */

int main (int argc, char **argv)
    {
    struct sockaddr_in		serverAddr, clientAddr;
    char		*buffer;
    int			s;      /* server socket descriptor */
    int                 snew;   /* per-client socket descriptor */
    int                 len;    /* sizeof(clientAddr) */
    int                 nrecv;  /* number of bytes received */
    int			size;   /* size of the meesage */
    int			blen;   /* max size of socket receive buffer */

    /* parse arguments */

    if (argc < 4)
	{
	printf ("usage: %s port size bufLen (bindAddr)\n", argv [0]);
	exit (1);
	}

    size = atoi (argv [2]);
    blen = atoi (argv [3]);

    if ((buffer = (char *)malloc (size)) == NULL)
	{
	printf ("cannot allocate buffer of size %d\n", size);
	exit (1);
	}

    /* setup Unix alarm to periodically report network throughput
     */
    signal (SIGINT, blasteeTCPQuit); /* set ^c handler */
    signal (SIGALRM, blastRate);
    alarm (10);

    /* setup BSD socket to read blasts from */

    bzero ((char *) &serverAddr, sizeof (serverAddr));
    bzero ((char *) &clientAddr, sizeof (clientAddr));

    if ((s = socket (AF_INET, SOCK_STREAM, 0)) < 0)
	{
	perror("socket");
	exit (1);
	}

    serverAddr.sin_family	= AF_INET;
    serverAddr.sin_port	= htons (atoi (argv [1]));
    if (argc == 5)
        serverAddr.sin_addr.s_addr = inet_addr (argv [4]);
    else
        serverAddr.sin_addr.s_addr = INADDR_ANY;
    if (bind (s, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0)
	{
    	perror("bind");
	exit (1);
	}

    if (listen (s, 5) < 0)
	{
    	perror("listen");
	exit (1);
	}
    
    len = sizeof (clientAddr);

    while ((snew = accept (s, (struct sockaddr *)&clientAddr, &len)) == -1)
        ;

    if (setsockopt (snew, SOL_SOCKET, SO_RCVBUF,
                    (char *) &blen, sizeof (blen)) < 0)
	{
	perror("setsockopt");
	exit (1);
	}

    blastNum = 0;

    /* loop that reads TCP blasts */

    for (;;)
	{
        if ((nrecv = read (snew, buffer, size)) < 0)
            {
            if (errno == EINTR) /* keep going after SIGALRM */
                continue;
	    perror("read");
	    exit(1);
	    }
	
	blastNum += nrecv;
	}

    /* not reached */
    }


/* alarm handler. reports network throughput */

static void blastRate ()
    {
    if (blastNum > 0)
	{
	printf ("%d bytes/sec tot %d\n", blastNum / 10, blastNum);
	blastNum = 0;
	}
    else
	printf ("No bytes read in the last 10 seconds.\n");

    signal (SIGALRM, blastRate);
    alarm (10);
    }

/* SIGINT handler */

static void blasteeTCPQuit(int dummy)
    {
    printf ("blasteeTCP end.\n");
    exit(0);
    }
