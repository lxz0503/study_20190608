/* rtpMain.c - used for test ipnet support CORE SAFETY */

/*
 * Copyright (c) 1988-2018, 2021 Wind River Systems, Inc.
 *
 * The right to copy, distribute, modify or otherwise make use
 * of this software may be licensed only pursuant to the terms
 * of an applicable Wind River license agreement.
 */

#include <vxWorks.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

extern STATUS testStartUdpServer ();
extern STATUS testStartUdpClient 
    (
    char * ipaddr,
    long   loopCount
    );

int main 
    (
    int    argc,        /* number of arguments */
    char * argv[]       /* array of arguments */
    )
    {
    if (argc != 4)
        {
        printf ("usage: rtp.vxe server|client ip loopcount\n");
        return 0;
        }
    
    if (strcmp (argv[1], "server") == 0) /* run as server */
        {
        return testStartUdpServer ();
        }
    else
        return testStartUdpClient (argv[2], atol (argv[3]));
    }
