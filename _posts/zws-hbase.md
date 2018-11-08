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


