---
layout:     post
title:     Avoiding Full GCs in Apache HBase with MemStore-Local Allocation Buffers
subtitle:   Avoiding Full GCs in Apache HBase with MemStore-Local Allocation Buffers
date:       2011-02-24
author:     Cloudra
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - hbase
    - Full GC
    - MemStore
    - LAB

typora-copy-images-to: ..\img
typora-root-url: ..
---



# Avoiding Full GCs in Apache HBase with MemStore-Local Allocation Buffers: Part 1



http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-1/

http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-2/

http://blog.cloudera.com/blog/2011/03/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-3/



[February 24, 2011](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-1/)[By Todd Lipcon](http://blog.cloudera.com/blog/author/todd/) [(@tlipcon)](https://twitter.com/@tlipcon)[10 Comments](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-1/#comments)

Categories: [General](http://blog.cloudera.com/blog/category/general/) [HBase](http://blog.cloudera.com/blog/category/hbase/)

Today, rather than discussing new projects or use cases built on top of CDH, I’d like to switch gears a bit and share some details about the engineering that goes into our products. In this post, I’ll explain the *MemStore-Local Allocation Buffer*, a new component in the guts of Apache HBase which dramatically reduces the frequency of long garbage collection pauses. While you won’t need to understand these details to use Apache HBase, I hope it will provide an interesting view into the kind of work that engineers at Cloudera do.

This post will be the first in a three part series on this project.

## Background

##### Heaps and heaps of RAM!

Over the last few years, the amount of memory available on inexpensive commodity servers has gone up and up. When the Apache HBase project started in 2007, typical machines running Hadoop had 4-8GB of RAM. Today, most Cloudera customers run with at least 24G of RAM, and larger amounts like 48G or even 72G are becoming increasingly common as costs continue to come down. On the surface, all this new memory capacity seems like a great win for latency-sensitive database software like HBase — with a lot of RAM, more data can fit in cache, avoiding expensive disk seeks on reads, and more data can fit in the *memstore*, the memory area that buffers writes before they flush to disk.

In practice, however, as typical heap sizes for HBase have crept up and up, the garbage collection algorithms available in production-quality JDKs have remained largely the same. This has led to one major problem for many users of HBase: lengthy stop-the-world garbage collection pauses which get longer and longer as heap sizes continue to grow. What does this mean in practice?

- During a stop-the-world pause, any client requests to HBase are stalled, causing user-visible latency or even timeouts. If a request takes over a minute to respond because of a pause, HBase may as well be down – there’s often little value in such a delayed response.
- HBase relies on Apache ZooKeeper to track cluster membership and liveness. If a server pauses for a significant amount of time, it will be unable to send heartbeat ping messages to the ZooKeeper quorum, and the rest of the servers will presume that the server has died. This causes the master to initiate certain recovery processes to account for the presumed-dead server. When the server comes out of its pause, it will find all of its leases revoked, and commit suicide. The HBase development team has affectionately dubbed this scenario a *Juliet Pause* — the master (Romeo) presumes the region server (Juliet) is dead when it’s really just sleeping, and thus takes some drastic action (recovery). When the server wakes up, it sees that a great mistake has been made and takes its own life. Makes for a good play, but a pretty awful failure scenario!

The above issues will be familiar to most who have done serious load testing of an HBase cluster. On typical hardware, it can pause 8-10 seconds per GB of heap — a 8G heap may pause for upwards of a minute. No matter how much tuning one might do, it turns out this problem is completely unavoidable in HBase 0.90.0 or older with today’s production-ready garbage collectors. Since this is such a common issue, and only getting worse, it became a priority for Cloudera at the beginning of the year. In the rest of this post, I’ll describe a solution we developed that largely eliminates the problem.

## Java GC Background

In order to understand the GC pause issue thoroughly, it’s important to have some background in Java’s garbage collection techniques. Some simplifications will be made, so I highly encourage you to do further research for all the details.

If you’re already an expert in GC, feel free to skip this section.

##### Generational GC

Java’s garbage collector typically operates in a *generational* mode, relying on an assumption called the *generational hypothesis*: we assume that most objects either die young, or stick around for quite a long time. For example, the buffers used in processing an RPC request will only last for some milliseconds, whereas the data in a cache or the data in the HBase MemStore will likely survive for many minutes.

Given that objects have two different lifetime profiles, it’s intuitive that different garbage collection algorithms might do a better job on one profile than another. So, we split up the heap into two generations: the *young*(a.k.a *new*) generation and the *old* (a.k.a *tenured*). When objects are allocated, they start in the young generation, where we prefer an algorithm that operates efficiently when most of the data is short-lived. If an object survives several collections inside the young generation, we *tenure* it by relocating it into the old generation, where we assume that data is likely to die out much more slowly.

In most latency-sensitive workloads like HBase, we recommend the `-XX:+UseParNewGC` and `-XX:+UseConcMarkSweepGC` JVM flags. This enables the *Parallel New* collector for the young generation and the *Concurrent Mark-Sweep* collector for the old generation.

##### Young Generation – Parallel New Collector

The Parallel New collector is a *stop-the-world copying collector*. Whenever it runs, it first stops the world, suspending all Java threads. Then, it traces object references to determine which objects are *live* (still referenced by the program). Lastly, it moves the live objects over to a free section of the heap and updates any pointers into those objects to point to the new addresses. There are a few important points here about this collector:

- It stops the world, but not for very long. Because the young generation is usually fairly small, and this collector runs with many threads, it can accomplish its work very quickly. For production workloads we usually recommend a young generation no larger than 512MB, which results in pauses of less than a few hundred milliseconds at the worst case.
- It copies the live objects into a free heap area. This has the side effect of *compacting* the free space – after every collection, the free space in the young generation is one contiguous chunk, which means that allocation can be very efficient.

Each time the Parallel New collector copies an object, it increments a counter for that object. After an object has been copied around in the young generation several times, the algorithm decides that it must belong to the long-lived class of objects, and moves it to the old generation (*tenures* it*)*. The number of times an object is copied inside the young generation before being tenured is called the *tenuring threshold.*

##### Old Generation – Concurrent Mark-Sweep

Every time the parallel new collector runs, it will tenure some objects into the old generation. So, of course, the old generation will eventually fill up, and we need a strategy for collecting it as well. The Concurrent-Mark-Sweep collector (CMS) is responsible for clearing dead objects in this generation.

The CMS collector operates in a series of phases. Some phases stop the world, and others run concurrently with the Java application. The major phases are:

1. **initial-mark** (stops the world). In this phase, the CMS collector places a *mark* on the *root* objects. A *root*object is something directly referenced from a live Thread – for example, the local variables in use by that thread. This phase is short because the number of roots is very small.
2. **concurrent-mark** (concurrent). The collector now follows every pointer starting from the root objects until it has marked all live objects in the system.
3. **remark** (stops the world). Since objects might have had references changed, and new objects might have been created during concurrent-mark, we need to go back and take those into account in this phase. This is short because a special data structure allows us to only inspect those objects that were modified during the prior phase.
4. **concurrent-sweep** (concurrent). Now, we proceed through all objects in the heap. Any object without a mark is collected and considered free space. New objects allocated during this time are marked as they are created so that they aren’t accidentally collected.

The important things to note here are:

- The stop-the-world phases are made to be very short. The long work of scanning the whole heap and sweeping up the dead objects happens concurrently.
- This collector does *not* relocate the live objects, so free space can be spread in different chunks throughout the heap. We’ll come back to this later!

## CMS Failure Modes

As I described it, the CMS collector sounds pretty great – it only pauses for very short times and most of the heavy lifting is done concurrently. So how is it that we see multi-minute pauses when we run HBase under heavy load with large heaps? It turns out that the CMS collector has two failure modes.

##### Concurrent Mode Failure

The first failure mode, and the one more often discussed, is simple *concurrent mode failure*. This is best described with an example: suppose that there is an 8GB heap. When the heap is 7GB full, the CMS collector may begin its first phase. It’s happily chugging along with the concurrent-mark phase. Meanwhile, more data is being allocated and tenured into the old generation. If the tenuring rate is too fast, the generation may completely fill up before the collector is done marking. At that point, the program may not proceed because there is no free space to tenure more objects! The collector must abort its concurrent work and fall back to a stop-the-world single-threaded copying collection algorithm. This algorithm relocates all live objects to the beginning of the heap, and frees up all of the dead space. After the long pause, the program may proceed.

It turns out this is fairly easy to avoid with tuning: we simply need to encourage the collector to start its work earlier! Thus, it’s less likely that it will get overrun with new allocations before it’s done with its collection. This is tuned by setting `-XX:CMSInitiatingOccupancyFraction=N` where `N` is the percent of heap at which to start the collection process. The HBase region server carefully accounts its memory usage to stay within 60% of the heap, so we usually set this value to around 70.

##### Promotion Failure due to Fragmentation

This failure mode is a little bit more complicated. Recall that the CMS collector does not relocate objects, but simply tracks all of the separate areas of free space in the heap. As a thought experiment, imagine that I allocate 1 million objects, each 1KB, for a total usage of 1GB in a heap that is exactly 1GB. Then I free every odd-numbered object, so I have 500MB live. However, the free space will be solely made up of 1KB chunks. If I need to allocate a 2KB object, there is nowhere to put it, even though I ostensibly have 500MB of space free. This is termed *memory fragmentation*. No matter how early I ask the CMS collector to start, since it does not relocate objects, it cannot solve this problem!

When this problem occurs, the collector again falls back to the copying collector, which is able to compact all the objects and free up space.

## Enough GC! Back to HBase!

Let’s come back up for air and use what we learned about Java GC to think about HBase. We can make two observations about the pauses we see in HBase:

1. By setting the `CMSInitiatingOccupancyFraction` tunable lower, we’ve seen that some users can avoid the GC issue. But for other workloads, it will always happen, no matter how low we set this tuning parameter.
2. We often see these pauses even when metrics and logs indicate that the heap has several GB of free space!

Given these observations, we hypothesize that our problem must be caused by fragmentation, rather than some kind of memory leak or improper tuning.

## An experiment: measuring fragmentation

To confirm this hypothesis, we’ll run an experiment. The first step is to collect some measurements about heap fragmentation. After spelunking in the OpenJDK source code, I discovered the little-known parameter `-XX:PrintFLSStatistics=1` which, when combined with other verbose GC logging options, causes the CMS collector to print statistical information about its free space before and after every collection. In particular, the metrics we care about are:

- **Free space** – the total amount of free memory in the old generation
- **Num chunks** – the total number of non-contiguous free chunks of memory
- **Max chunk size** – the size of the largest one of these chunks (i.e the biggest single allocation we can satisfy without a pause)

I enabled this option, started up a cluster, and then ran three separate stress workloads against it using Yahoo Cloud Serving Benchmark (YCSB):

1. **Write-only**: writes rows with 10 columns, each 100 bytes, across 100M distinct row keys.
2. **Read-only with cache churn**: reads data randomly for 100M distinct row keys, so that the data does not fit in the LRU cache.
3. **Read-only without cache churn**: reads data randomly for 10K distinct row keys, so that the data fits entirely in the LRU cache.

Each workload will run at least an hour, so we can collect some good data about the GC behavior under that workload. The goal of this experiment is first to verify our hypothesis that the pauses are caused by fragmentation, and second to determine whether these issues were primarily caused by the read path (including the LRU cache) or the write path (including the MemStores for each region).

## To be continued…

The next post in the series will show the results of this experiment and dig into HBase’s internals to understand how the different workloads affect memory layout.

Meanwhile, if you want to learn more about Java’s garbage collectors, I recommend the following links:

- Jon “the collector” Masamitsu has a good post describing the [various collectors in Java 6](http://blogs.sun.com/jonthecollector/entry/our_collectors).
- To learn more about CMS, you can read the original paper: [A Generational Mostly-concurrent Garbage Collector](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.22.8915) [Printezis/Detlefs, ISMM2000]





# Avoiding Full GCs in HBase with MemStore-Local Allocation Buffers: Part 2

[February 28, 2011](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-2/)[By Todd Lipcon](http://blog.cloudera.com/blog/author/todd/) [(@tlipcon)](https://twitter.com/@tlipcon)[21 Comments](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-2/#comments)

Categories: [HBase](http://blog.cloudera.com/blog/category/hbase/)

This is the second post in a series detailing a recent improvement in Apache HBase that helps to reduce the frequency of garbage collection pauses. Be sure you’ve read [part 1](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-1/) before continuing on to this post.

## Recap from Part 1

In [last week’s post](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-1/), we noted that HBase has had problems coping with long garbage collection pauses, and we summarized the different garbage collection algorithms commonly used for HBase on the Sun/Oracle Java 6 JVM. Then, we hypothesized that the long garbage collection pauses are due to memory fragmentation, and devised an experiment to both confirm this hypothesis and investigate which workloads are most prone to this problem.

## Experimental Results

##### Overview

As described in the previous post, I ran three different workload types against an HBase region server while collecting verbose GC logs with `-XX:PrintFLSStatistics=1`. I then wrote a [short python script](https://issues.apache.org/jira/secure/attachment/12468869/parse-fls-statistics.py) to parse the results and reformat into a TSV file, and graphed the resulting metrics using my favorite R graphing library, [ggplot2](http://had.co.nz/ggplot2/):

[![HBase fragmentation experiment](/img/overview.png)](https://www.cloudera.com/wp-content/uploads/2011/02/overview.png)

The top part of the graph shows `free_space`, the total amount of free space in the heap. The bottom graph shows `max_chunk`, the size of the largest chunk of contiguous free space. The X axis is time in seconds, and the Y axis has units of heap words. In this case a word is 8 bytes, since I am running a 64-bit JVM.

It was immediately obvious from this overview graph that the three different workloads have very different memory characteristics. We’ll zoom in on each in turn.

##### Write-only Workload

[![Write-only workload](/img/insert-workload.png)](https://www.cloudera.com/wp-content/uploads/2011/02/insert-workload.png)

Zoomed in on the write-only workload, we can see two interesting patterns:

1. The `free_space` graph shows a fluctuation between about 350 megawords (2.8GB) and 475 megawords (3.8GB). Each time the free space hits 2.8G, the CMS collector kicks in and frees up about 1GB of space. This shows that the CMS initiating occupancy fraction has been tuned to a low enough value – there is always a significant amount of free space in the heap. We can also see that there are no memory leaks – the heap usage keeps a fairly consistent profile over time and doesn’t trend in any direction.
2. Although the CMS collector is kicking in to free up heap, the `max_chunk` graph is seen to drop precipitously nearly down to 0. Each time it reaches 0 (eg at around t=102800) we see a sharp spike back up to a large value.

By correlating this graph with the GC logs, I noted that the long full GCs corresponded exactly to the vertical spikes in the `max_chunk` graph — after each of these full GCs, the heap had been defragmented, so all of the free space was in one large chunk.

So, we’ve learned that the write load does indeed cause heap fragmentation and that the long pauses occur when there are no large free chunks left in the heap.

##### Read-only Workload with Cache Churn

[![Read-only workload with cache churn](/img/read-churn-workload.png)](https://www.cloudera.com/wp-content/uploads/2011/02/read-churn-workload.png)

In the second workload, the clients perform only reads, and the set of records to be read is much larger than the size of the LRU block cache. So, we see a large amount of memory churn as items are pulled into and evicted from the cache.

The `free_space` graph reflects this – it shows much more frequent collections than the write-only workload. However, we note that the `max_chunk` graph stays pretty constant around its starting value. This suggests that the read-only workload doesn’t cause heap fragmentation nearly as badly as the write workload, even though the memory churn is much higher.

##### Read-only Workload without Cache Churn

The third workload, colored green in the overview graph, turned out to be quite boring. Because there’s no cache churn, the only allocations being done were short-lived objects for servicing each RPC request. Hence, they were never promoted to the old generation, and both `free_space` and `max_chunk` time series stayed entirely constant.

## Experiment Summary

To summarize the results of this experiment:

- The full GCs we’d like to eliminate are due to fragmentation, not concurrent-mode failure.
- The write-only workload causes fragmentation much more than either read workload.

## Why HBase Writes Fragment the Heap

Now that we know that write workloads cause rapid heap fragmentation, let’s take a step back and think about why. In order to do so, we’ll take a brief digression to give an overview of how HBase’s write path works.

##### The HBase Write Path

In order to store a very large dataset distributed across many machines, Apache HBase partitions each table into segments called Regions. Each region has a designated “start key” and “stop key”, and contains every row where the key falls between the two. This scheme can be compared to primary key-based range partitions in an RDBMS, though HBase manages the partitions automatically and transparently. Each region is typically less than a gigabyte in size, so every server in an HBase cluster is responsible for several hundred regions. Read and write requests are routed to the server currently hosting the target region.

Once a write request has reached the correct server, the new data is added to an in-memory structure called a *MemStore*. This is essentially a sorted map, per region, containing all recently written data. Of course, memory is a finite resource, and thus the region server carefully accounts memory usage and triggers a *flush* on a MemStore when the usage has crossed some threshold. The flush writes the data to disk and frees up the memory.

##### MemStore Fragmentation

Let’s imagine that a region server is hosting 5 regions — colored pink, blue, green, red, and yellow in the diagram below. It is being subjected to a random write workload where the writes are spread evenly across the regions and arrive in no particular order.

As the writes come in, new buffers are allocated for each row, and these buffers are promoted into the old generation, since they stay in the MemStore for several minutes waiting to be flushed. Since the writes arrive in no particular order, data from different regions is intermingled in the old generation. When one of the regions is flushed, however, this means we can’t free up any large contiguous chunk, and we’re guaranteed to get fragmentation:

[![Memstore Fragmentation on Flush](/img/frag-drawing.png)](https://www.cloudera.com/wp-content/uploads/2011/02/frag-drawing.png)

This behavior results in exactly what our experiment showed: over time, writes will always cause severe fragmentation in the old generation, leading to a full garbage collection pause.

## To be continued…

In this post we reviewed the results of our experiment, and came to understand why writes in HBase cause memory fragmentation. In the [next](http://blog.cloudera.com/blog/2011/03/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-3/) and [last post](http://blog.cloudera.com/blog/2011/03/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-3/) in this series, we’ll look at [the design of *MemStore-Local Allocation Buffers*](http://blog.cloudera.com/blog/2011/03/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-3/), which avoid fragmentation and thus avoid full GCs.





# Avoiding Full GCs in Apache HBase with MemStore-Local Allocation Buffers: Part 3

[March 7, 2011](http://blog.cloudera.com/blog/2011/03/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-3/)[By Todd Lipcon](http://blog.cloudera.com/blog/author/todd/) [(@tlipcon)](https://twitter.com/@tlipcon)[9 Comments](http://blog.cloudera.com/blog/2011/03/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-3/#comments)

Categories: [General](http://blog.cloudera.com/blog/category/general/) [HBase](http://blog.cloudera.com/blog/category/hbase/)

This is the third and final post in a series detailing a recent improvement in Apache HBase that helps to reduce the frequency of garbage collection pauses. Be sure you’ve read [part 1](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-1/) and [part 2](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-2/) before continuing on to this post.

## Recap

It’s been a few days since the first two posts, so let’s start with a quick refresher. In the [first post](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-1/) we discussed Java garbage collection algorithms in general and explained that the problem of lengthy pauses in HBase has only gotten worse over time as heap sizes have grown. In the [second post](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-2/) we ran an experiment showing that write workloads in HBase cause memory fragmentation as all newly inserted data is spread out into several MemStores which are freed at different points in time.

## Arena Allocators and TLABs

As identified in the previous post, we saw that the central issue is that data from different MemStores is all mixed up in the old generation. When we flush one MemStore, we only free up bits and pieces of heap instead of any large chunks. In other words, we’re violating one of the assumptions of the Java GC model — namely, that objects allocated together in time tend to die together. The allocation pattern of a random write workload guarantees nearly the opposite.

In order to attack this issue, we simply need to ensure that data for each region is allocated from the same area in the heap. In a language with manual memory management, this is typically done using a well-known pattern called *arena allocation*. In this pattern, every allocation is associated with a larger area of memory called an arena — the arena is simply divided up into smaller pieces as memory is allocated.

The most commonly seen application of this concept is the *thread-local allocation buffer*, or TLAB. In this model, each execution thread has its own memory arena, and all allocations done by that thread come from its own arena. There are several benefits to the use of TLABs:

1. There is often very good locality of access between a thread and the memory it allocates. For example, a thread that is processing some database request will need to allocate some local buffers which will be referred to over and over again during that request. Keeping all such buffers near each other in memory improves CPU cache locality and hence performance.
2. Since allocation is only done by a single thread from this arena, they can be satisfied with no locks or atomic operations required. This is known as *bump-the-pointer allocation*. The TLAB needs to maintain only a single *start* pointer, and allocations are satisfied by incrementing it forward by some number of bytes. This makes TLAB allocation extremely efficient.

In fact, the Sun JVM uses TLABs by default for small allocations. You can learn more about TLABs in the JVM in this [excellent blog post](https://blogs.oracle.com/jonthecollector/entry/a_little_thread_privacy_please).

## MemStore-Local Allocation Buffers

Unfortunately, the TLABs used in the JVM do not help solve the fragmentation issue experienced by HBase. This is because an individual handler thread in HBase actually handles requests for different regions throughout its lifetime – so even though the allocations come from a single thread-local arena, data for different MemStores are intermixed within the TLAB. When the memory is promoted to the old generation, the data remains intermingled.

However, it’s not too difficult to borrow the concept and apply the same idea to MemStores — coining the term MemStore-Local Allocation Buffer (MSLAB). Whenever a request thread needs to insert data into a MemStore, it shouldn’t allocate the space for that data from the heap at large, but rather from a memory arena dedicated to the target region. This should have the following benefits:

1. First and foremost, this means that data for different MemStores will not be intermingled near each other. When we flush a MemStore, we will be able to free the entire arena, and thus create a large free chunk in the old generation. This will hopefully reduce fragmentation and solve the garbage collection pause issue.
2. Additionally, we should hope to see some benefits from CPU cache locality within a region. HBase read operations target individual regions at a time, and often need to sort or search through data in a single MemStore. By moving all the bits of data for a MemStore to be near each other, we should expect to see improved CPU cache locality and better performance.

## Implementation

Unfortunately, standard Java does not give programmers the ability to allocate objects from memory arenas. But, in the case of HBase, we’re not dealing with particularly large or many *objects* — each piece of data consists of a single `KeyValue` object which is not large. Additionally each object is exactly the same size, so doesn’t cause significant fragmentation. Rather, it’s the `byte[]` arrays referred to by the `KeyValue` objects that cause the fragmentation. So, we simply need to ensure that the `byte[]` arrays are allocated from MSLABs instead of the heap.

It turns out this is not very difficult! The `KeyValue` class doesn’t just contain a `byte[]`, but also an `offset`field pointing into the byte array. So in order to place the data for different `KeyValue` objects near each other, we just need to take slices of a larger `byte[]` representing the MSLAB arena. The implementation looks something like this:

- Each `MemStore` instance has an associated instance of a new class `MemStoreLAB`.
- `MemStoreLAB` retains a structure called `curChunk` which consists of a 2MB `byte[]` and a `nextFreeOffset` pointer starting at 0.
- When a `KeyValue` is about to be inserted into the MemStore, it is first copied into `curChunk` and the `nextFreeOffset` pointer is bumped by the length of the new data.
- Should the 2MB chunk fill up, a new one is allocated from the JVM using the usual method: `new byte[2*1024*1024]`.

In order to keep this efficient, the entire algorithm is implemented lock-free, using atomic compare-and-swap operations on the `nextFreeOffset` pointer and the `curChunk` structure.

## Results

After implementing MSLABs, we expected to see significantly less fragmentation. So, to confirm this, I ran the same write-load generator as described in the prior post and graphed the results with the same methodology:

[![Memory Fragmentation with MSLABs enabled](/img/withkvallocs.png)](https://www.cloudera.com/wp-content/uploads/2011/03/withkvallocs.png)

This graph shows the experiment beginning with an entirely empty heap when the Region Server is started, and continuing through about an hour and a half of write load. As before, we see the `free_space` graph fluctuate back and forth as the concurrent collector runs. The `max_chunk` graph drops quickly at first as memory is allocated, but then eventually stabilizes. I’ve also included `num_blocks` — the total number of separate free chunks in the old generation — in this graph. You can see that this metric also stabilizes after an hour or so of runtime.

## The Best News of All

After producing the above graph, I let the insert workload run overnight, and then continued for several days. In all of this time, there was not a single GC pause that lasted longer than a second. The fragmentation problem was completely solved for this workload!

## How to try it

The MSLAB allocation scheme is available in Apache HBase 0.90.1, and part of CDH3 Beta 4 released last week. Since it is relatively new, it is not yet enabled by default, but it can be configured using the following flags:

| Configuration                                 | Description                                                  |
| --------------------------------------------- | ------------------------------------------------------------ |
| `hbase.hregion.memstore.mslab.enabled`        | Set to `true` to enable this feature                         |
| `hbase.hregion.memstore.mslab.chunksize`      | The size of the chunks allocated by MSLAB, in bytes (default 2MB) |
| `hbase.hregion.memstore.mslab.max.allocation` | The maximum size byte array that should come from the MSLAB, in bytes (default 256KB) |

## Future Work

As this is a very new feature, there are still a few rough edges to be worked out. In particular, each region now has a minimum of 2MB of memory usage on the region server – this means that a server hosting thousands of regions could have several GB of wasted memory sitting in unused allocation buffers. We need to figure out a good heuristic to automatically tune chunk size and avoid this kind of situation.

There are also a few more efficiency gains to be made. For example, we currently do an extra memory copy of data when moving it into the MSLAB chunk. This can be avoided for a modest CPU improvement.

Lastly, some work needs to be done to re-tune the suggested garbage collecting tuning parameters. Given this improvement, we may be able to tune the value of `-XX:CMSInitiatingOccupancyFraction` to a higher value than we did in prior versions.

## Conclusion

If you’ve been having problems with garbage collection pauses in Apache HBase, please give this experimental option a try and report back your results. According to our synthetic test workloads, it may significantly reduce or even eliminate the problem!

I had a great time working with HBase and the JVM to understand these memory fragmentation behaviors and then designing and implementing the MSLAB solution. If you found this series of posts interesting, you might be just the kind of engineer we’re looking for to join Cloudera. Please be sure to check out our [careers](http://blog.cloudera.com/company/careers) page and get in touch!