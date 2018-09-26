---
layout:     post
title:     Linux: IO Scheduler（转）
subtitle:   Linux IO Scheduler
date:       2018-09-25
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - linux
    - Scheduler
    - IO
typora-copy-images-to: ../img
typora-root-url: ..
---



# [Linux IO Scheduler](https://www.cnblogs.com/cobbliu/p/5389556.html)

[原文在此](https://www.cnblogs.com/cobbliu/p/5389556.html)

每个块设备或者块设备的分区，都对应有自身的请求队列(request_queue),而每个请求队列都可以选择一个I/O调度器来协调所递交的request。I/O调度器的基本目的是将请求按照它们对应在块设备上的扇区号进行排列，以减少磁头的移动，提高效率。每个设备的请求队列里的请求将按顺序被响应。实际上，除了这个队列，每个调度器自身都维护有不同数量的队列，用来对递交上来的request进行处理，而排在队列最前面的request将适时被移动到请求队列中等待响应。

​     IO调度器在内核栈中所处位置如下：

![img](/img/384029-20160413234742113-712280053.png)



​      内核中实现的IO调度器主要有四种--Noop,Deadline,CFG, Anticipatory。

### 1，Noop算法

[Noop调度算法](https://en.wikipedia.org/wiki/Noop_scheduler)是内核中最简单的IO调度算法。Noop调度算法也叫作电梯调度算法，它将IO请求放入到一个FIFO队列中，然后逐个执行这些IO请求，当然对于一些在磁盘上连续的IO请求，Noop算法会适当做一些合并。这个调度算法特别适合那些不希望调度器重新组织IO请求顺序的应用。

这种调度算法在以下场景中优势比较明显：

1）在IO调度器下方有更加智能的IO调度设备。如果您的Block Device Drivers是Raid，或者SAN，NAS等存储设备，这些设备会更好地组织IO请求，不用IO调度器去做额外的调度工作；

2）上层的应用程序比IO调度器更懂底层设备。或者说上层应用程序到达IO调度器的IO请求已经是它经过精心优化的，那么IO调度器就不需要画蛇添足，只需要按序执行上层传达下来的IO请求即可。

3）对于一些非旋转磁头氏的存储设备，使用Noop的效果更好。因为对于旋转磁头式的磁盘来说，IO调度器的请求重组要花费一定的CPU时间，但是对于SSD磁盘来说，这些重组IO请求的CPU时间可以节省下来，因为SSD提供了更智能的请求调度算法，不需要内核去画蛇添足。[这篇文章](http://www.nuodb.com/techblog/tuning-linux-io-scheduler-ssds)提及了SSD中使用Noop效果会更好。

### 2，Deadline算法

Deadline算法的核心在于保证每个IO请求在一定的时间内一定要被服务到，以此来避免某个请求饥饿。

Deadline算法中引入了四个队列，这四个队列可以分为两类，每一类都由读和写两类队列组成，一类队列用来对请求按起始扇区序号进行排序，通过红黑树来组织，称为sort_list；另一类对请求按它们的生成时间进行排序，由链表来组织，称为fifo_list。每当确定了一个传输方向(读或写)，那么将会从相应的sort_list中将一批连续请求dispatch到requst_queue的请求队列里，具体的数目由fifo_batch来确定。只有下面三种情况才会导致一次批量传输的结束：

1）对应的sort_list中已经没有请求了

2）下一个请求的扇区不满足递增的要求

3）上一个请求已经是批量传输的最后一个请求了。


所有的请求在生成时都会被赋上一个期限值(根据jiffies)，并按期限值排序在fifo_list中，读请求的期限时长默认为为500ms，写请求的期限时长默认为5s，可以看出内核对读请求是十分偏心的，其实不仅如此，在deadline调度器中，还定义了一个starved和writes_starved，writes_starved默认为2，可以理解为写请求的饥饿线，内核总是优先处理读请求，starved表明当前处理的读请求批数，只有starved超过了writes_starved后，才会去考虑写请求。因此，假如一个写请求的期限已经超过，该请求也不一定会被立刻响应，因为读请求的batch还没处理完，即使处理完，也必须等到starved超过writes_starved才有机会被响应。为什么内核会偏袒读请求？这是从整体性能上进行考虑的。读请求和应用程序的关系是同步的，因为应用程序要等待读取的内容完毕，才能进行下一步工作，因此读请求会阻塞进程，而写请求则不一样，应用程序发出写请求后，内存的内容何时写入块设备对程序的影响并不大，所以调度器会优先处理读请求。

默认情况下，读请求的超时时间是500ms，写请求的超时时间是5s。

[这篇文章](http://www.ibm.com/support/knowledgecenter/api/content/linuxonibm/liaat/liaatbestpractices_pdf.pdf)说在一些多线程应用下，Deadline算法比CFQ算法好。[这篇文章](https://www.percona.com/blog/2009/01/30/linux-schedulers-in-tpcc-like-benchmark/)说在一些数据库应用下，Deadline算法比CFQ算法好。

### 3，Anticipatory算法

Anticipatory算法的核心是局部性原理，它期望一个进程昨晚一次IO请求后还会继续在此处做IO请求。在IO操作中，有一种现象叫“假空闲”（Deceptive idleness），它的意思是一个进程在刚刚做完一波读操作后，看似是空闲了，不读了，但是实际上它是在处理这些数据，处理完这些数据之后，它还会接着读，这个时候如果IO调度器去处理另外一个进程的请求，那么当原来的假空闲进程的下一个请求来的时候，磁头又得seek到刚才的位置，这样大大增加了寻道时间和磁头旋转时间。所以，Anticipatory算法会在一个读请求做完后，再等待一定时间t（通常是6ms），如果6ms内，这个进程上还有读请求过来，那么我继续服务，否则，处理下一个进程的读写请求。
​   

在一些场景下，Antocipatory算法会有非常有效的性能提升。[这篇文章](http://portal.acm.org/citation.cfm?id=502046&dl=GUIDE&coll=GUIDE&CFID=87027259&CFTOKEN=77244280)有说，[这篇文章](http://kerneltrap.org/node/592)也有一份评测。
值得一提的是，Anticipatory算法从Linux 2.6.33版本后，就被移除了，因为CFQ通过配置也能达到Anticipatory算法的效果。

### 4，CFQ算法

CFQ（**Completely Fair Queuing**）算法，顾名思义，绝对公平算法。它试图为竞争块设备使用权的所有进程分配一个请求队列和一个时间片，在调度器分配给进程的时间片内，进程可以将其读写请求发送给底层块设备，当进程的时间片消耗完，进程的请求队列将被挂起，等待调度。 每个进程的时间片和每个进程的队列长度取决于进程的IO优先级，每个进程都会有一个IO优先级，CFQ调度器将会将其作为考虑的因素之一，来确定该进程的请求队列何时可以获取块设备的使用权。IO优先级从高到低可以分为三大类:RT(real time),BE(best try),IDLE(idle),其中RT和BE又可以再划分为8个子优先级。实际上，我们已经知道CFQ调度器的公平是针对于进程而言的，而只有同步请求(read或syn write)才是针对进程而存在的，他们会放入进程自身的请求队列，而所有同优先级的异步请求，无论来自于哪个进程，都会被放入公共的队列，异步请求的队列总共有8(RT)+8(BE)+1(IDLE)=17个。


从Linux 2.6.18起，CFQ作为默认的IO调度算法。
对于通用的服务器来说，CFQ是较好的选择。


对于使用哪种调度算法来说，还是要根据具体的业务场景去做足benchmark来选择，不能仅靠别人的文字来决定。

### 5，更改IO调度算法

在RHEL5/OEL5以及之后的版本中（比如RHEL6和RHEL7），可以针对每块磁盘制定I/O Scheduler，修改完毕立刻生效，比如：

```
$ cat /sys/block/sda1/queue/scheduler
[noop] anticipatory deadline cfq

#修改为cfq
$ echo 'cfq'>/sys/block/sda1/queue/scheduler

#立刻生效
$ cat /sys/block/sda1/queue/scheduler
noop anticipatory deadline [cfq]
```

 

6，一些磁盘相关的内核参数

/sys/block/sda/queue/nr_requests 磁盘队列长度。默认只有 128 个队列,可以提高到 512 个.会更加占用内存,但能更加多的合并读写操作,速度变慢,但能读写更加多的量

/sys/block/sda/queue/iosched/antic_expire 等待时间 。读取附近产生的新请时等待多长时间


/sys/block/sda/queue/read_ahead_kb

这个参数对顺序读非常有用,意思是,一次提前读多少内容,无论实际需要多少.默认一次读 128kb 远小于要读的,设置大些对读大文件非常有用,可以有效的减少读 seek 的次数,这个参数可以使用 blockdev –setra 来设置,setra 设置的是多少个扇区,所以实际的字节是除以2,比如设置 512 ,实际是读 256 个字节.


/proc/sys/vm/dirty_ratio

这个参数控制文件系统的文件系统写缓冲区的大小,单位是百分比,表示系统内存的百分比,表示当写缓冲使用到系统内存多少的时候,开始向磁盘写出数 据.增大之会使用更多系统内存用于磁盘写缓冲,也可以极大提高系统的写性能.但是,当你需要持续、恒定的写入场合时,应该降低其数值,一般启动上缺省是 10.下面是增大的方法： echo ’40’> 


/proc/sys/vm/dirty_background_ratio

这个参数控制文件系统的pdflush进程,在何时刷新磁盘.单位是百分比,表示系统内存的百分比,意思是当写缓冲使用到系统内存多少的时候, pdflush开始向磁盘写出数据.增大之会使用更多系统内存用于磁盘写缓冲,也可以极大提高系统的写性能.但是,当你需要持续、恒定的写入场合时,应该降低其数值,一般启动上缺省是 5.下面是增大的方法： echo ’20’ >

 

 /proc/sys/vm/dirty_writeback_centisecs

这个参数控制内核的脏数据刷新进程pdflush的运行间隔.单位是 1/100 秒.缺省数值是500,也就是 5 秒.如果你的系统是持续地写入动作,那么实际上还是降低这个数值比较好,这样可以把尖峰的写操作削平成多次写操作.设置方法如下： echo ‘200’ > /proc/sys/vm/dirty_writeback_centisecs 如果你的系统是短期地尖峰式的写操作,并且写入数据不大（几十M/次）且内存有比较多富裕,那么应该增大此数值： echo ‘1000’ > /proc/sys/vm/dirty_writeback_centisecs



/proc/sys/vm/dirty_expire_centisecs

这个参数声明Linux内核写缓冲区里面的数据多“旧”了之后,pdflush进程就开始考虑写到磁盘中去.单位是 1/100秒.缺省是 30000,也就是 30 秒的数据就算旧了,将会刷新磁盘.对于特别重载的写操作来说,这个值适当缩小也是好的,但也不能缩小太多,因为缩小太多也会导致IO提高太快.建议设置为 1500,也就是15秒算旧. echo ‘1500’ > /proc/sys/vm/dirty_expire_centisecs 当然,如果你的系统内存比较大,并且写入模式是间歇式的,并且每次写入的数据不大（比如几十M）,那么这个值还是大些的好.

 

参考文献

1，https://en.wikipedia.org/wiki/Noop_scheduler

2，https://en.wikipedia.org/wiki/Deadline_scheduler

3，https://en.wikipedia.org/wiki/Anticipatory_scheduling

4，https://en.wikipedia.org/wiki/CFQ

5，http://www.redhat.com/magazine/008jun05/features/schedulers/ 这篇文章介绍了四种IO调度算法并且针对他们的应用场景做了一个评测

6，<http://www.dbform.com/html/2011/1510.html>

7，https://support.rackspace.com/how-to/configure-flash-drives-in-high-io-instances-as-data-drives/ 这篇文章介绍了一些SSD中IO scheduler的配置

8，https://www.percona.com/blog/2009/01/30/linux-schedulers-in-tpcc-like-benchmark/

9，http://www.ibm.com/support/knowledgecenter/api/content/linuxonibm/liaat/liaatbestpractices_pdf.pdf

10，http://dl.acm.org/citation.cfm?id=502046&dl=GUIDE&coll=GUIDE

11，http://www.nuodb.com/techblog/tuning-linux-io-scheduler-ssds

 


