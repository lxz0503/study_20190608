/* udpServer.c - used for test ipnet support CORE SAFETY */

/*
 * Copyright (c) 1988-2018, 2021 Wind River Systems, Inc.
 *
 * The right to copy, distribute, modify or otherwise make use
 * of this software may be licensed only pursuant to the terms
 * of an applicable Wind River license agreement.
 */

#include <vxWorks.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <unistd.h>

#define  MAXDATASIZE       2049
#define  PORT              2345
BOOL     testStopServer = FALSE;
static BOOL  isStarted  = FALSE;

STATUS testStartUdpServer ()
    {
    int                sockfd;
    struct sockaddr_in server = {0};
    struct sockaddr_in client = {0};
    socklen_t          addrlen;
    int                num;
    char               buf[MAXDATASIZE];
    
    if (isStarted)
        return OK;
    
    if((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == -1)
        {
        printf ("Create socket failed.\n");
        return ERROR;
        }
    
    server.sin_family = AF_INET;
    server.sin_port = htons(PORT);
    server.sin_addr.s_addr = htonl (INADDR_ANY);
    
    if (bind(sockfd, (struct sockaddr *) &server, sizeof (server)) == -1)
        {
        printf ("bind error.\n");
        close (sockfd);
        return ERROR;
        }
    isStarted = TRUE;
    
    while (!testStopServer)
        {
        addrlen = sizeof(client);
        num = recvfrom (sockfd, buf, MAXDATASIZE - 1, 0, (struct sockaddr*) &client, &addrlen);
        if (num < 0)
            {
            printf ("recvfrom() error \n");
            close (sockfd);
            return ERROR;
            }
        buf[num] = '\0';
        printf ("You got a message from client. The ip is %s:%d; message is: %s\n", 
                inet_ntoa(client.sin_addr), client.sin_port, buf);
        }
    return OK;
    }

