---
layout:     post
title:     Hbase HFile
subtitle:   Apache HBase I/O – HFile
date:       2019-04-02
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    -  bully
        -  election
typora-copy-images-to: ..\img
typora-root-url: ..
---


# Bully algorithm

In [distributed computing](https://en.wikipedia.org/wiki/Distributed_computing), the **bully algorithm** is a method for dynamically electing a [coordinator](https://en.wikipedia.org/wiki/Distributed_computing#Coordinator_election) or leader from a group of distributed computer processes. The process with the highest process ID number from amongst the non-failed processes is selected as the coordinator.

## Assumptions[[edit](https://en.wikipedia.org/w/index.php?title=Bully_algorithm&action=edit&section=1)]

The algorithm assumes that:[[1\]](https://en.wikipedia.org/wiki/Bully_algorithm#cite_note-1)

- the system is synchronous.
- processes may fail at any time, including during execution of the algorithm.
- a process fails by stopping and returns from failure by restarting.
- there is a failure detector which detects failed processes.
- message delivery between processes is reliable.
- each process knows its own process id and address, and that of every other process.

## Algorithm[[edit](https://en.wikipedia.org/w/index.php?title=Bully_algorithm&action=edit&section=2)]

The algorithm uses the following message types:

- Election Message: Sent to announce election.
- Answer (Alive) Message: Responds to the Election message.
- Coordinator (Victory) Message: Sent by winner of the election to announce victory.

When a process P recovers from failure, or the failure detector indicates that the current coordinator has failed, P performs the following actions:

1. If P has the highest process id, it sends a Victory message to all other processes and becomes the new Coordinator. Otherwise, P broadcasts an Election message to all other processes with higher process IDs than itself.
2. If P receives no Answer after sending an Election message, then it broadcasts a Victory message to all other processes and becomes the Coordinator.
3. If P receives an Answer from a process with a higher ID, it sends no further messages for this election and waits for a Victory message. (If there is no Victory message after a period of time, it restarts the process at the beginning.)
4. If P receives an Election message from another process with a lower ID it sends an Answer message back and starts the election process at the beginning, by sending an Election message to higher-numbered processes.
5. If P receives a Coordinator message, it treats the sender as the coordinator.

### Analysis[[edit](https://en.wikipedia.org/w/index.php?title=Bully_algorithm&action=edit&section=3)]

#### Safety[[edit](https://en.wikipedia.org/w/index.php?title=Bully_algorithm&action=edit&section=4)]

The safety property expected of leader election protocols is that every non-faulty process either elects a process Q, or elects none at all. Note that all processes that elect a leader must decide on the same process Q as the leader. The Bully algorithm satisfies this property (under the system model specified), and at no point in time is it possible for two processes in the group to have a conflicting view of who the leader is, except during an election. This is true because if it weren't, there are two processes X and Y such that both sent the Coordinator (victory) message to the group. This means X and Y must also have sent each other victory messages. But this cannot happen, since before sending the victory message, Election messages would have been exchanged between the two, and the process with a lower process id among the two would never send out victory messages. We have a contradiction, and hence our initial assumption that there are two leaders in the system at any given time is false, and that shows that the bully algorithm is safe.

#### Liveness[[edit](https://en.wikipedia.org/w/index.php?title=Bully_algorithm&action=edit&section=5)]

Liveness is also guaranteed in the synchronous, crash-recovery model. Consider the would-be leader failing after sending an Answer (Alive) message but before sending a Coordinator (victory) message. If it does not recover before the set timeout on lower id processes, one of them will become leader eventually (even if some of the other processes crash). If the failed process recovers in time, it simply sends a Coordinator (victory) message to all of the group.

#### Network bandwidth utilization[[edit](https://en.wikipedia.org/w/index.php?title=Bully_algorithm&action=edit&section=6)]

Assuming that the bully algorithm messages are of a fixed (known, invariant) sizes, the most number of messages are exchanged in the group when the process with the lowest id initiates an election. This process sends (N-1) Election messages, the next higher id sends (N-2) messages, and so on, resulting in {\displaystyle \Theta \left(N^{2}\right)}![{\displaystyle \Theta \left(N^{2}\right)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2b80aaaf1ee027d094109717c77f7ab1e8882373) election messages. There are also the {\displaystyle \Theta \left(N^{2}\right)}![{\displaystyle \Theta \left(N^{2}\right)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2b80aaaf1ee027d094109717c77f7ab1e8882373) Alive messages, and {\displaystyle \Theta \left(N\right)}![{\displaystyle \Theta \left(N\right)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/edaa7032a213984dc16f5ea2275a928492f771ad) co-ordinator messages, thus making the overall number messages exchanged in the worst case be {\displaystyle \Theta \left(N^{2}\right)}![{\displaystyle \Theta \left(N^{2}\right)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2b80aaaf1ee027d094109717c77f7ab1e8882373).

## See also[[edit](https://en.wikipedia.org/w/index.php?title=Bully_algorithm&action=edit&section=7)]

- [Leader election](https://en.wikipedia.org/wiki/Leader_election)
- [Chang and Roberts algorithm](https://en.wikipedia.org/wiki/Chang_and_Roberts_algorithm)



Garcia-Monila 在 1982 年的一篇论文中发明了所谓的霸道选举算法（Bully Algorithm）。其基本思想是：当一个进程P发现协调者不再响应请求时，就判定协调者出现故障，于是它就发起选举，选出新的协调者，即当前活动进程中进程号最大者

## 霸道选举算法的假设

1. 系统是同步的
2. 进程在任何时候都可能失败，包括算法在执行的过程中
3. 进程失败后停止工作，重启后重新工作
4. 有失败监控者，它可以发现失败的进程
5. 进程之间消息传递是可靠地
6. 每一个进程知道自己和其他每一个进程的id以及地址

## 霸道算法的选举流程

编辑

选举过程中会发送以下三种消息类型：

1. Election消息：表示发起一次选举
2. Answer(Alive)消息：对发起选举消息的应答
3. Coordinator(Victory)消息：选举胜利者向参与者发送选举成功消息

触发选举流程的事件包括：

1. 当进程P从错误中恢复
2. 检测到Leader失败

选举流程：

1. 如果P是最大的ID，直接向所有人发送Victory消息，成功新的Leader；否则向所有比他大的ID的进程发送Election消息
2. 如果P再发送Election消息后没有收到Alive消息，则P向所有人发送Victory消息，成功新的Leader
3. 如果P收到了从比自己ID还要大的进程发来的Alive消息，P停止发送任何消息，等待Victory消息（如果过了一段时间没有等到Victory消息，重新开始选举流程）
4. 如果P收到了比自己ID小的进程发来的Election消息，回复一个Alive消息，然后重新开始选举流程
5. 如果P收到Victory消息，把发送者当做Leader



## 示例

编辑

以8个进程为例，由于进程7的崩溃，进程3第1个注意到这一点，因此，由进程3发起新的选举。

- 进程3向比它大的进程4发送选举消息，如图(a)。
- 进程4收到这一消息，向进程3发送接管消息OK，如图(b)。
- 进程4向比它大的进程5发送选举消息。
- 进程5收到这一消息，向进程4发送接管消息OK。
- 
- 进程5向比它大的进程6发送选举消息。
- 进程6收到这一消息，向进程5发送接管消息OK。
- 进程6向比它大的进程7发送选举消息，发现进程7故障，如图(c)。
- 进程6最终取得了协调权，向所有进程发送协调者消息，开始协调工作，如图(d)。



![bully-algo-1](/img/bully-algo-1.jpg)