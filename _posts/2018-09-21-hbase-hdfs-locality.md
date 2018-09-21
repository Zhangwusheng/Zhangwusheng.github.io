---
layout:     post
title:     HBase File Locality in HDFS（转）
subtitle:   HBase File Locality in HDFS
date:       2018-09-21
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - hbase
    - hdfs
	- Locality
	- 本地化

typora-copy-images-to: ..\img
typora-root-url: ..
---

# HBase File Locality in HDFS

[原文在此](http://www.larsgeorge.com/2010/05/hbase-file-locality-in-hdfs.html)  

One of the more ambiguous things in [Hadoop](http://hadoop.apache.org/common/) is block replication: it happens automatically and you should not have to worry about it. [HBase](http://hadoop.apache.org/hbase/) relies on it 100% to provide the data safety as it stores its files into the [distributed file system](http://www.larsgeorge.com/2009/10/hbase-architecture-101-storage.html). While that works completely transparent, one of the more advanced questions asked though is how does this affect performance? This usually arises when the user starts writing [MapReduce](http://hadoop.apache.org/mapreduce/) jobs against either HBase or Hadoop directly. Especially with larger data being stored in HBase, how does the system take care of placing the data close to where it is needed? This is referred to data locality and in case of HBase using the Hadoop file system (HDFS) there may be doubts how that is working.   First let's see how Hadoop handles this. The MapReduce documentation advertises the fact that tasks run close to the data they process. This is achieved by breaking up large files in HDFS into smaller chunks, or so called blocks. That is also the reason why the block size in Hadoop is much larger than you may know them from operating systems and their file systems. Default setting is 64MB, but usually 128MB is chosen, if not even larger when you are sure all your files are larger than a single block in size. Each block maps to a task run to process the contained data. That also means larger block sizes equal fewer map tasks to run as the number of mappers is driven by the number of blocks that need processing. Hadoop knows where blocks are located and runs the map tasks directly on the node that hosts it (actually one of them as replication means it has a few hosts to chose from). This is how it guarantees data locality during MapReduce.  Back to HBase. When you have arrived at that point with Hadoop and you now understand that it can process data locally you start to question how this may work with HBase. If you have read my [post](http://www.larsgeorge.com/2009/10/hbase-architecture-101-storage.html) on HBase's storage architecture you saw that HBase simply stores files in HDFS. It does so for the actual data files (HFile) as well as its log (WAL). And if you look into the code it simply uses `FileSystem.create(Path path)` to create these. When you then consider two access patterns, a) direct random access and b) MapReduce scanning of tables, you wonder if care was taken that the HDFS blocks are close to where they are read by HBase.   One thing upfront, if you do not co-share your cluster with Hadoop and HBase but instead employ a separate Hadoop as well as a stand-alone HBase cluster then there is no data locality - and it can't be. That equals to running a separate MapReduce cluster where it would not be able to execute tasks directly on the datanode. It is imperative for data locality to have them running on the same cluster, Hadoop (as in the HDFS), MapReduce and HBase. End of story.   OK, you them all co-located on a single (hopefully larger) cluster? Then read on. How does Hadoop figure out where data is located as HBase accesses it. Remember the access pattern above, both go through a single piece of software called a RegionServer. Case a) uses random access patterns while b) scans all contiguous rows of a table but does so through the same API. As explained in my referenced post and mentioned above, HBase simply stores files and those get distributed as replicated blocks across all data nodes of the HDFS. Now imagine you stop HBase after saving a lot of data and restarting it subsequently. The region servers are restarted and assign a seemingly random number of regions. At this very point there is no data locality guaranteed - how could it be?  The most important factor is that HBase is not restarted frequently and that it performs house keeping on a regular basis. These so called compactions rewrite files as new data is added over time. All files in HDFS once written are immutable (for all sorts of reasons). Because of that, data is written into new files and as their number grows HBase compacts them into another set of new, consolidated files. And here is the kicker: HDFS is smart enough to put the data where it is needed! How does that work you ask? We need to take a deep dive into Hadoop's source code and see how the above `FileSystem.create(Path path)` that HBase uses works. We are running on HDFS here, so we are actually using `DistributedFileSystem.create(Path path)`which looks like this: 



```
public FSDataOutputStream create(Path f) throws IOException {
return create(f, true);
}
```

It returns a `FSDataOutputStream` and that is create like so: 

```
public FSDataOutputStream create(Path f, FsPermission permission, boolean overwrite, int bufferSize, short replication, long blockSize, Progressable progress) throws IOException {
return new FSDataOutputStream(dfs.create(getPathName(f), permission, overwrite, replication, blockSize, progress, bufferSize), statistics);
}
```

It uses a `DFSClient` instance that is the "umbilical" cord connecting the client with the NameNode: 

```
this.dfs = new DFSClient(namenode, conf, statistics);
```

What is returned though is a `DFSClient.DFSOutputStream` instance. As you write data into the stream the `DFSClient` aggregates it into "packages" which are then written as blocks to the data nodes. This happens in `DFSClient.DFSOutputStream.DataStreamer`(please hang in there, we are close!) which runs as a daemon thread in the background. The magic unfolds now in a few hops on the stack, first in the daemon `run()` it gets the list of nodes to store the data on: 

```
nodes = nextBlockOutputStream(src);
```

This in turn calls: 

```
long startTime = System.currentTimeMillis();
lb = locateFollowingBlock(startTime);
block = lb.getBlock();
nodes = lb.getLocations();
```

We follow further down and see that `locateFollowingBlocks()` calls: 

```
return namenode.addBlock(src, clientName);
```

Here is where it all comes together. The name node is called to add a new block and the `src` parameter indicates for what file, while `clientName` is the name of the `DFSClient` instance. I skip one more small method in between and show you the next bigger step involved: 

```
public LocatedBlock getAdditionalBlock(String src, String clientName) throws IOException {
...
INodeFileUnderConstruction pendingFile  = checkLease(src, clientName);
...
fileLength = pendingFile.computeContentSummary().getLength();
blockSize = pendingFile.getPreferredBlockSize();
clientNode = pendingFile.getClientNode();
replication = (int)pendingFile.getReplication();
 
// choose targets for the new block tobe allocated.
DatanodeDescriptor targets[] = replicator.chooseTarget(replication, clientNode, null, blockSize);
...
}
```

We are finally getting to the core of this code in the `replicator.chooseTarget()` call: 

```
rivate DatanodeDescriptor chooseTarget(int numOfReplicas, DatanodeDescriptor writer, List<Node> excludedNodes, long blocksize, int maxNodesPerRack, List<DatanodeDescriptor> results) {
 
if (numOfReplicas == 0 || clusterMap.getNumOfLeaves()==0) {
return writer;
}
 
int numOfResults = results.size();
boolean newBlock = (numOfResults==0);
if (writer == null && !newBlock) {
writer = (DatanodeDescriptor)results.get(0);
}
 
try {
switch(numOfResults) {
case 0:
writer = chooseLocalNode(writer, excludedNodes, blocksize, maxNodesPerRack, results);
if (--numOfReplicas == 0) {
break;
}
case 1:
chooseRemoteRack(1, results.get(0), excludedNodes, blocksize, maxNodesPerRack, results);
if (--numOfReplicas == 0) {
break;
}
case 2:
if (clusterMap.isOnSameRack(results.get(0), results.get(1))) {
chooseRemoteRack(1, results.get(0), excludedNodes, blocksize, maxNodesPerRack, results);
} else if (newBlock) {
chooseLocalRack(results.get(1), excludedNodes, blocksize, maxNodesPerRack, results);
} else {
chooseLocalRack(writer, excludedNodes, blocksize, maxNodesPerRack, results);
}
if (--numOfReplicas == 0) {
break;
}
default:
chooseRandom(numOfReplicas, NodeBase.ROOT, excludedNodes, blocksize, maxNodesPerRack, results);
}
} catch (NotEnoughReplicasException e) {
FSNamesystem.LOG.warn("Not able to place enough replicas, still in need of " + numOfReplicas);
}
return writer;
}
```

Recall that we have started with the `DFSClient` and created a file which was subsequently filled with data. As the blocks need writing out the above code checks first if that can be done on the same host that the client is on, i.e. the "writer". That is "case 0". In "case 1" the code tries to find a remote rack to have a distant replication of the block. Lastly is fills the list of required replicas with local or machines of another rack.   So this means for HBase that as the region server stays up for long enough (which is the default) that after a major compaction on all tables - which can be invoked manually or is triggered by a configuration setting - it has the files local on the same host. The data node that shares the same physical host has a copy of all data the region server requires. If you are running a scan or get or any other use-case you can be sure to get the best performance.  Finally a good overview over the HDFS design and data replication can be found [here](http://hadoop.apache.org/common/docs/r0.20.2/hdfs_design.html#Data+Replication). Also note that the HBase team is working on redesigning how the Master is assigning the regions to servers. The plan is to improve it so that regions are deployed on the server where most blocks are. This will particularly be useful after a restart because it would guarantee a better data locality right off the bat. Stay tuned! 