https://www.cnblogs.com/zhangyingai/p/7097922.html      ---参考这个网址
socket层是一个抽象层，在应用层和传输层之间，它封装了tcp/ip的协议标准
我们只需要遵循socket编程规范，自然就遵循了tcp/ip标准
省去了研究复杂的tcp/ip标准

# import socket
# socket.socket(socket_family,socket_type,protocal=0)
# socket_family 可以是 AF_UNIX 或 AF_INET。socket_type 可以是 SOCK_STREAM 或 SOCK_DGRAM。protocol 一般不填,默认值为 0。
#
# 获取tcp/ip套接字
# tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# 获取udp/ip套接字
# udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
# 由于 socket 模块中有太多的属性。我们在这里破例使用了'from module import *'语句。
# 使用 'from socket import *',我们就把 socket 模块里的所有属性都带到我们的命名空间里了,这样能 大幅减短我们的代码。
# 例如tcpSock = socket(AF_INET, SOCK_STREAM)
 服务端套接字函数
s.bind()  # 绑定(主机,端口号)到套接字
s.listen()  # 开始TCP监听
s.accept()  # 被动接受TCP客户的连接,(阻塞式)等待连接的到来

客户端套接字函数
s.connect()  # 主动初始化TCP服务器连接
s.connect_ex()  # connect()函数的扩展版本,出错时返回出错码,而不是抛出异常
 公共用途的套接字函数
s.recv()            #接收TCP数据
s.send()            #发送TCP数据(send在待发送数据量大于己端缓存区剩余空间时,数据丢失,不会发完)
s.sendall()         #发送完整的TCP数据(本质就是循环调用send,sendall在待发送数据量大于己端缓存区剩余空间时,数据不丢失,循环调用send直到发完)
s.recvfrom()        #接收UDP数据
s.sendto()          #发送UDP数据
s.getpeername()     #连接到当前套接字的远端的地址
s.getsockname()     #当前套接字的地址
s.getsockopt()      #返回指定套接字的参数
s.setsockopt()      #设置指定套接字的参数
s.close()           #关闭套接字
close方法可以释放一个连接的资源，但是不是立即释放，
如果想立即释放，那么请在close之前使用shutdown方法
shutdown方法是用来实现通信模式的，模式分三种，
SHUT_RD 关闭接收消息通道，SHUT_WR 关闭发送消息通道，SHUT_RDWR 两个通道都关闭
也就是说，想要关闭一个连接，首先把通道全部关闭，然后在release连接，
以上三个静态变量分别对应数字常量：0,1,2, shutdown(2)即可

面向锁的套接字方法
s.setblocking()     #设置套接字的阻塞与非阻塞模式
s.settimeout()      #设置阻塞套接字操作的超时时间
s.gettimeout()      #得到阻塞套接字操作的超时时间

面向文件的套接字方法
s.fileno()          #套接字的文件描述符
s.makefile()        #创建一个与该套接字相关的文件

recv与recvfrom 注意区别
recv()返回的是接收到的数据，
recvfrom返回的是（数据,客户端地址)，可以用来接收对端的地址信息，
这个对于udp这种无连接的，可以很方便地进行回复。
而换过来如果你在udp当中也使用recv，那么就不知道该回复给谁了，如果你不需要回复的话，也是可以使用的。
另外就是对于tcp是已经知道对端的，就没必要每次接收还多收一个地址，没有意义，
要取地址信息，在accept当中取得就可以加以记录了。
https://blog.csdn.net/zj19880814/article/details/84479557

发消息，都是将数据发送到己端的发送缓冲中，收消息都是从己端的缓冲区中收（也就是内核态内存中）。

tcp：send or sendall发消息，recv收消息
udp：sendto发消息，recvfrom收消息，是带两个参数，一个是数据，一个是对端地址

粘包如何产生
TCP为了提高网络的利用率，会使用一个叫做Nagle的算法。
该算法是指，发送端即使有要发送的数据，如果很少的话，会延迟发送。
如果应用层给TCP传送数据很快的话，就会把两个应用层数据包“粘”在一起，TCP最后只发一个TCP数据包给接收端。

tcp的协议数据不会丢，没有收完包，下次接收，会继续上次继续接收，己端总是在收到ack时才会清除缓冲区内容。数据是可靠的，但是会粘包。

两种情况下会发生粘包。

1.发送端需要等缓冲区满才发送出去，造成粘包（发送数据时间间隔很短，数据了很小，会合到一起，产生粘包）--hellofeng
2.接收方不及时接收缓冲区的包，造成多个包接收  -----he    llo feng
（客户端发送了一段数据，服务端只收了一小部分，服务端下次再收的时候还是从缓冲区拿上次遗留的数据，产生粘包）

recv里指定的1024意思是从缓存里一次拿出1024个字节的数据

send的字节流是先放入己端缓存，然后由协议控制将缓存内容发往对端，
如果待发送的字节流大小大于缓存剩余空间，那么数据丢失，用sendall就会循环调用send，数据不会丢失

用python3实现组播的例子：https://www.cnblogs.com/lsdb/p/9408947.html