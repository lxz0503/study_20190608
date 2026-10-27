#include <unistd.h>  
#include <stdio.h>  
#include <arpa/inet.h>  
#include <sys/socket.h>  
#include <string.h>  
#include <stdlib.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <errno.h>
#include <vxWorks.h>

#define LOCALPORT 8888  

/* 
 *=============================================================================
 *                    recvmsg_controllen_test6
 *=============================================================================
 * Description: test msg_controllen in recvmsg() all for IPv6 ancillary data
 * Parameters:  controllen - msg_controllen for ancillary data
 * Returns:     0 - test pass
 *              1:  input error
 *              -1: test failed
 *              errno: for other socket issues
 *
 */
int
recvmsg_controllen_test6(unsigned int controllen)
{  
    int mysocket;
    int len;  
    struct sockaddr_in6 addr;

    if (controllen == 0)
    {
        printf("Input error, Invalid length!\n");
        return 1;
    }

    char buf[8];
    struct iovec iov[1];
    iov[0].iov_base = buf;
    iov[0].iov_len = sizeof(buf);

    socklen_t addr_len = sizeof (struct sockaddr_in6);
    memset(&addr, 0, addr_len);

    struct msghdr msg;
    msg.msg_name = &addr;
    msg.msg_namelen = addr_len;

    int iovlen = 1;
    msg.msg_iov = &iov[0];
    msg.msg_iovlen = iovlen;

    void *controlbuf = NULL;
    controlbuf = malloc(controllen);

    msg.msg_control = controlbuf;
    msg.msg_controllen = controllen; // test condition
    msg.msg_flags = 0;

    if ((mysocket = socket(AF_INET6, SOCK_DGRAM, 0)) < 1)  
    {  
        perror("create");  
        return errno;  
    }    
    else  
    {  
        printf("socket created ..., id: %d\n", mysocket);  
    } 
    
    int optval = 1;
	setsockopt(mysocket, IPPROTO_IPV6, IPV6_RECVHOPLIMIT,
                      &optval, sizeof(optval));
                     
    bzero(&addr, sizeof(addr));  
    addr.sin6_family = AF_INET6;  
    addr.sin6_port = htons(LOCALPORT);  
    addr.sin6_addr = in6addr_any;  
  
    if (bind(mysocket, (struct sockaddr*)&addr, sizeof(addr)) < 0)  
    {  
        perror("bind");  
        return errno;  
    }  
    else  
    {  
        printf("bind ok. \n");  
        printf("local port: %d\n", LOCALPORT);  
    } 
    printf("Original msg.msg_controllen : %d\n", msg.msg_controllen);

    len = recvmsg(mysocket, &msg, 0);  
    printf("\nlen = %d\n", len);  
    
    if (len > 0)
    {
        printf("recvmsg runs successfully.\n");
        printf("msg.iov_base : %s\n", msg.msg_iov->iov_base);
        printf("msg.msg_controllen : %d\n", msg.msg_controllen);		
        printf("msg.msg_flags: 0x%x\n", msg.msg_flags);
        if( (msg.msg_flags == MSG_CTRUNC) && (msg.msg_controllen > 0))
        {
            printf("msg.msg_control for MSG_CTRUNC should be 0\n");
            close(mysocket);
            printf("\ntest fail\n");
            return -1;
        }
    }
    else
    {
        perror("recvmsg");
        return errno;
    }
    
    close(mysocket); 
    printf("\ntest pass\n");
    
    return 0;
}
