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
 *                    mysendto6
 *=============================================================================
 * Description: send 'hello!' over IPv6 socket
 * Parameters:  ipstr - receiver's IPv6 address 
 * Returns:     0 - send data successfully
 *              errno: any socket issues
 *
 */
int 
mysendto6(char *ipstr)  
{  
    int mysocket;  
    struct sockaddr_in6 addr;  
    int addr_len;  
    char msg[8] = "hello!"; 
    if ((mysocket = socket(AF_INET6, SOCK_DGRAM, 0)) < 0)  
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
    setsockopt(mysocket, IPPROTO_IPV6, IPV6_HOPLIMIT,
                      &optval, sizeof(optval));
                      
    addr_len = sizeof(struct sockaddr_in6);  
    bzero(&addr, sizeof(addr));  
    addr.sin6_family = AF_INET6;  
    addr.sin6_port = htons(REMOTEPORT);  
    inet_pton(AF_INET6, ipstr, &addr.sin6_addr);  

    if (sendto(mysocket, msg, sizeof(msg), 0, (struct sockaddr *)&addr, addr_len) < 0)  
    {  
	    perror("sendto");  
        close(mysocket);
        return errno;  
    }  
    
    close(mysocket);
    return 0;
}
