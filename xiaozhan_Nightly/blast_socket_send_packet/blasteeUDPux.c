/* blasteeUDPux.c - UDP ethernet transfer benchmark for Unix */

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
04b,27jan10,x_z  remove zbuf and add support for multiple interfaces.
04a,10may01,jgn  checkin for AE
01a,18May99,gow  Created from blastee.c
*/

/*
DESCRIPTION
   With this module, a Unix target ("blasteeUDP") receives
   blasts of UDP packets and reports network throughput on 10
   second intervals.

SYNOPSIS
   blasteeUDP port size bufsize bindaddr

   where:

   port = UDP port for receiving packets
   size = number of bytes per "blast"
   bufsize = size of receive-buffer for blasteeUDP's BSD socket
             (usually, better performance with larger bufsize)
   bindaddr = address to be bound

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
   Since this test loads the network heavily, the target and source
   should have a dedicated ethernet link.

   The bufsize parameter is disabled for Linux. Changing UDP socket
   buffer size with setsockopt() in Linux somehow breaks the socket.
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

static int blastNum; /* number of bytes read per 10 second interval */

/* forward declarations */

static void blastRate ();
static void blasteeUDPQuit (int);

/*****************************************************************
 *
 * blasteeUDP - Accepts blasts of UDP packets from blasterUDP
 *
 * This program accepts blasts of UDP packets from blasterUDP
 * and prints out the throughput every 10 seconds.
 *
 * blasteeUDP port size bufsize bindaddr
 *
 * where:
 *
 * port = UDP port to connect with on "blasterUDP"
 * size = number of bytes per "blast"
 * bufsize = size of receive-buffer for blasteeUDP's BSD socket
 * bindaddr = address to be bound
 */

int main (int argc, char **argv)
    {
    struct sockaddr_in  serverAddr;
    struct sockaddr_in  clientAddr;
    char *              buffer; /* receive buffer */
    int                 sock; /* receiving socket descriptor */
    int                 nrecv; /* number of bytes received */
    int                 sockAddrSize = sizeof(struct sockaddr);
    int                 size; /* size of the meesage */
    int                 blen; /* max size of socket receive buffer */

    /* parse arguments */

    if (argc < 4)
        {
        printf ("usage: %s port size bufLen (bindAddr)\n", argv [0]);
        exit (1);
        }

    size = atoi (argv [2]);
    blen = atoi (argv [3]);
    buffer = (char *) malloc (size);
    if (buffer == NULL)
        {
        printf ("cannot allocate buffer of size %d\n", size);
        exit (1);
        }

    /*
     * setup watchdog or Unix alarm to periodically report network
     * throughput
     */

    signal (SIGINT, blasteeUDPQuit); /* set ^c handler */
    signal (SIGALRM, blastRate);
    alarm (10);

    if ((sock = socket (AF_INET, SOCK_DGRAM, 0)) < 0)
        {
        perror("socket");
        exit (1);
        }

    serverAddr.sin_family   = AF_INET;
    serverAddr.sin_port = htons (atoi (argv [1]));
    if (argc == 5)
        serverAddr.sin_addr.s_addr = inet_addr (argv [4]);
    else
        serverAddr.sin_addr.s_addr = INADDR_ANY;
    bzero((char *)&serverAddr.sin_zero, 8); /* zero rest of struct */

    if (bind (sock, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0)
        {
        perror("bind");
        exit (1);
        }

    if (setsockopt (sock, SOL_SOCKET, SO_RCVBUF,
                    (char *) &blen, sizeof (blen)) < 0)
        {
        perror("setsockopt");
        exit (1);
        }

    blastNum = 0;

    /* loop that reads UDP blasts */

    for (;;)
        {
        nrecv = recvfrom (sock, (char *)buffer, size, 0,
                          (struct sockaddr *)&clientAddr,
                          (socklen_t * __restrict__)&sockAddrSize);
        if (nrecv < 0)
            {
            if (errno == EINTR) /* keep going after SIGALRM */
                continue;

            perror("recvfrom");
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

static void blasteeUDPQuit (int dummy)
    {
    printf ("blasteeUDP end.\n");
    exit(0);
    }

