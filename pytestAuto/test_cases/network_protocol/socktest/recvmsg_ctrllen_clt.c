#include <stdio.h>  
#include <arpa/inet.h>  
#include <unistd.h>  
#include <sys/socket.h>  
#include <string.h>  
#include <errno.h>
#include <vxWorks.h>  

#define REMOTEPORT 8888  

/* 
 *=============================================================================
 *                    mysendto
 *=============================================================================
 * Description: send 'hello!' over IPv4 socket
 * Parameters:  ipstr - receiver's IPv4 address 
 * Returns:     0 - send data successfully
 *              errno: any socket issues
 *
 */
int 
mysendto(char *ipstr)  
{  
    int mysocket;  
    struct sockaddr_in addr;  
    int addr_len;  
    char msg[8] = "hello!"; 
    if ((mysocket = socket(AF_INET, SOCK_DGRAM, 0)) < 0)  
    {  
        perror("create");  
        return errno;  
    }  
    else  
    {  
        printf("socket created ..., id: %d\n", mysocket);  
        printf("rmote ip: %s\n", ipstr);  
        printf("remote port: %d\n", REMOTEPORT);  
    }  
    
    int optval = 1;
    setsockopt(mysocket, IPPROTO_IP, IP_RECVDSTADDR,
                      &optval, sizeof(optval));
                      
    addr_len = sizeof(struct sockaddr_in);  
    bzero(&addr, sizeof(addr));  
    addr.sin_family = AF_INET;  
    addr.sin_port = htons(REMOTEPORT);  
    inet_pton(AF_INET, ipstr, &addr.sin_addr);  

    if (sendto(mysocket, msg, sizeof(msg), 0, (struct sockaddr *)&addr, addr_len) < 0)  
    {  
	    perror("sendto");  
        close(mysocket);
        return errno;  
    }  
    
    close(mysocket);
    return 0;

}
