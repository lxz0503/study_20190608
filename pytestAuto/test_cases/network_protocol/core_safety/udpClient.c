/* udpClient.c - only used for test ipnet support CORE SAFETY */

/*
 * Copyright (c) 1988-2018, 2021 Wind River Systems, Inc.
 *
 * The right to copy, distribute, modify or otherwise make use
 * of this software may be licensed only pursuant to the terms
 * of an applicable Wind River license agreement.
 */

/* includes */

#include <stdio.h>
#include <stdlib.h>
#include <sockLib.h>
#include <sys/socket.h>
#include <inetLib.h>
#include <string.h>
#include <taskLib.h>

#define PORT              2345
#define BUF_MAX           2048
#define RESULT_FILENAME   "/ram0/coresafetyresult.txt"  

LOCAL void saveResult 
    (
    BOOL bResult
    )
    {
    FILE * f = fopen (RESULT_FILENAME, "w");
    if (f != NULL)
        {
        if (bResult)
            (void) fputs ("OK", f);
        else
            (void) fputs ("ERROR", f);
        (void) fclose (f);
        }
    }

STATUS testStartUdpClient 
    (
    char * ipaddr,
    long   loopCount
    ) 
    {
    int                  index;
    struct sockaddr_in   nicSockAddr;
    struct sockaddr_in   txMsgSockAddr;
    int                  txMsgSocket;
    int                  iteration;
    ssize_t              bytesSent;
    char                 buf[BUF_MAX];
    
    memset( &txMsgSockAddr, 0, sizeof(struct sockaddr) );
    txMsgSockAddr.sin_family = PF_INET;
    txMsgSockAddr.sin_addr.s_addr = inet_addr (ipaddr);
    txMsgSockAddr.sin_port = htons (PORT);
    
    txMsgSocket = socket (PF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (txMsgSocket == ERROR)
        {
        printf ("socket failed\n");
        saveResult (FALSE);
        return ERROR;
        }

    memset( &nicSockAddr, 0, sizeof(struct sockaddr) );
    nicSockAddr.sin_family = PF_INET;
    nicSockAddr.sin_addr.s_addr = htonl (INADDR_ANY);
    
    if (bind (txMsgSocket, (struct sockaddr *)&nicSockAddr, sizeof (nicSockAddr)) == ERROR)
        {
        printf( "bind failed\n" );
        saveResult (FALSE);
        return ERROR;
        }
    
    iteration = 0;
    do
        {
        for (index = 0; index < BUF_MAX; index++ )
            buf[index ] = iteration % 255;
        
        iteration++;
        bytesSent = sendto (txMsgSocket, buf, BUF_MAX, 0, 
                            (struct sockaddr *) (&(txMsgSockAddr)),
                            sizeof (txMsgSockAddr)  
                            );
        if (iteration % 100 == 0)
            {
            printf ("Iterations[%d], bytes send: [%d]\n", iteration, bytesSent);
            (void) taskDelay (1);
            }
        }
    while (iteration < loopCount);
        
    if (iteration == loopCount)
        {
        printf( "OK\n");
        saveResult (TRUE);
        }
    else
        {
        printf( "Out of memory.\n");
        saveResult (FALSE);
        }
    
    printf( "...Exiting A_TEST_RTP\n");
    return OK;
    }

STATUS testGetResult ()
    {
    STATUS  ret    = ERROR;
    char    buf[8] = {0};
    
    FILE * f = fopen (RESULT_FILENAME, "r");
    if (f != NULL)
        {
        fgets (buf, sizeof (buf), f);
        if (strcmp (buf, "OK") == 0)
            {
            ret = OK;
            }
        } 
    
    if (ret == ERROR)
        {
        printf ("Failed\n");
        }
    else
        {
        printf ("OK\n");
        }
    return ret;
    }
