```

  /** Parameter name for # days to keep MVCC values during a major compaction */
hbase.hstore.compaction.keep.seqId.period
这个参数Hbase文档里面没有，默认值是5天

  /** At least to keep MVCC values in hfiles for 5 days */
  public static final int MIN_KEEP_SEQID_PERIOD = 5;
  
```




Meta的regoin的打开:

HMaster.run

调用startActiveMasterManager，startActiveMasterManager调用finishActiveMasterInitialization，finishActiveMasterInitialization调用

```
this.fileSystemManager = new MasterFileSystem(conf);
```

MasterFileSystem构造函数调用了createInitialFileSystemLayout,
createInitialFileSystemLayout调用了 checkRootDir , checkRootDir调用了 bootstrap
```
    // Make sure the meta region directory exists!
    if (!FSUtils.metaRegionExists(fs, rd)) {
      bootstrap(rd, c);
    }
```

bootstrap调用了HRegion.createHRegion


C:\Work\Source\HDP\hbase-release-HDP-3.0.0.0-1634-tag\hbase-server\src\main\java\org\apache\hadoop\hbase\regionserver\RSRpcServices.java

openRegion函数调用了  OpenRegionHandler  ,OpenRegionHandler. process函数里面调用了openRegion,openRegion调用了HRegion.openHRegion

这里会加载Hstore的目录下面的文件,并且打开

HRegion.flush这里可以看到flush的整个过程





Hbase

判断memstor需要刷新的标准：

在写入数据时，

org.apache.hadoop.hbase.regionserver.RSRpcServices#mutate

首先会reclaimMemStoreMemory，来判断是否需要flush，获取flush的类型：

```
flushType = isAboveHighWaterMark();

```

org.apache.hadoop.hbase.regionserver.RegionServerAccounting#isAboveHighWaterMark

org.apache.hadoop.hbase.io.util.MemorySizeUtil#getGlobalMemStoreSize

这里综合考虑了对外内存和堆内内存的情况，如果是堆内内存，那么读取JVM配置的最大可用内存，乘以配置的比例，如果是对外内存，获取配置的对外内存的大小，乘以配置的比例。优先选择对外内存，即如果配置了对外内存，那么优先使用对外内存！





Flush Region的时候，如果超出了Hfile的个数，那么会请求split region！

org.apache.hadoop.hbase.regionserver.MemStoreFlusher#flushRegion(org.apache.hadoop.hbase.regionserver.MemStoreFlusher.FlushRegionEntry)



这里很恐怖，如果要求刷新的时候，Hfile过多，会请求split，同时把这个刷新请求在此放入到队列里面去，如果下次再碰到这个请求，那么会log一下！如果不需要Split，那么这时候就会请求SystemCompaction!!



注意：如果使用了对外内存，必须配置MSLAB为turn on！

```

  public static long getOnheapGlobalMemStoreSize(Configuration conf) {
    long max = -1L;
    final MemoryUsage usage = safeGetHeapMemoryUsage();
    if (usage != null) {
      max = usage.getMax();
    }
    float globalMemStorePercent = getGlobalMemStoreHeapPercent(conf, true);
    return ((long) (max * globalMemStorePercent));
  }
  

public static Pair<Long, MemoryType> getGlobalMemStoreSize(Configuration conf) {
  long offheapMSGlobal = conf.getLong(OFFHEAP_MEMSTORE_SIZE_KEY, 0);// Size in MBs
  if (offheapMSGlobal > 0) {
    // Off heap memstore size has not relevance when MSLAB is turned OFF. We will go with making
    // this entire size split into Chunks and pooling them in MemstoreLABPoool. We dont want to
    // create so many on demand off heap chunks. In fact when this off heap size is configured, we
    // will go with 100% of this size as the pool size
    if (MemStoreLAB.isEnabled(conf)) {
      // We are in offheap Memstore use
      long globalMemStoreLimit = (long) (offheapMSGlobal * 1024 * 1024); // Size in bytes
      return new Pair<>(globalMemStoreLimit, MemoryType.NON_HEAP);
    } else {
      // Off heap max memstore size is configured with turning off MSLAB. It makes no sense. Do a
      // warn log and go with on heap memstore percentage. By default it will be 40% of Xmx
      LOG.warn("There is no relevance of configuring '" + OFFHEAP_MEMSTORE_SIZE_KEY + "' when '"
          + MemStoreLAB.USEMSLAB_KEY + "' is turned off."
          + " Going with on heap global memstore size ('" + MEMSTORE_SIZE_KEY + "')");
    }
  }
  return new Pair<>(getOnheapGlobalMemStoreSize(conf), MemoryType.HEAP);
}
```







globalMemStoreLimit


```
public RegionServerAccounting(Configuration conf) {
    Pair<Long, MemoryType> globalMemstoreSizePair = MemorySizeUtil.getGlobalMemStoreSize(conf);
    this.globalMemStoreLimit = globalMemstoreSizePair.getFirst();
    this.memType = globalMemstoreSizePair.getSecond();
    this.globalMemStoreLimitLowMarkPercent =
        MemorySizeUtil.getGlobalMemStoreHeapLowerMark(conf, this.memType == MemoryType.HEAP);
    // When off heap memstore in use we configure the global off heap space for memstore as bytes
    // not as % of max memory size. In such case, the lower water mark should be specified using the
    // key "hbase.regionserver.global.memstore.size.lower.limit" which says % of the global upper
    // bound and defaults to 95%. In on heap case also specifying this way is ideal. But in the past
    // we used to take lower bound also as the % of xmx (38% as default). For backward compatibility
    // for this deprecated config,we will fall back to read that config when new one is missing.
    // Only for on heap case, do this fallback mechanism. For off heap it makes no sense.
    // TODO When to get rid of the deprecated config? ie
    // "hbase.regionserver.global.memstore.lowerLimit". Can get rid of this boolean passing then.
    this.globalMemStoreLimitLowMark =
        (long) (this.globalMemStoreLimit * this.globalMemStoreLimitLowMarkPercent);
    this.globalOnHeapMemstoreLimit = MemorySizeUtil.getOnheapGlobalMemStoreSize(conf);
    this.globalOnHeapMemstoreLimitLowMark =
        (long) (this.globalOnHeapMemstoreLimit * this.globalMemStoreLimitLowMarkPercent);
  }
```