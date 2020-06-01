/* blasterUDPvx.c - UDP ethernet transfer benchmark for VxWorks */

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
02b,18May99,gow  created from blaster.c
*/

/*
DESCRIPTION
   With this module, VxWorks transmits blasts of UDP packets to
   a specified target IP/port.

SYNOPSIS
   blasterUDP (targetname, port, size, bufsize)

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

   The bufsize parameter is disabled for VxWorks. Changing UDP socket
   buffer size with setsockopt() in VxWorks somehow breaks the socket.
*/

#include <vxWorks.h>
#include <types.h>
#include <socket.h>
#include <sockLib.h>
#include <inetLib.h>
#include <ioLib.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

static int quitFlag; /* set to 1 to quit blasterUDP gracefully */
void blasterUDPQuit(void); /* global for shell accessibility */

/*****************************************************************
 *
 * blasterUDP - Transmit blasts of UDP packets to blasteeUDP
 *
 * blasterUDP (targetname, port, size, bufsize)
 *
 * where:
 *
 * targetname = network address of "blasteeUDP"
 * port = UDP port on "blasteeUDP" to receive packets
 * size = number of bytes per "blast"
 * bufsize = size of transmit-buffer for blasterUDP's BSD socket
 *
 * RETURNS:  N/A
 */

void blasterUDP (char *targetAddr, int port, int size, int blen)
    {
    struct sockaddr_in  sin;
    int                 s; /* socket descriptor */
    int                 nsent; /* how many bytes sent */
    char *              buffer;

    /* setup BSD socket for transmitting blasts */

    if ((s = socket (AF_INET, SOCK_DGRAM, 0)) < 0)
        {
        printf ("cannot create socket\n");
        return;
        }

    sin.sin_addr.s_addr = inet_addr (targetAddr);
    sin.sin_port        = htons (port);
    sin.sin_family      = AF_INET;
    bzero((char *) &sin.sin_zero, 8); /* zero the rest of the struct */

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
        close (s);
        free (buffer);
        return;
        }

    quitFlag = 0;

    /* Loop that transmits blasts */

    for (;;)
        {
        if (quitFlag == 1)
            break;

        nsent = sendto(s, buffer, size, 0, (struct sockaddr *)&sin,
            sizeof(struct sockaddr_in));

        /* sendto() and zbufSockBufSendto() both error-out for
         * some strange reason. Somehow this doesn't seem to
         * affect the test, and we can get away with ignoring
         * the errors.
         */

        if (nsent < 0)
            continue;
        }

    /* cleanup */

    close (s);
    free (buffer);
    printf ("blasterUDP exit.\n");
    }

/* make blasterUDP stop */

void blasterUDPQuit(void)
    {
    quitFlag = 1;
    }

