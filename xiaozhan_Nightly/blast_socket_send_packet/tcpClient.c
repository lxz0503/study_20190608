/* tcpClient.c - TCP client example */
/*
DESCRIPTION
This file contains the client-side of the TCP example code.
The example code demonstrates the usage of several BSD 4.4-style
socket routine calls.
*/

/* includes */
#include "vxWorks.h"
#include "sockLib.h"
#include "inetLib.h"
#include "stdioLib.h"
#include "strLib.h"
#include "hostLib.h"
#include "ioLib.h"
#include "tcpExample.h"

/****************************************************************************
*
* tcpClient - send requests to server over a TCP socket
*
* This routine connects over a TCP socket to a server, and sends a
* user-provided message to the server. Optionally, this routine
* waits for the server's reply message.
*
* This routine may be invoked as follows:
* -> tcpClient "remoteSystem"
* Message to send:
* Hello out there
* Would you like a reply (Y or N):
* y
* value = 0 = 0x0
* -> MESSAGE FROM SERVER:
* Server received your message
*
* RETURNS: OK, or ERROR if the message could not be sent to the server.
*/

static int quit = 0;

STATUS tcpClient
(
	char * serverName /* name or IP address of server */
)
{
	struct tcpRequest myRequest;    /* request to send to server */
	struct sockaddr_in serverAddr;  /* server's socket address */
	char replyBuf[REPLY_MSG_SIZE];  /* buffer for reply */
	char reply;                     /* if TRUE, expect reply back */
	int sockAddrSize;               /* size of socket address structure */
	int sFd;                        /* socket file descriptor */
	int mlen;                       /* length of message */
	int repeatTimes = 2;    
	int noStop = 0;	

	printf("TCP client start...\n");

	/* create client's socket */
	if ((sFd = socket (AF_INET, SOCK_STREAM, 0)) == ERROR)
	{
		perror ("socket");
		return (ERROR);
	}
    
	/* bind not required - port number is dynamic */
    
	/* build server socket address */
	sockAddrSize = sizeof (struct sockaddr_in);
	bzero ((char *) &serverAddr, sockAddrSize);
	serverAddr.sin_family = AF_INET;
	serverAddr.sin_len = (u_char) sockAddrSize;
	serverAddr.sin_port = htons (SERVER_PORT_NUM);
	if (((serverAddr.sin_addr.s_addr = inet_addr (serverName)) == ERROR) &&
	((serverAddr.sin_addr.s_addr = hostGetByName (serverName)) == ERROR))
	{
		perror ("unknown server name");
		close (sFd);
		return (ERROR);
	}
    
	/* connect to server */
	if (connect (sFd, (struct sockaddr *) &serverAddr, sockAddrSize) == ERROR)
	{
		perror ("connect");
		close (sFd);
		return (ERROR);
	}
    
	/* build request, prompting user for message */
	printf ("Message to send: \n");
	mlen = read (STD_IN, myRequest.message, REQUEST_MSG_SIZE);
	myRequest.msgLen = mlen;
	myRequest.message[mlen - 1] = '\0';
	
	printf ("Would you like a reply (Y or N): \n");
	read (STD_IN, &reply, 1);


	switch (reply)
	{
		case 'y':
		case 'Y': myRequest.reply = TRUE;
		break;
		default: myRequest.reply = FALSE;
		break;
	}
 
/*	   
	printf ("How many times do you want to repeat the sending? (1-9, 1 means 500 times; 0 menas NoStop; n means no repeat): \n");
	read (STD_IN, &reply, 1);
	switch (reply)
	{
		case '1': repeatTimes = 500; break;
		case '2': repeatTimes = 1000; break;
		case '3': repeatTimes = 1500; break; 	
		case '4': repeatTimes = 2000; break;
		case '5': repeatTimes = 2500; break;
		case '6': repeatTimes = 3000; break;
		case '7': repeatTimes = 3500; break;
		case '8': repeatTimes = 4000; break;
		case '9': repeatTimes = 4500; break;
		case '0': noStop = 1; break;
		default:  break;
	}
 
*/		
/*        while( (repeatTimes-- || noStop == 1 ) && quit == 0) */
/*	{*/
		/* send request to server */
		if (write (sFd, (char *) &myRequest, sizeof (myRequest)) == ERROR)
		{
			perror ("write");
			close (sFd);
			return (ERROR);
		}
    
   	 	/* if expecting reply, read and display it */
		if (myRequest.reply) 
		{
			if (read (sFd, replyBuf, REPLY_MSG_SIZE) < 0)
			{
				perror ("read");
				close (sFd);
				return (ERROR);
			}
/*			if (repeatTimes < 10) */
				printf ("MESSAGE FROM SERVER:\n%s\n", replyBuf); 
		}
/*	} */


	close (sFd);
	return (OK);
}

/*
STATUS quit()
{
	quit = 1;
}
*/
