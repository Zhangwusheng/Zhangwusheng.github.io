---
layout:     post
title:     HBASE BlockCache 101 & Showdown（转）
subtitle:   Hbase BlockCache Detail
date:       2018-09-21
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - hbase
    - blockcache
    - cache

typora-copy-images-to: ..\img
typora-root-url: ..
---

# BlockCache 101

[原文在此](http://www.n10k.com/blog/blockcache-101/)

HBase is a distributed database built around the core concepts of an ordered write log and a log-structured merge tree. As with any database, optimized I/O is a critical concern to HBase. When possible, the priority is to not perform any I/O at all. This means that memory utilization and caching structures are of utmost importance. To this end, HBase maintains two cache structures: the “memory store” and the “block cache”. Memory store, implemented as the [`MemStore`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/regionserver/MemStore.java), accumulates data edits as they’re received, buffering them in memory [1](http://www.n10k.com/blog/blockcache-101/#1). The block cache, an implementation of the [`BlockCache`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/BlockCache.java) interface, keeps data blocks resident in memory after they’re read.

The `MemStore` is important for accessing recent edits. Without the `MemStore`, accessing that data as it was written into the write log would require reading and deserializing entries back out of that file, at least a `O(n)` operation. Instead, `MemStore` maintains a skiplist structure, which enjoys a `O(log n)`access cost and requires no disk I/O. The `MemStore` contains just a tiny piece of the data stored in HBase, however.

Servicing reads from the `BlockCache` is the primary mechanism through which HBase is able to serve random reads with millisecond latency. When a data block is read from HDFS, it is cached in the `BlockCache`. Subsequent reads of neighboring data – data from the same block – do not suffer the I/O penalty of again retrieving that data from disk [2](http://www.n10k.com/blog/blockcache-101/#2). It is the `BlockCache` that will be the remaining focus of this post.

## Blocks to cache

Before understanding the `BlockCache`, it helps to understand what exactly an HBase “block” is. In the HBase context, a block is a single unit of I/O. When writing data out to an HFile, the block is the smallest unit of data written. Likewise, a single block is the smallest amount of data HBase can read back out of an HFile. Be careful not to confuse an HBase block with an HDFS block, or with the blocks of the underlying file system – these are all different [3](http://www.n10k.com/blog/blockcache-101/#3).

HBase blocks come in 4 [varieties](https://github.com/apache/hbase/blob/0.98/hbase-common/src/main/java/org/apache/hadoop/hbase/io/hfile/BlockType.java): `DATA`, `META`, `INDEX`, and `BLOOM`.

`DATA` blocks store user data. When the `BLOCKSIZE` is specified for a column family, it is a hint for this kind of block. Mind you, it’s only a hint. While flushing the `MemStore`, HBase will do its best to honor this guideline. After each `Cell` is written, the writer checks if the amount written is >= the target `BLOCKSIZE`. If so, it’ll close the current block and start the next one [4](http://www.n10k.com/blog/blockcache-101/#4).

`INDEX` and `BLOOM` blocks serve the same goal; both are used to speed up the read path. `INDEX`blocks provide an index over the `Cell`s contained in the `DATA` blocks. `BLOOM` blocks contain a [bloom filter](http://en.wikipedia.org/wiki/Bloom_filter) over the same data. The index allows the reader to quickly know where a `Cell` should be stored. The filter tells the reader when a `Cell` is definitely absent from the data.

Finally, `META` blocks store information about the HFile itself and other sundry information – metadata, as you might expect. A more comprehensive overview of the HFile formats and the roles of various block types is provided in [Apache HBase I/O - HFile](http://blog.cloudera.com/blog/2012/06/hbase-io-hfile-input-output/).

## HBase BlockCache and its implementations

There is a single `BlockCache` instance in a region server, which means all data from all regions hosted by that server share the same cache pool [5](http://www.n10k.com/blog/blockcache-101/#5). The `BlockCache` is instantiated at region server startup and is retained for the entire lifetime of the process. Traditionally, HBase provided only a single `BlockCache` implementation: the [`LruBlockCache`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/LruBlockCache.java). The 0.92 release introduced the first alternative in [HBASE-4027](https://issues.apache.org/jira/browse/HBASE-4027): the [`SlabCache`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/slab/SlabCache.java). HBase 0.96 introduced another option via [HBASE-7404](https://issues.apache.org/jira/browse/HBASE-7404), called the [`BucketCache`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/bucket/BucketCache.java).

The key difference between the tried-and-true `LruBlockCache` and these alternatives is the way they manage memory. Specifically, `LruBlockCache` is a data structure that resides entirely on the JVM heap, while the other two are able to take advantage of memory from outside of the JVM heap. This is an important distinction because JVM heap memory is managed by the JVM Garbage Collector, while the others are not. In the cases of `SlabCache` and `BucketCache`, the idea is to reduce the GC pressure experienced by the region server process by reducing the number of objects retained on the heap.

### LruBlockCache

This is the default implementation. Data blocks are cached in JVM heap using this implementation. It is subdivided into three areas: single-access, multi-access, and in-memory. The areas are sized at 25%, 50%, 25% of the total `BlockCache` size, respectively [6](http://www.n10k.com/blog/blockcache-101/#6). A block initially read from HDFS is populated in the single-access area. Consecutive accesses promote that block into the multi-access area. The in-memory area is reserved for blocks loaded from column families flagged as `IN_MEMORY`. Regardless of area, old blocks are evicted to make room for new blocks using a Least-Recently-Used algorithm, hence the “Lru” in “LruBlockCache”.

### SlabCache

This implementation allocates areas of memory outside of the JVM heap using `DirectByteBuffer`s. These areas provide the body of this `BlockCache`. The precise area in which a particular block will be placed is based on the size of the block. By default, two areas are allocated, consuming 80% and 20% of the total configured off-heap cache size, respectively. The former is used to cache blocks that are approximately the target block size [7](http://www.n10k.com/blog/blockcache-101/#7). The latter holds blocks that are approximately 2x the target block size. A block is placed into the smallest area where it can fit. If the cache encounters a block larger than can fit in either area, that block will not be cached. Like `LruBlockCache`, block eviction is managed using an LRU algorithm.

### BucketCache

This implementation can be configured to operate in one of three different modes: [`heap`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/bucket/ByteBufferIOEngine.java), [`offheap`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/bucket/ByteBufferIOEngine.java), and [`file`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/bucket/FileIOEngine.java). Regardless of operating mode, the `BucketCache` manages areas of memory called “buckets” for holding cached blocks. Each bucket is created with a target block size. The `heap`implementation creates those buckets on the JVM heap; `offheap` implementation uses `DirectByteByffers` to manage buckets outside of the JVM heap; `file` mode expects a path to a file on the filesystem wherein the buckets are created. `file` mode is intended for use with a low-latency backing store – an in-memory filesystem, or perhaps a file sitting on SSD storage [8](http://www.n10k.com/blog/blockcache-101/#8). Regardless of mode, `BucketCache` creates 14 buckets of different sizes. It uses frequency of block access to inform utilization, just like `LruBlockCache`, and has the same single-access, multi-access, and in-memory breakdown of 25%, 50%, 25%. Also like the default cache, block eviction is managed using an LRU algorithm.

### Multi-Level Caching

Both the `SlabCache` and `BucketCache` are designed to be used as part of a multi-level caching strategy. Thus, some portion of the total `BlockCache` size is allotted to an `LruBlockCache` instance. This instance acts as the first level cache, “L1,” while the other cache instance is treated as the second level cache, “L2.” However, the interaction between `LruBlockCache` and `SlabCache` is different from how the `LruBlockCache` and the `BucketCache` interact.

The `SlabCache` strategy, called [`DoubleBlockCache`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/DoubleBlockCache.java), is to always cache blocks in both the L1 and L2 caches. The two cache levels operate independently: both are checked when retrieving a block and each evicts blocks without regard for the other. The `BucketCache` strategy, called [`CombinedBlockCache`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/CombinedBlockCache.java), uses the L1 cache exclusively for Bloom and Index blocks. Data blocks are sent directly to the L2 cache. In the event of L1 block eviction, rather than being discarded entirely, that block is demoted to the L2 cache.

## Which to choose?

There are two reasons to consider enabling one of the alternative `BlockCache` implementations. The first is simply the amount of RAM you can dedicate to the region server. Community wisdom recognizes the upper limit of the JVM heap, as far as the region server is concerned, to be somewhere between 14GB and 31GB [9](http://www.n10k.com/blog/blockcache-101/#9). The precise limit usually depends on a combination of hardware profile, cluster configuration, the shape of data tables, and application access patterns. You’ll know you’ve entered the danger zone when GC pauses and `RegionTooBusyException`s start flooding your logs.

The other time to consider an alternative cache is when response latency *really* matters. Keeping the heap down around 8-12GB allows the CMS collector to run very smoothly [10](http://www.n10k.com/blog/blockcache-101/#10), which has measurable impact on the 99th percentile of response times. Given this restriction, the only choices are to explore an alternative garbage collector or take one of these off-heap implementations for a spin.

This second option is exactly what I’ve done. In my [next post](http://www.n10k.com/blog/blockcache-showdown/), I’ll share some unscientific-but-informative experiment results where I compare the response times for different `BlockCache`implementations.

As always, stay tuned and keep on with the HBase!

------

1: The `MemStore` accumulates data edits as they’re received, buffering them in memory. This serves two purposes: it increases the total amount of data written to disk in a single operation, and it retains those recent changes in memory for subsequent access in the form of low-latency reads. The former is important as it keeps HBase write chunks roughly in sync with HDFS block sizes, aligning HBase access patterns with underlying HDFS storage. The latter is self-explanatory, facilitating read requests to recently written data. It’s worth pointing out that this structure is not involved in data durability. Edits are also written to the ordered write log, the [`HLog`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/regionserver/wal/HLog.java), which involves an HDFS append operation at a configurable interval, usually immediate.

2: Re-reading data from the local file system is the best-case scenario. HDFS is a distributed file system, after all, so the worst case requires reading that block over the network. HBase does its best to maintain data locality. These [two](http://www.larsgeorge.com/2010/05/hbase-file-locality-in-hdfs.html) [articles](http://hadoop-hbase.blogspot.com/2013/07/hbase-and-data-locality.html) provide an in-depth look at what data locality means for HBase and how its managed.

3: File system, HDFS, and HBase blocks are all different but related. The modern I/O subsystem is many layers of abstraction on top of abstraction. Core to that abstraction is the concept of a single unit of data, referred to as a “block”. Hence, all three of these storage layers define their own block, each of their own size. In general, a larger block size means increased sequential access throughput. A smaller block size facilitates faster random access.

4: Placing the `BLOCKSIZE` check after data is written has two ramifications. A single `Cell` is the smallest unit of data written to a `DATA` block. It also means a `Cell` cannot span multiple blocks.

5: This is different from the `MemStore`, for which there is a separate instance for every region hosted by the region server.

6: Until very recently, these memory partitions were statically defined; there was no way to override the 25/50/25 split. A given segment, the multi-access area for instance, could grow larger than it’s 50% allotment as long as the other areas were under-utilized. Increased utilization in the other areas will evict entries from the multi-access area until the 25/50/25 balance is attained. The operator could not change these default sizes. [HBASE-10263](https://issues.apache.org/jira/browse/HBASE-10263), shipping in HBase 0.98.0, introduces configuration parameters for these sizes. The flexible behavior is retained.

7: The “approximately” business is to allow some wiggle room in block sizes. HBase block size is a rough target or hint, not a strictly enforced constraint. The exact size of any particular data block will depend on the target block size and the size of the `Cell` values contained therein. The block size hint is specified as the default block size of 64kb.

8: Using the `BucketCache` in `file` mode with a persistent backing store has another benefit: persistence. On startup, it will look for existing data in the cache and verify its validity.

9: As I understand it, there’s two components advising the upper bound on this range. First is a limit on JVM object addressability. The JVM is able to reference an object on the heap with a 32-bit relative address instead of the full 64-bit native address. This optimization is only possible if the total heap size is less than 32GB. See [Compressed Oops](http://docs.oracle.com/javase/7/docs/technotes/guides/vm/performance-enhancements-7.html#compressedOop) for more details. The second is the ability of the garbage collector to keep up with the amount of object churn in the system. From what I can tell, the three sources of object churn are `MemStore`, `BlockCache`, and network operations. The first is mitigated by the `MemSlab` feature, enabled by default. The second is influenced by the size of your dataset vs. the size of the cache. The third cannot be helped so long as HBase makes use of a network stack that relies on data copy.

10: Just like with [8](http://www.n10k.com/blog/blockcache-101/#8), this is assuming “modern hardware”. The interactions here are quite complex and well beyond the scope of a single blog post.

Posted by Nick Dimiduk Feb 13th, 2014



# BlockCache Showdown

[原文在此](http://www.n10k.com/blog/blockcache-showdown/)

The HBase [`BlockCache`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/BlockCache.java) is an important structure for enabling low latency reads. As of HBase 0.96.0, there are no less than three different `BlockCache` implementations to choose from. But how to know when to use one over the other? There’s a little bit of guidance floating around out there, but nothing concrete. It’s high time the HBase community changed that! I did some benchmarking of these implementations, and these results I’d like to share with you here.

Note that this is my second post on the `BlockCache`. In my [previous post](http://www.n10k.com/blog/blockcache-101/), I provide an overview of the `BlockCache` in general as well as brief details about each of the implementations. I’ll assume you’ve read that one already.

The goal of this exercise is to directly compare the performance of different `BlockCache`implementations. The metric of concern is that of client-perceived response latency. Specifically, the concern is for the response latency at the 99th percentile of queries – that is, the worst case experience that the vast majority of users will ever experience. With this in mind, two different variables are adjusted for each test: RAM allotted and database size.

The first variable is the amount of RAM made available to the RegionServer process and is expressed in gigabytes. The `BlockCache` is sized as a portion of the total RAM allotted to the RegionServer process. For these tests, this is fixed at 60% of total RAM. The second variable is the size of the database over which the `BlockCache` is operating. This variable is also expressed in gigabytes, but in order to directly compare results generated as the first variable changes, this is also expressed as the ratio of database size to RAM allotted. Thus, this ratio is a rough description for the amount “cache churn” the RegionServer will experience, regardless of the magnitude of the values. With a smaller ratio, the `BlockCache` spends less time juggling blocks and more time servicing reads.

## Test Configurations

The tests were run across two single machine deployments. Both machines are identical, with 64G total RAM and 2x Xeon E5-2630@2.30GHz, for a total of 24 logical cores each. The machines both had 6x1T disks sharing HDFS burden, spinning at 7200 RPM. Hadoop and HBase were deployed using Apache Ambari from HDP-2.0. Each of these clusters-of-one were configured to be fully “distributed,” meaning that all Hadoop components were deployed as separate processes. The test client was also run on the machine under test, so as to omit any networking overhead from the results. The RegionServer JVM, Hotspot 64-bit Server v1.6.0_31, was configured to use the CMS collector.

Configurations are built assuming a random-read workload, so [`MemStore`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/regionserver/MemStore.java) capacity is sacrificed in favor of additional space for the `BlockCache`. The default [`LruBlockCache`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/LruBlockCache.java) is considered the baseline, so that cache is configured first and its memory allocations are used as guidelines for the other configurations. The goal is for each configuration to allow roughly the same amount of memory for the `BlockCache`, the `MemStore`s, and other activities of the HBase process itself.

It’s worth noting that the `LruBlockCache` configuration includes checks to ensure that JVM heap within the process is not oversubscribed. These checks enforce a limitation that only 80% of the heap may be assigned between the `MemStore` and `BlockCache`, leaving the remaining 20% for other HBase process needs. As the amount of RAM consumed by these configurations increases, this 20% is likely overkill. A production configuration using so much heap would likely want to override this over-subscription limitation. Unfortunately, this limit is not currently exposed as a configuration parameter. For large memory configurations that make use of off-heap memory management techniques, this limitation is likely not encountered.

Four different memory allotments were exercised: 8G (considered “conservative” heapsize), 20G (considered “safe” heapsize), 50G (complete memory subscription on this machine), and 60G (memory over-subscription for this machine). This is the total amount of memory made available to the RegionServer process. Within that process, memory is divided between the different subsystems, primarily the `BlockCache` and `MemStore`. Because some of the `BlockCache` implementations operate on RAM outside of the JVM garbage collector’s control, the size of the JVM heap is also explicitly mentioned. The total memory divisions for each configuration are as follows. Values are taken from the logs; [`CacheConfig`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/io/hfile/CacheConfig.java) initialization in the case of `BlockCache` implementations and [`MemStoreFlusher`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/main/java/org/apache/hadoop/hbase/regionserver/MemStoreFlusher.java)for the max heap and global MemStore limit.

------

| **Configuration**    | **Total Memory** | **Max Heap** | **BlockCache Breakdown**    | **Global MemStore Limit** |
| -------------------- | ---------------- | ------------ | --------------------------- | ------------------------- |
| LruBlockCache        | 8G               | 7.8G         | 4.7G lru                    | 1.6G                      |
| SlabCache            | 8G               | 1.5G         | 4.74G slabs + 19.8m lru     | 1.9G                      |
| BucketCache, heap    | 8G               | 7.8G         | 4.63G buckets + 47.9M lru   | 1.6G                      |
| BucketCache, offheap | 8G               | 1.9G         | 4.64G buckets + 48M lru     | 1.5G                      |
| BucketCache, tmpfs   | 8G               | 1.9G         | 4.64G buckets + 48M lru     | 1.5G                      |
| LruBlockCache        | 20G              | 19.4G        | 11.7G lru                   | 3.9G                      |
| SlabCache            | 20G              | 4.8G         | 11.8G slabs + 48.9M lru     | 3.8G                      |
| BucketCache, heap    | 20G              | 19.4G        | 11.54G buckets + 119.5M lru | 3.9G                      |
| BucketCache, offheap | 20G              | 4.9G         | 11.60G buckets + 120.0M lru | 3.8G                      |
| BucketCache, tmpfs   | 20G              | 4.8G         | 11.60G buckets + 120.0M lru | 3.8G                      |
| LruBlockCache        | 50G              | 48.8G        | 29.3G lru                   | 9.8G                      |
| SlabCache            | 50G              | 12.2G        | 29.35G slabs + 124.8M lru   | 9.6G                      |
| BucketCache, heap    | 50G              | 48.8G        | 30.0G buckets + 300M lru    | 9.8G                      |
| BucketCache, offheap | 50G              | 12.2G        | 29.0G buckets + 300.0M lru  | 9.6G                      |
| BucketCache, tmpfs   | 50G              | 12.2G        | 29.0G buckets + 300.0M lru  | 9.6G                      |
| LruBlockCache        | 60G              | 58.6G        | 35.1G lru                   | 11.7G                     |
| SlabCache            | 60G              | 14.6G        | 35.2G slabs + 149.8M lru    | 11.6G                     |
| BucketCache, heap    | 60G              | 58.6G        | 34.79G buckets + 359.9M lru | 11.7G                     |
| BucketCache, offheap | 60G              | 14.6G        | 34.80G buckets + 360M lru   | 11.6G                     |
| BucketCache, tmpfs   | 60G              | 14.6G        | 34.80G buckets + 360.0M lru | 11.6G                     |

------

These configurations are included in the test harness [repository](https://github.com/ndimiduk/perf_blockcache).

## Test Execution

HBase ships with a tool called [`PerformanceEvaluation`](https://github.com/apache/hbase/blob/0.98/hbase-server/src/test/java/org/apache/hadoop/hbase/PerformanceEvaluation.java), which is designed for generating a specific workload against an HBase cluster. These tests were conducted using the `randomRead` workload, executed in multi-threaded mode (as opposed to mapreduce mode). As of [HBASE-10007](https://issues.apache.org/jira/browse/HBASE-10007), this tool can produce latency information for individual read requests. [YCSB](https://github.com/brianfrankcooper/YCSB/wiki) was considered as an alternative load generator, but `PerformanceEvaluation` was preferred because it is provided out-of-the-box by HBase. Thus, hopefully these results are easily reproduced by other HBase users.

The schema of the test dataset is as follows. It is comprised of a single table with a single column family, called “info”. Each row contains a single column, called “data”. The rowkey is 26 bytes long; the column value is 1000 bytes. Thus, a single row is a total of 1032 bytes, or just over 1K, of user data. Cell tags were not enabled for these tests.

The test was run three times for each configuration: database size to RAM allotted ratios of 0.5:1, 1.5:1, and 4.5:1. Because the `BlockCache` consumes roughly 60% of available RegionServer RAM, these ratios translated roughly into database size to `BlockCache` size ratios of 1:1, 3:1, 9:1. That is, roughly, not exactly, and in the `BlockCache`’s favor. Thus, with the first configuration, the `BlockCache`shouldn’t need to ever evict a block while in the last configuration, the `BlockCache` will be evicting stale blocks frequently. Again, the goal here is to evaluate the performance of a `BlockCache` as it experiences varying working conditions.

For all tests, the number of clients was fixed at 5, far below the number of available RPC handlers. This is consistent with the desire to benchmark individual read latency with minimal overhead from context switching between tasks. A future test can examine the overall latency (and, hopefully, throughput) impact of varying numbers of concurrent clients. My intention with [HBASE-9953](https://issues.apache.org/jira/browse/HBASE-9953) is to simplify managing this kind of test.

Before a test is run, the database is created and populated. This is done using the `sequentialWrite`command, also provided by `PerformanceEvaluation`. Once created, the RegionServer was restarted using the desired configuration and the `BlockCache` warmed. Warming the cache was performed in one of two ways, depending on the ratio of database size to RAM allotted. For the 0.5:1, the entire table was scanned with a scanner configured with `cacheBlocks=true`. For this purpose, a modified version of the HBase shell’s `count` command was used. For other ratios, the `randomRead` command was used with a sampling rate of 0.1.

With the cache initially warmed, the test was run. Again, `randomRead` was used to execute the test. This time the sampling rate was set to 0.01 and the latency flag was enabled so that response times would be collected. This test was run 3 times, with the last run being collected for the final result. This was repeated for each permutation of configuration and database:RAM ratio.

HBase served no other workload while under test – there were no concurrent scan or write operations being served. This is likely not the case with real-world application deployments. The previous table was dropped before creating the next, so that the only user table on the system was the table under test.

The test harness used to run these tests is crude, but it’s [available](https://github.com/ndimiduk/perf_blockcache) for inspection. It also includes patch files for all configurations, so direct reproduction is possible.

## Initial Results

[![Click through for charts](/img/perfeval_blockcache_50G.jpg)](http://www.n10k.com/assets/perfeval_blockcache_v1.pdf)

The [first view](http://www.n10k.com/assets/perfeval_blockcache_v1.pdf) on the data is comparing the behavior of implementations at a given memory footprint. This view is informative of how an implementation performs as the ratio of memory footprint to database size increases. The amount of memory under management remains fixed. With the smallest memory footprint and smallest database size, the 99% response latency is pretty consistent across all implementations. As the database size grows, the heap-based implementations begin to separate from the pack, suffering consistently higher latency. This turns out to be a consistent trend regardless of the amount of memory under management.

Also notice that the `LruBlockCache` is holding its own alongside the off-heap implementations with the 20G RAM hosting both the 30G and 90G data sets. It falls away in the 50G RAM test though, which indicates to me that the effective maximum size for this implementation is somewhere between these two values. This is consistent with the “community wisdom” referenced in the [previous post](http://www.n10k.com/blog/blockcache-101/).

[![Click through for charts](/img/perfeval_blockcache_buckettmpfs.jpg)](http://www.n10k.com/assets/perfeval_blockcache_v2.pdf)

The [second view](http://www.n10k.com/assets/perfeval_blockcache_v2.pdf) is a pivot on the same data that looks at how a single implementation performs as the overall amount of data scales up. In this view, the ratio of memory footprint to database size is held fixed while the absolute values are increased. This is interesting as it suggests how an implementation might perform as it “scales up” to match increasing memory sizes provided by newer hardware.

From this view it’s much easier to see that both the `LruBlockCache` and `BucketCache`implementations suffer no performance degradation with increasing memory sizes – *so long as* the dataset fits in RAM. This result for the `LruBlockCache` surprised me a little. It indicates to me that under the conditions of this test, the on-heap cache is able to reach a kind of steady-state with the Garbage Collector.

The other surprise illustrated by this view is that the `SlabCache` imposes some overhead on managing increasingly larger amounts of memory. This overhead is present even when the dataset fits into RAM. In this, it is inferior to the `BucketCache`.

From this view’s perspective, I believe the `BucketCache` running in `tmpfs` mode is the most efficient implementation for larger memory footprints, with `offheap` mode coming in a close second. Operationally, the `offheap` mode is simpler to configure as it requires only changes to HBase configuration files. It also suggests the cache is of decreasing benefit with larger datasets (though this should be intuitively obvious).

Based on this data, I would recommend considering use of an off-heap `BucketCache` cache solution when your database size is far larger than the amount of available cache, especially when the absolute size of available memory is larger than 20G. This data can be used to inform the purchasing decisions regarding amount of memory required to host a dataset of a given size. Finally, I would consider deprecating the `SlabCache` implementation in favor of the `BucketCache`.

Here’s the [raw results](http://www.n10k.com/assets/perfeval_blockcache.csv). It includes additional latency measurements at the 95% and 99.9%.

## Followup test

[![Click through for chart](/img/perfeval_L2cache.jpg)](http://www.n10k.com/assets/perfeval_L2cache.pdf)

With the individual implementation baselines established, it’s time to examine how a “real world” configuration holds up. The `BucketCache` and `SlabCache` are designed to be run as a multi-level configuration, after all. For this, I chose to examine only the 50G memory footprint. The total 50G was divided between onheap and offheap memory. Two additional configurations were created for each implementation: 10G onheap + 40G offheap and 20G onheap + 30G offheap. These are compared to running with the full 50G heap and `LruBlockCache`.

This result is the most impressive of all. When properly configured in L1+L2 deployment, the `BucketCache` is able to maintain sub-millisecond response latency even with the largest database tested. This configuration significantly outperforms both the single-level `LruBlockCache` and the (effectively) single-level `BucketCache`. There is no apparent difference between 10G heap and 20G heap configurations, which leads me to believe, for this test, the non-data blocks fit comfortably in the `LruBlockCache` with even the 10G heap configuration.

Again, the [raw results](http://www.n10k.com/assets/perfeval_L2cache.csv) with additional latency measurements.

## Conclusions

When a dataset fits into memory, the lowest latency results are experienced using the `LruBlockCache`. This result is consistent regardless of how large the heap is, which is perhaps surprising when compared to “common wisdom.” However, when using a larger heap size, even a slight amount of `BlockCache` churn will cause the `LruBlockCache` latency to spike. Presumably this is due to the increased GC activity required to manage a large heap. This indicates to me that this test establishes a kind of false GC equilibrium enjoyed by this implementation. Further testing would intermix other activities into the workload and observe the impact.

When a dataset is just a couple times larger than available `BlockCache` and the region server has a large amount of RAM to dedicate to caching, it’s time to start exploring other options. The `BucketCache` using the `file` configuration running against a tmpfs mount holds up well to an increasing amount of RAM, as does the `offheap` configuration. Despite having slightly higher latency than the `BucketCache` implementations, the `SlabCache` holds its own. Worryingly, though, as the amount of memory under management increases, its trend lines show a gradual rise in latency.

Be careful not to oversubscribe the RAM in systems running any of these configurations, as this causes latency to spike dramatically. This is most clear in the heap-based `BlockCache`implementations. Oversubscribing the memory on a system serving far more data than it has available cache results in the worst possible performance.

I hope this experiment proves useful to the wider community. Hopefully these results can be reproduced without difficulty and that other can pick up where I’ve left off. Though these results are promising, a more thorough study is warranted. Perhaps someone out there with even larger memory machines can extend the X-axis of these graphs into the multiple-hundreds of gigabytes.

Posted by Nick Dimiduk Mar 7th, 2014