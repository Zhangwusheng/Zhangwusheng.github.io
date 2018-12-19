# Increase CentOS 7’s MTU



Ethernet interfaces normally use an MTU of 1500 bytes.

I recently needed to increase the MTU use by the NICs on a point-to-point link to 9000 bytes in order to improve DRBD performance. This is sometimes referred to as enabling jumbo frames.

In the past I’ve used **ifconfig** to test this change out. For example, to increase the MTU of the **eth0** interface from the default of 1500 bytes to 9000 bytes, I would run

`ifconfig eth0 mtu 9000`

I could then verify that the new MTU had been applied by running:

`ifconfig eth0`

Unfortunately for me the two servers that I was working on, like many CentOS 7 systems did not have the **ifconfig**command installed.

If you want the **ifconfig** command, then you can install it by installing the **net-tools** package:

`yum install net-tools`

However, I wanted to avoid making any changes other than increasing the MTU, so I use the **ip** command instead.

The **ip** command can be used in place of **ifconfig** for many purposes, including increasing the MTU. For example, to increase the MTU of the **eth0** interface from the default of 1500 bytes to 9000 bytes, run:

`ip link set mtu 9000 dev eth0`

You can then verify that the new MTU has taken effect by running:

`ip link show dev eth0`

After you’ve applied the new MTU, and verified that all is working as expected, be sure to update the interface’s configuration file, so that this change persists the next time the server is rebooted.

To edit the MTU for the eth0 interface, add an “MTU=” line to the **/etc/sysconfig/network-scripts/ifcfg-eth0** file. For example:

`MTU=9000`





# How to check supported MTU value for destination system and/or intermediate network ?

https://access.redhat.com/solutions/2440411

SOLUTION VERIFIED 

 

## Environment

- Red Hat Enterprise Linux (All versions).

## Issue

- How to test a particular MTU value is support ?
- How I can check if this MTU size is supported by each Network Card ?
- Is there any checklist to verify our environment is prepared for enable MTU change ?
- How to test the custom Jumbo Frames are supported ?

## Resolution

- Testing the `MTU` is supported in the network.

[Raw](https://access.redhat.com/solutions/2440411#)

```
# ping -M do -s 8972 [destination IP]
```

> ##### Note: there is an overhead of `28 bytes` for the packet size. `8 bytes` for `ICMP headers` and `20 bytes` for `Ethernet header`, so the `MTU` is `28 bytes` larger than the figure you establish through the method above. So to test for `MTU` of `9000`, you actually need to set your ping packet size to `9000-28 = 8972`.

- By adjusting the MTU value its possible to find the supported MTU value in the network.

- If the `MTU` value is not enables in the client side the `ping` output will be :

  [Raw](https://access.redhat.com/solutions/2440411#)

  ```
  PING xxx.xxx.xxx.xxx (xxx.xxx.xxx.xxx): 8184 data bytes
  ping: sendto: Message too long
  ```

- If the `MTU` value is enabled in client but not in destination (or switch in between) the `ping` output will be :

  [Raw](https://access.redhat.com/solutions/2440411#)

  ```
  PING xxx.xxx.xxx.xxx (xxx.xxx.xxx.xxx): 8184 data bytes
  Request timeout for icmp_seq 0
  ```

- If the `MTU` is supported and enabled in client and destination the `ping` output will be :

  [Raw](https://access.redhat.com/solutions/2440411#)

  ```
  PING xxx.xxx.xxx.xxx (xxx.xxx.xxx.xxx): 8184 data bytes
  8192 bytes from xxx.xxx.xxx.xxx: icmp_seq=0 ttl=128 time=0.714 ms
  ```

- 



# 什么是MTU？为什么MTU值普遍都是1500？

https://yq.aliyun.com/articles/222535

大学那会我玩魔兽世界，我的职业是法师，然后经常有朋友找我我带小号，带小号的方式是冲到血色副本里面把所有怪拉到一起，然后一起用AOE技能瞬间杀掉，在学校玩的时候没什么问题，但是放假在家的时候，我发现每次我拉好怪，放技能AOE的那个瞬间，很大概率会掉线，也不是网速问题，当时很多人也遇到同样的问题，看到个帖子说，把自己的MTU改成1480就行了，当时也不知道啥是MTU，就改了，发现还真的可以，就愉快地打游戏去了，多年以后我才知道MTU的重要性。

## 什么是MTU

Maximum Transmission Unit，缩写MTU，中文名是：最大传输单元。

## 这是哪一层网络的概念？

从下面这个表格中可以看到，在7层网络协议中，MTU是**数据链路层**的概念。MTU限制的是数据链路层的payload，也就是**上层协议**的大小，例如IP，ICMP等。

| OSI中的层  | 功能                                   | TCP/IP协议族                             |
| ---------- | -------------------------------------- | ---------------------------------------- |
| 应用层     | 文件传输，电子邮件，文件服务，虚拟终端 | TFTP，HTTP，SNMP，FTP，SMTP，DNS，Telnet |
| 表示层     | 数据格式化，代码转换，数据加密         | 没有协议                                 |
| 会话层     | 解除或建立与别的接点的联系             | 没有协议                                 |
| 传输层     | 提供端对端的接口                       | TCP，UDP                                 |
| 网络层     | 为数据包选择路由                       | IP，ICMP，RIP，OSPF，BGP，IGMP           |
| 数据链路层 | 传输有地址的帧以及错误检测功能         | SLIP，CSLIP，PPP，ARP，RARP，MTU         |
| 物理层     | 以二进制数据形式在物理媒体上传输数据   | ISO2110，IEEE802，IEEE802.2              |

## MTU有什么用？

举一个最简单的场景，你在家用自己的笔记本上网，用的是路由器，路由器连接电信网络，然后访问了`www.baidu.com`，从你的笔记本出发的一个以太网数据帧总共经过了以下路径：

```
笔记本 -> 路由器 -> 电信机房 -> 服务器
```

其中，每个节点都有一个MTU值，如下：

```
1500     1500                 1500
笔记本 -> 路由器 -> 电信机房  -> 服务器
```

假设现在我把笔记本的MTU最大值设置成了1700，然后发送了一个超大的ip数据包（2000），这时候在以外网传输的时候会被拆成2个包，一个1700，一个300，然后加上头信息进行传输。

```
1700     1500                1500
笔记本 -> 路由器 -> 电信机房 -> 服务器
```

路由器接收到了一个1700的帧，发现大于自己设置的最大值：1500，如果IP包DF标志位为1，也就是不允许分包，那么路由器直接就把这个包丢弃了，根本就不会到达电信机房，也就到不了服务器了，所以，到这里我们就会发现，MTU其实就是在每一个节点的管控值，只要是大于这个值的数据帧，要么选择分片，要么直接丢弃。

## 为什么是1500？

其实一个标准的以太网数据帧大小是：`1518`，头信息有14字节，尾部校验和FCS占了4字节，所以真正留给上层协议传输数据的大小就是：1518 - 14 - 4 = 1500，那么，1518这个值又是从哪里来的呢？

## 假设取一个更大的值

假设MTU值和IP数据包大小一致，一个IP数据包的大小是：65535，那么加上以太网帧头和为，一个以太网帧的大小就是：`65535 + 14 + 4 = 65553`，看起来似乎很完美，发送方也不需要拆包，接收方也不需要重组。

那么假设我们现在的带宽是：`100Mbps`，因为以太网帧是传输中的最小可识别单元，再往下就是0101所对应的光信号了，所以我们的一条带宽同时只能发送一个以太网帧。如果同时发送多个，那么对端就无法重组成一个以太网帧了，在`100Mbps`的带宽中（假设中间没有损耗），我们计算一下发送这一帧需要的时间：

```
( 65553 * 8 ) / ( 100 * 1024 * 1024 ) ≈ 0.005(s)
```

在100M网络下传输一帧就需要5ms，也就是说这5ms其他进程发送不了任何数据。如果是早先的电话拨号，网速只有2M的情况下：

```
( 65553 * 8 ) / ( 2 * 1024 * 1024 ) ≈ 0.100(s)
```

100ms，这简直是噩梦。其实这就像红绿灯，时间要设置合理，交替通行，不然同一个方向如果一直是绿灯，那么另一个方向就要堵成翔了。

## 既然大了不行，那设置小一点可以么？

假设MTU值设置为100，那么单个帧传输的时间，在2Mbps带宽下需要：

```
( 100 * 8 ) / ( 2 * 1024 * 1024 ) * 1000 ≈ 5(ms)
```

时间上已经能接受了，问题在于，不管MTU设置为多少，以太网头帧尾大小是固定的，都是14 + 4，所以在MTU为100的时候，一个以太网帧的传输效率为：

```
( 100 - 14 - 4 ) / 100 = 82%
```

写成公式就是：`( T - 14 - 4 ) / T`，当T趋于无穷大的时候，效率接近`100%`，也就是MTU的值越大，传输效率最高，但是基于上一点传输时间的问题，来个折中的选择吧，既然头加尾是18，那就凑个整来个1500，总大小就是1518，传输效率：

```
1500 / 1518 =  98.8%
```

100Mbps传输时间：

```
( 1518 * 8 ) / ( 100 * 1024 * 1024 ) * 1000 = 0.11(ms)
```

2Mbps传输时间：

```
( 1518 * 8 ) / ( 2 * 1024 * 1024 ) * 1000 = 5.79(ms)
```

总体上时间都还能接受

### 最小值被限制在64

为什么是64呢？

这个其实和以太网帧在半双工下的碰撞有关，感兴趣的同学可以自行去搜索。

## 在我玩游戏的时候，为什么把MTU改成1480就不卡了？

路由器默认值大多都是1500，理论上是没有问题的，那为什么我玩游戏的时候改成1480才能流畅呢？原因在于当时我使用的是ADSL上网的方式，ADSL使用的PPPoE协议。

### PPPoE

PPPoE协议介于以太网和IP之间，协议分为两部分，PPP( Point to Point Protocol )和oE( over Ethernet )，也就是以太网上的PPP协议，而PPPoE协议头信息为:

```
| VER(4bit) | TYPE(4bit) | CODE(8bit) | SESSION-ID(16bit) | LENGTH(16bit) |
```

这里总共是48位，也就是6个字节，那么另外2个字节是什么呢？答案是PPP协议的ID号，占用两个字节，所以在PPPoE环境下，最佳MTU值应该是：1500 - 4 - 2 = 1492。

### 我的上网方式

当时我的上网路径如下：

```
PC -> 路由器 -> 电信
```

我在路由器进行拨号，然后PC连接路由器进行上网。

### 最根本原因

问题就出在路由器拨号，如果是PC拨号，那么PC会进行PPPoE的封装，会按照MTU:1492来进行以太网帧的封装，即使通过路由器，路由器这时候也只是转发而已，不会进行拆包。

而当用路由器拨号时，PC并不知道路由器的通信方式，会以网卡的设置，默认1500的MTU来进行以太网帧的封装，到达路由器时，由于路由器需要进行PPPoE协议的封装，加上8字节的头信息，这样一来，就必须进行拆包，路由器把这一帧的内容拆成两帧发送，一帧是1492，一帧是8，然后分别加上PPPoE的头进行发送。

平时玩游戏不卡，是因为数据量路由器还处理得过来，而当进行群怪AOE的时候，由于短时间数据量过大，路由器处理不过来，就会发生丢包卡顿的情况，也就掉线了。

帖子里面提到的1480，猜测可能是尽量设小一点，避免二次拨号带来的又一次PPPoE的封装，因为时间久远，没办法回到当时的场景再去抓包了。

## 结论

1518这个值是考虑到传输效率以及传输时间而折中选择的一个值，并且由于目前网络链路中的节点太多，其中某个节点的MTU值如果和别的节点不一样，就很容易带来拆包重组的问题，甚至会导致无法发送。