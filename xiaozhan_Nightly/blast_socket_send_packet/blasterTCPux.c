/* blasterTCPux.c - TCP ethernet transfer benchmark for Unix */

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
04b,27jan10,x_z  add support for multiple interfaces.
04a,10may01,jgn  checkin for AE
02c,20May99,gow  Split off from blaster.c
02b,17May99,gow  Extended to zero-copy sockets
02a,02Mar99,gow  Better documentation. Tested Linux as "blastee".
01b,15May95,ism  Added header
01a,24Apr95,ism  Unknown Date of origin
*/

/*
DESCRIPTION
   With this module, Unix transmits blasts of TCP packets to
   a specified target IP/port.

SYNOPSIS
   blasterTCP targetname port size bufsize

   where:

   targetname = network address of "blasteeTCP"
   port = TCP port to connect with on "blasteeTCP"
   size = number of bytes per "blast"
   bufsize = size of transmit-buffer for blasterTCP's BSD socket
             (usually, size == bufsize)

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
   blasteeTCP 5000 1000 1000                (for default interface)

   or

   blasteeTCP 5000 1000 1000 "10.255.255.4" (for "10.255.255.4")

   and issue the following VxWorks command on the target
   (use appropriate IP address):

   sp blasterTCP,"10.255.255.4",5000,1000,1000

   To stop the test, call blasterTCPQuit() in VxWorks or kill
   blasteeTCP on Unix with a control-c.

CAVEATS
   Since this test loads the network heavily, the target and host
   should have a dedicated ethernet link.

*/

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>

static void blasterTCPQuit(int);          /* forward declaration */


/*****************************************************************
 *
 * blasterTCP - Transmit blasts of TCP packets to blasteeTCP
 * 
 * blasterTCP targetname port size bufsize
 * 
 * where:
 * 
 * targetname = network address of "blasteeTCP"
 * port = TCP port to connect with on "blasteeTCP"
 * size = number of bytes per "blast"
 * bufsize = size of transmit-buffer for blasterTCP's BSD socket
 */

int main (int argc, char **argv)
    {
    struct sockaddr_in	sin;
    int 		s;      /* socket descriptor */
    int                 nsent; /* how many bytes sent */
    char 		*buffer;
    int			blen;
    int 		size;
    struct hostent 	*hp, *gethostbyname ();

    if (argc < 5)
	{
	printf ("usage: %s targetname port size bufLen\n", argv [0]);
	exit (1);
	}

    /* setup BSD socket for transmitting blasts */

    bzero ((void *)&sin, sizeof (sin));

    if ((s = socket (AF_INET, SOCK_STREAM, 0)) < 0)
        {
	perror("socket");
        exit (1);
        }

    signal(SIGINT, blasterTCPQuit);
    hp = gethostbyname (argv[1]);
    if (hp == 0 && (sin.sin_addr.s_addr = inet_addr (argv [1])) == -1)
	{
	fprintf (stderr, "%s: unknown host\n", argv [1]);
	exit (1);
	}

    if (hp != 0)
        bcopy (hp->h_addr, &sin.sin_addr, hp->h_length);

    sin.sin_port 	= htons (atoi (argv [2]));
    size		= atoi (argv [3]);
    blen = atoi (argv [4]);
    sin.sin_family 	= AF_INET;

    if ((buffer = (char *) malloc (size)) == NULL)
	{
	printf ("cannot allocate buffer of size %d\n", size);
	exit (1);
	}

    if (setsockopt (s, SOL_SOCKET, SO_SNDBUF, (void *)&blen,
                    sizeof (blen)) < 0)
	{
	perror("setsockopt");
	exit (1);
	}

    if (connect (s, (struct sockaddr *)&sin, sizeof (sin)) < 0)
	{
	perror ("connect");
	exit (1);
	}
    
    /* Loop that transmits blasts */

    for (;;)
	{
        nsent = write(s, buffer, size);
        if (nsent < 0)
	    {
	    perror("write");
            exit(1);
	    }
	}
    
    /* not reached */
    }

/* SIGINT handler */

static void blasterTCPQuit(int dummy)
    {
    printf ("blasterTCP end.\n");
    exit(0);
    }
