---
layout:     post
title:     BlockCache 101
subtitle:   Hbase BlockCache Detail
date:       2018-09-20
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - hbase
    - blockcache
    - cache

---

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