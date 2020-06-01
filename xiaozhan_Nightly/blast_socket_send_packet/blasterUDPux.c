/* blasterUDPux.c - UDP ethernet transfer benchmark for Unix */

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
04c,23jun10,x_z  enable socket buffer size configuration and code clean.
04b,27jan10,x_z  add support for multiple interfaces.
04a,10may01,jgn  checkin for AE
02b,18May99,gow  created from blaster.c
*/

/*
DESCRIPTION
   With this module, Unix transmits blasts of UDP packets to
   a specified target IP/port.

SYNOPSIS
   blasterUDP targetname port size bufsize

   where:

   targetname = network address of "blasteeUDP"
   port = UDP port to connect with on "blasteeUDP"
   size = number of bytes per "blast"
   bufsize = size of transmit-buffer for blasterUDP's BSD socket
             (usually, better performance with larger bufsize)

EXAMPLE
   To start this test, issue the following VxWorks command on the
   target:

   sp blasteeUDP,5000,1000,1000                 (for default interface)

   or

   sp blasteeUDP,5000,1000,1000,"10.255.255.8"  (for "10.255.255.8")
   then issue the following UNIX commands on the host:

   gcc -O -Wall -o blasterUDP blasterUDPux.c -lsocket   (solaris)
   gcc -O -Wall -DLINUX -o blasterUDP blasterUDPux.c    (linux)
   blasterUDP 10.255.255.8 5000 1000 1000  (use appropriate IP address)

   Note: blasteeUDP should be started before blasterUDP because
   blasterUDP needs a port to send UDP packets to.

   To stop this test, call blasteeUDPQuit(index) in VxWorks or kill
   blasterUDP on UNIX with a control-c.

   The "blasterUDP"/"blasteeUDP" roles can also be reversed. That is,
   the VxWorks target can be the "blasterUDP" and the UNIX host can
   be the "blasteeUDP". In this case, issue the following UNIX
   commands on the host:

   gcc -O -Wall -o blasteeUDP blasteeUDPux.c -lsocket    (solaris)
   gcc -O -Wall -DLINUX -o blasteeUDP blasteeUDPux.c     (linux)
   blasteeUDP 5000 1000 1000                (for default interface)

   or

   blasteeUDP 5000 1000 1000 "10.255.255.4" (for "10.255.255.4")

   and issue the following VxWorks command on the target
   (use appropriate IP address):

   sp blasterUDP,"10.255.255.4",5000,1000,1000

   To stop the test, call blasterUDPQuit() in VxWorks or kill
   blasteeUDP on Unix with a control-c.

CAVEATS
   Since this test loads the network heavily, the target and host
   should have a dedicated ethernet link.

   The bufsize parameter is disabled for Linux. Changing UDP socket
   buffer size with setsockopt() in Linux somehow breaks the socket.
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

struct hostent * gethostbyname (const char *);

static void blasterUDPQuit(int);          /* forward declaration */

/*****************************************************************
 *
 * blasterUDP - Transmit blasts of UDP packets to blasteeUDP
 *
 * blasterUDP targetname port size bufsize
 *
 * where:
 *
 * targetname = network address of "blasteeUDP"
 * port = UDP port to connect with on "blasteeUDP"
 * size = number of bytes per "blast"
 * bufsize = size of transmit-buffer for blasterUDP's BSD socket
 */

int main (int argc, char **argv)
    {
    struct sockaddr_in  sin;
    int                 s; /* socket descriptor */
    int                 nsent; /* how many bytes sent */
    char *              buffer;
    int                 blen; /* max size of socket send buffer */
    int                 size; /* size of the message to be sent */
    struct hostent *    hp;

    if (argc < 5)
        {
        printf ("usage: %s targetname port size bufLen\n", argv [0]);
        exit (1);
        }

    /* setup BSD socket for transmitting blasts */

    if ((s = socket (AF_INET, SOCK_DGRAM, 0)) < 0)
        {
    perror("socket");
        exit (1);
        }

    signal(SIGINT, blasterUDPQuit);
    if ((hp = gethostbyname (argv[1])) == NULL)
        {
        fprintf (stderr, "%s: unknown host\n", argv [1]);
        exit (1);
        }
    sin.sin_addr = *((struct in_addr *)hp->h_addr);
    sin.sin_port    = htons (atoi (argv [2]));
    size        = atoi (argv [3]);
    blen = atoi (argv [4]);
    sin.sin_family  = AF_INET;
    bzero((char *)&sin.sin_zero, 8); /* zero the rest of the struct */

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

    /* Loop that transmits blasts */

    for (;;)
        {
        nsent = sendto(s, buffer, size, 0, (struct sockaddr *)&sin,
            sizeof(struct sockaddr));
        if (nsent < 0)
            {
            perror("sendto");
            exit(1);
            }
        }

    /* not reached */
    }

/* SIGINT handler */
static void blasterUDPQuit(int dummy)
    {
    printf ("blasterUDP exit.\n");
    exit(0);
    }

