

org.apache.hadoop.hbase.backup.BackupDriver#addOptions

运行参数：

这个类使用了org.apache.hadoop.util.ToolRunner#run(org.apache.hadoop.conf.Configuration, org.apache.hadoop.util.Tool, java.lang.String[])来运行，这个类会首先进行hadoop相关的解析。

支持的Hadoop命令行参数包括:

```java
*     -conf &lt;configuration file&gt;     specify a configuration file
*     -D &lt;property=value&gt;            use value for given property
*     -fs &lt;local|namenode:port&gt;      specify a namenode
*     -jt &lt;local|resourcemanager:port&gt;    specify a ResourceManager
*     -files &lt;comma separated list of files&gt;    specify comma separated
*                            files to be copied to the map reduce cluster
*     -libjars &lt;comma separated list of jars&gt;   specify comma separated
*                            jar files to include in the classpath.
*     -archives &lt;comma separated list of archives&gt;    specify comma
*             separated archives to be unarchived on the compute machines.
```

解析之后的变量，会保存到conf对象中。

然后会添加自己的命令行选项

```
@Override
protected void addOptions() {
  // define supported options
  addOptNoArg(OPTION_DEBUG, OPTION_DEBUG_DESC);
  addOptWithArg(OPTION_TABLE, OPTION_TABLE_DESC);
  addOptWithArg(OPTION_BANDWIDTH, OPTION_BANDWIDTH_DESC);
  addOptWithArg(OPTION_WORKERS, OPTION_WORKERS_DESC);
  addOptWithArg(OPTION_RECORD_NUMBER, OPTION_RECORD_NUMBER_DESC);
  addOptWithArg(OPTION_SET, OPTION_SET_DESC);
  addOptWithArg(OPTION_PATH, OPTION_PATH_DESC);
  addOptWithArg(OPTION_YARN_QUEUE_NAME, OPTION_YARN_QUEUE_NAME_DESC);
  
}

 public static final String OPTION_TABLE = "t";
  public static final String OPTION_TABLE_DESC = "Table name. If specified, only backup images,"
      + " which contain this table will be listed.";

public static final String OPTION_BANDWIDTH = "b";
  public static final String OPTION_BANDWIDTH_DESC = "Bandwidth per task (MapReduce task) in MB/s";

  public static final String OPTION_WORKERS = "w";
  public static final String OPTION_WORKERS_DESC = "Number of parallel MapReduce tasks to execute";

 
  public static final String OPTION_RECORD_NUMBER = "n";
  public static final String OPTION_RECORD_NUMBER_DESC =
      "Number of records of backup history. Default: 10";

  public static final String OPTION_SET = "s";
  public static final String OPTION_SET_DESC = "Backup set name";

 public static final String OPTION_PATH = "p";
  public static final String OPTION_PATH_DESC = "Backup destination root directory path";

  public static final String OPTION_YARN_QUEUE_NAME = "q";
  public static final String OPTION_YARN_QUEUE_NAME_DESC = "Yarn queue name to run backup create command on";

```





backup action type -t -p -q  -s



| 动作     | 参数                                          | 只允许一个会话 | 一致性检查 | 备注                                                         |
| -------- | --------------------------------------------- | -------------- | ---------- | ------------------------------------------------------------ |
| create   | create full\|increment  path  -s\|-t -w -q -b | Y              | Y          |                                                              |
| DESCRIBE | DESCRIBE backupId                             | N              | N          |                                                              |
| PROGRESS | PROGRESS [backupId]                           | N              | N          | backid如果为空，那么选择状态为running的                      |
| DELETE   | DELETE backupId \[backupId]\[backupId]        | N              | N          | 可以有多个backupId                                           |
| HISTORY  | HISTORY -s\|-t \[-p] \[-n]                    | N              | N          | 如果-n没有，默认加载十条记录，如果-p有，那么从文件系统加载，如果-s或者-t有那么从元数据表加载，两者逻辑不通 |
| SET      | SET_ADD setName tableNames,tableNames         | N              | N          |                                                              |
|          | SET_REMOVE setName tableNames,tableNames      | N              | N          |                                                              |
|          | SET_DELETE  setName                           | N              | N          |                                                              |
|          | SET_DESCRIBE setName                          | N              | N          |                                                              |
|          | SET_LIST                                      | N              | N          |                                                              |
| REPAIR   |                                               |                |            |                                                              |
| MERGE    | MERGE backupId,backupId,backupId              |                |            |                                                              |
|          |                                               |                |            |                                                              |





首先分析Create：



如果是-s，表示是一个集合，那么首先获取集合里面有哪些表：

org.apache.hadoop.hbase.backup.impl.BackupMetaTable#describeBackupSet

实际上就是读取backup:system表的rowkey为backupset:setName的meta列，这里面记录了这个set对应的表名的列表，如果set里面没有表或者找不到set，抛出异常，这里就是把set转换成tablename的列表。

```
public List<TableName> describeBackupSet(String name) throws IOException {
  if (LOG.isTraceEnabled()) {
    LOG.trace(" Backup set describe: " + name);
  }
  Table table = null;
  try {
    table = connection.getTable(tableName);
    Get get = createGetForBackupSet(name);
    Result res = table.get(get);
    if (res.isEmpty()) return null;
    res.advance();
    String[] tables = cellValueToBackupSet(res.current());
    return toList(tables);
  } finally {
    if (table != null) {
      table.close();
    }
  }
}

  private Get createGetForBackupSet(String name) {
    Get get = new Get(rowkey(SET_KEY_PREFIX, name));
    get.addFamily(BackupMetaTable.META_FAMILY);
    return get;
  }
```



然后解析带宽参数，worker数量，以及yarn队列参数，然后生成BackupAdminImpl对象，进行备份：

```
try (BackupAdminImpl admin = new BackupAdminImpl(conn);) {

  BackupRequest.Builder builder = new BackupRequest.Builder();
  BackupRequest request =
      builder
          .withBackupType(BackupType.valueOf(args[1].toUpperCase()))
          .withTableList(
            tables != null ? Lists.newArrayList(BackupUtils.parseTableNames(tables)) : null)
          .withTargetRootDir(targetBackupDir).withTotalTasks(workers)
          .withBandwidthPerTasks(bandwidth).withBackupSetName(setName).build();
  String backupId = admin.backupTables(request);
  System.out.println("Backup session " + backupId + " finished. Status: SUCCESS");
} catch (IOException e) {
  System.out.println("Backup session finished. Status: FAILURE");
  throw e;
}
```





```
@Override
public String backupTables(BackupRequest request) throws IOException {
  BackupType type = request.getBackupType();
  String targetRootDir = request.getTargetRootDir();
  List<TableName> tableList = request.getTableList();

首先生成backupId，但是这个backupId在进行完毕后才会返回，这里可以优化一下！或者利用RUNNING状态返回，但是RUNNING状态一旦结束，就会返回这个ID，然后根据这个ID来查询相关状态。

  String backupId = BackupRestoreConstants.BACKUPID_PREFIX + EnvironmentEdgeManager.currentTime();
  if (type == BackupType.INCREMENTAL) {
   #如果是增量备份，那么会进行如下检查：
   表 backup:system
   rowkey：incrbackupset:[$Path]，列簇为meta，列名为各个表明
   hbase注释为：qualifier = table name - we use table names as qualifiers
   
   #这里的逻辑很重要！很明显，在全量创建备份的时候，每个表的全量备份有可能自己写自己的一个增量额备份的列！否则这里会出错！参见代码FullTableBackupClient.execute里面，这里面有一行代码：
     backupManager.addIncrementalBackupTableSet(backupInfo.getTables());，最终会调用BackupMetaTable#createPutForIncrBackupTableSet
这一行就是把全量备份的表的表名作为一个列写入到增量备份里面去，所以增量备份才有基础去做！！！

    Set<TableName> incrTableSet = null;
    try (BackupMetaTable table = new BackupMetaTable(conn)) {
      incrTableSet = table.getIncrementalBackupTableSet(targetRootDir);
    }

    if (incrTableSet.isEmpty()) {
      String msg =
          "Incremental backup table set contains no tables. "
              + "You need to run full backup first "
              + (tableList != null ? "on " + StringUtils.join(tableList, ",") : "");

      throw new IOException(msg);
    }
    if (tableList != null) {
      tableList.removeAll(incrTableSet);
      if (!tableList.isEmpty()) {
        String extraTables = StringUtils.join(tableList, ",");
        String msg =
            "Some tables (" + extraTables + ") haven't gone through full backup. "
                + "Perform full backup on " + extraTables + " first, " + "then retry the command";
        throw new IOException(msg);
      }
    }
    tableList = Lists.newArrayList(incrTableSet);
  }
  
  每一个表的备份路径是：root/backupID/namespace/table，如果目录已经存在，那么就会报错。
  如果已经存在，意味着已经进行过备份了，那么既不需要了！
  if (tableList != null && !tableList.isEmpty()) {
    for (TableName table : tableList) {
      String targetTableBackupDir =
          HBackupFileSystem.getTableBackupDir(targetRootDir, backupId, table);
      Path targetTableBackupDirPath = new Path(targetTableBackupDir);
      FileSystem outputFs =
          FileSystem.get(targetTableBackupDirPath.toUri(), conn.getConfiguration());
      if (outputFs.exists(targetTableBackupDirPath)) {
        throw new IOException("Target backup directory " + targetTableBackupDir
            + " exists already.");
      }
    }
    
    然后，检查表是否存在，有可能已经被删除了！如果是增量的话，那么就把不存在的表排除掉，只备份存在的表，如果是全量的话，那么就报错，不允许备份不存在的表！
    ArrayList<TableName> nonExistingTableList = null;
    try (Admin admin = conn.getAdmin();) {
      for (TableName tableName : tableList) {
        if (!admin.tableExists(tableName)) {
          if (nonExistingTableList == null) {
            nonExistingTableList = new ArrayList<>();
          }
          nonExistingTableList.add(tableName);
        }
      }
    }
    if (nonExistingTableList != null) {
      if (type == BackupType.INCREMENTAL) {
        // Update incremental backup set
        tableList = excludeNonExistingTables(tableList, nonExistingTableList);
      } else {
        // Throw exception only in full mode - we try to backup non-existing table
        throw new IOException("Non-existing tables found in the table list: "
            + nonExistingTableList);
      }
    }
  }

  // update table list
  BackupRequest.Builder builder = new BackupRequest.Builder();
  request =
      builder.withBackupType(request.getBackupType()).withTableList(tableList)
          .withTargetRootDir(request.getTargetRootDir())
          .withBackupSetName(request.getBackupSetName()).withTotalTasks(request.getTotalTasks())
          .withBandwidthPerTasks((int) request.getBandwidth()).build();

#这里会生成不同的TableBackupClient，如果是增量，对应IncrementalTableBackupClient，如果是全量，对应FullTableBackupClient：
  TableBackupClient client = null;
  try {
    client = BackupClientFactory.create(conn, backupId, request);
  } catch (IOException e) {
    LOG.error("There is an active session already running");
    throw e;
  }

  client.execute();

  return backupId;
}

private List<TableName> excludeNonExistingTables(List<TableName> tableList,
    List<TableName> nonExistingTableList) {

  for (TableName table : nonExistingTableList) {
    tableList.remove(table);
  }
  return tableList;
}

@Override
public void mergeBackups(String[] backupIds) throws IOException {
  try (final BackupMetaTable sysTable = new BackupMetaTable(conn);) {
    checkIfValidForMerge(backupIds, sysTable);
    //TODO run job on remote cluster
    BackupMergeJob job = BackupRestoreFactory.getBackupMergeJob(conn.getConfiguration());
    job.run(backupIds);
  }
}

BackupClientFactory类：
public static TableBackupClient create (Connection conn, String backupId, BackupRequest request)
    throws IOException
  {
    ......
    BackupType type = request.getBackupType();
    if (type == BackupType.FULL) {
      return new FullTableBackupClient(conn, backupId, request);
    } else {
      return new IncrementalTableBackupClient(conn, backupId, request);
    }
  }
```



全量备份：

- FullTableBackupClient

有两个类可以对元数据进行操作：BackupMetaTable，这个是DAO，直接操作HBase，另外一个是BackupManager，这个是Controller，进行备份的逻辑操作！BackupManager构造函数里面就new了一个BackupMetaTable！

```
首先看构造函数：
  public FullTableBackupClient(final Connection conn, final String backupId, BackupRequest request)
      throws IOException {
      这里只调用了父类的构造函数
    super(conn, backupId, request);
  }

public TableBackupClient(final Connection conn, final String backupId, BackupRequest request)
    throws IOException {
    父类的构造函数进行了初始化!
  init(conn, backupId, request);
}

public void init(final Connection conn, final String backupId, BackupRequest request)
    throws IOException
{
 
 #注意这里的BackupManager，这里所有关于备份的业务逻辑都在这里，主要是一个BackUpInfo
 要单独分析这个类！！
  if (request.getBackupType() == BackupType.FULL) {
    backupManager = new BackupManager(conn, conn.getConfiguration());
  } else {
    backupManager = new IncrementalBackupManager(conn, conn.getConfiguration());
  }
  this.backupId = backupId;
  this.tableList = request.getTableList();
  this.conn = conn;
  this.conf = conn.getConfiguration();
  this.fs = FSUtils.getCurrentFileSystem(conf);
  
  这里就是简单new了一个BackupInfo对象，所有关于备份的信息都存储在这个对象里面了！
  
  backupInfo =
      backupManager.createBackupInfo(backupId, request.getBackupType(), tableList,
        request.getTargetRootDir(), request.getTotalTasks(), request.getBandwidth());
  if (tableList == null || tableList.isEmpty()) {
    this.tableList = new ArrayList<>(backupInfo.getTables());
  }
  // Start new session
  backup:system表写入rowkey：“activesession:”，cf为：session，列名为'c'（业务含义为ACTIVE_SESSION_COL），值为yes的一个Put，标识有一个备份在进行，就是简单一个yes来标记，没有记录backupId和表名等信息。startBackupExclusiveOperation里面调用了checkAndPut，首先检查这个标记，如果已经存在，只有是NO的时候才会置为Yes，否则就是别人再跑，抛出异常，然后startBackupSession里面会捕捉这个异常，如果发生这类异常，那么就会等待hbase.backup.exclusive.op.timeout.seconds这么多秒，如果还是变不成Yes，那就抛出异常了，不允许执行！
  
  这里之所以检查，可能是为了不同动作的互斥，因为这里互斥的力度太粗，没有表，没有backupId，那就说明可能是为了防止在merge或者store的时候进行备份动作！上述连接是错误的，看下面解释！
  对应finishBackupExclusiveOperation会把YES支撑NO，delete/repair或者backupManager类finishBackupSession会调用finishBackupExclusiveOperation方法，只有父类TableBackupClient的 completeBackup/failBackup会调用finishBackupSession，所以这个标记就是为了防止多个BackUp同时跑，如果同时跑，那么就要等待一定时间！
  backupManager.startBackupSession();
}

backupManager类：
  public void startBackupExclusiveOperation() throws IOException {
    if (LOG.isDebugEnabled()) {
      LOG.debug("Start new backup exclusive operation");
    }
    try (Table table = connection.getTable(tableName)) {
      Put put = createPutForStartBackupSession();
      // First try to put if row does not exist
      if (!table.checkAndPut(ACTIVE_SESSION_ROW, SESSIONS_FAMILY, ACTIVE_SESSION_COL, null, put)) {
        // Row exists, try to put if value == ACTIVE_SESSION_NO
        if (!table.checkAndPut(ACTIVE_SESSION_ROW, SESSIONS_FAMILY, ACTIVE_SESSION_COL,
          ACTIVE_SESSION_NO, put)) {
          throw new ExclusiveOperationException();        }
      }
    }
  }



public void execute() throws IOException {
    try (Admin admin = conn.getAdmin();) {

      // Begin BACKUP
      beginBackup(backupManager, backupInfo);
      String savedStartCode = null;
      boolean firstBackup = false;
      // do snapshot for full table backup

     获取rowkey为：startcode:${ROOT}，cf=meta的列
        * Read the last backup start code (timestamp) of last successful backup. Will return null if
   * there is no start code stored on hbase or the value is of length 0. These two cases indicate
   * there is no successful backup completed so far.
   * @param backupRoot directory path to backup destination
   看HBase的注释，读取最近一次备份成功的pStartCode(时间戳），如果没有，或者长度为0，说明，迄今未回，还没有成功备份过数据(到这个目录！)
   
   是不是第一次运行全量备份，是通过StartCode来判断的！

      savedStartCode = backupManager.readBackupStartCode();
      firstBackup = savedStartCode == null || Long.parseLong(savedStartCode) == 0L;
      if (firstBackup) {
        // This is our first backup. Let's put some marker to system table so that we can hold the logs
        // while we do the backup.
        
        这里就是把rowkey为：startcode:${ROOT}，cf=meta的列置为0；
        注意后面还会写一次，记录的是regionserver的log的最小时间
        backupManager.writeBackupStartCode(0L);
      }
      // We roll log here before we do the snapshot. It is possible there is duplicate data
      // in the log that is already in the snapshot. But if we do it after the snapshot, we
      // could have data loss.
      // A better approach is to do the roll log on each RS in the same global procedure as
      // the snapshot.
      LOG.info("Execute roll log procedure for full backup ...");

    #这里执行roll log的Procedure，这里会重点分析
      Map<String, String> props = new HashMap<String, String>();
      props.put("backupRoot", backupInfo.getBackupRootDir());
      admin.execProcedure(LogRollMasterProcedureManager.ROLLLOG_PROCEDURE_SIGNATURE,
        LogRollMasterProcedureManager.ROLLLOG_PROCEDURE_NAME, props);

      newTimestamps = backupManager.readRegionServerLastLogRollResult();
      if (firstBackup) {
        // Updates registered log files
        // We record ALL old WAL files as registered, because
        // this is a first full backup in the system and these
        // files are not needed for next incremental backup
        List<String> logFiles = BackupUtils.getWALFilesOlderThan(conf, newTimestamps);
        backupManager.recordWALFiles(logFiles);
      }

      // SNAPSHOT_TABLES:
      backupInfo.setPhase(BackupPhase.SNAPSHOT);
      for (TableName tableName : tableList) {
        String snapshotName =
            "snapshot_" + Long.toString(EnvironmentEdgeManager.currentTime()) + "_"
                + tableName.getNamespaceAsString() + "_" + tableName.getQualifierAsString();

        snapshotTable(admin, tableName, snapshotName);
        backupInfo.setSnapshotName(tableName, snapshotName);
      }

      // SNAPSHOT_COPY:
      // do snapshot copy
      LOG.debug("snapshot copy for " + backupId);
      snapshotCopy(backupInfo);
      // Updates incremental backup table set
      backupManager.addIncrementalBackupTableSet(backupInfo.getTables());

      // BACKUP_COMPLETE:
      // set overall backup status: complete. Here we make sure to complete the backup.
      // After this checkpoint, even if entering cancel process, will let the backup finished
      backupInfo.setState(BackupState.COMPLETE);
      // The table list in backupInfo is good for both full backup and incremental backup.
      // For incremental backup, it contains the incremental backup table set.
      backupManager.writeRegionServerLogTimestamp(backupInfo.getTables(), newTimestamps);

      HashMap<TableName, HashMap<String, Long>> newTableSetTimestampMap =
          backupManager.readLogTimestampMap();

#
      Long newStartCode =
          BackupUtils.getMinValue(BackupUtils
              .getRSLogTimestampMins(newTableSetTimestampMap));
      backupManager.writeBackupStartCode(newStartCode);

      // backup complete
      completeBackup(conn, backupInfo, backupManager, BackupType.FULL, conf);
    } catch (Exception e) {
      failBackup(conn, backupInfo, backupManager, e, "Unexpected BackupException : ",
        BackupType.FULL, conf);
      throw new IOException(e);
    }

  }


  protected void snapshotTable(Admin admin, TableName tableName, String snapshotName)
      throws IOException {

    int maxAttempts =
        conf.getInt(BACKUP_MAX_ATTEMPTS_KEY, DEFAULT_BACKUP_MAX_ATTEMPTS);
    int pause =
        conf.getInt(BACKUP_ATTEMPTS_PAUSE_MS_KEY, DEFAULT_BACKUP_ATTEMPTS_PAUSE_MS);
    int attempts = 0;

    while (attempts++ < maxAttempts) {
      try {
        admin.snapshot(snapshotName, tableName);
        return;
      } catch (IOException ee) {
        LOG.warn("Snapshot attempt " + attempts + " failed for table " + tableName
            + ", sleeping for " + pause + "ms", ee);
        if (attempts < maxAttempts) {
          try {
            Thread.sleep(pause);
          } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            break;
          }
        }
      }
    }
    throw new IOException("Failed to snapshot table "+ tableName);
  }
```

LogRollMasterProcedureManager重要的一步就是把LogRoll掉，这一步怎么做到的呢？

首先，我们启用备份的时候是需要配置几个选项的：

```
<property>
  <name>hbase.backup.enable</name>
  <value>true</value>
</property>
<property>
  <name>hbase.master.logcleaner.plugins</name>
  <value>org.apache.hadoop.hbase.backup.master.BackupLogCleaner,...</value>
</property>
<property>
  <name>hbase.procedure.master.classes</name>
  <value>org.apache.hadoop.hbase.backup.master.LogRollMasterProcedureManager,...</value>
</property>
<property>
  <name>hbase.procedure.regionserver.classes</name>
  <value>org.apache.hadoop.hbase.backup.regionserver.LogRollRegionServerProcedureManager,...</value>
</property>
<property>
  <name>hbase.coprocessor.region.classes</name>
  <value>org.apache.hadoop.hbase.backup.BackupObserver,...</value>
</property>
<property>
  <name>hbase.master.hfilecleaner.plugins</name>
  <value>org.apache.hadoop.hbase.backup.BackupHFileCleaner,...</value>
</property>
```

我们重点跟进LogRollMasterProcedureManager，LogRollRegionServerProcedureManager







```
public class MasterProcedureManagerHost extends
    ProcedureManagerHost<MasterProcedureManager> {

  private Hashtable<String, MasterProcedureManager> procedureMgrMap = new Hashtable<>();

  @Override
  public void loadProcedures(Configuration conf) {
    loadUserProcedures(conf, MASTER_PROCEDURE_CONF_KEY);
    for (MasterProcedureManager mpm : getProcedureManagers()) {
      procedureMgrMap.put(mpm.getProcedureSignature(), mpm);
    }
  }
  
   public static final String ROLLLOG_PROCEDURE_SIGNATURE = "rolllog-proc";
  @Override
  public String getProcedureSignature() {
    return ROLLLOG_PROCEDURE_SIGNATURE;
  }
```



```
public class RegionServerProcedureManagerHost extends
    ProcedureManagerHost<RegionServerProcedureManager> {

  private static final Logger LOG = LoggerFactory
      .getLogger(RegionServerProcedureManagerHost.class);

  public void initialize(RegionServerServices rss) throws KeeperException {
    for (RegionServerProcedureManager proc : procedures) {
      LOG.debug("Procedure {} initializing", proc.getProcedureSignature());
      proc.initialize(rss);
      LOG.debug("Procedure {} initialized", proc.getProcedureSignature());
    }
  }
  ......

  @Override
  public void loadProcedures(Configuration conf) {
    loadUserProcedures(conf, REGIONSERVER_PROCEDURE_CONF_KEY);
    // load the default snapshot manager
    procedures.add(new RegionServerSnapshotManager());
    // load the default flush region procedure manager
    procedures.add(new RegionServerFlushTableProcedureManager());
  }


org.apache.hadoop.hbase.backup.regionserver.LogRollRegionServerProcedureManager

  @Override
  public String getProcedureSignature() {
    return "backup-proc";
  }
}
```





```
public class HRegionServer extends HasThread implements
    RegionServerServices, LastSequenceId, ConfigurationObserver {
    
    ......
    
    private RegionServerProcedureManagerHost rspmHost;
    
     private void initializeZooKeeper() throws IOException, InterruptedException {
 ...
 try {
      rspmHost = new RegionServerProcedureManagerHost();
      rspmHost.loadProcedures(conf);
      rspmHost.initialize(this);
    } catch (KeeperException e) {
      this.abort("Failed to reach coordination cluster when creating procedure handler.", e);
    }
 
 }
 
 
 public class HMaster extends HRegionServer implements MasterServices {
private MasterProcedureManagerHost mpmHost;
 void initializeZKBasedSystemTrackers() throws IOException,
      InterruptedException, KeeperException {
   ......
   this.mpmHost = new MasterProcedureManagerHost();
    this.mpmHost.register(this.snapshotManager);
    this.mpmHost.register(new MasterFlushTableProcedureManager());
    this.mpmHost.loadProcedures(conf);
    this.mpmHost.initialize(this, this.metricsMaster);
  }
```



```
MasterProcedureManager的注释
```

```
/**
* A life-cycle management interface for globally barriered procedures on master.
* See the following doc on details of globally barriered procedure:
* https://issues.apache.org/jira/secure/attachment/12555103/121127-global-barrier-proc.pdf
*
* To implement a custom globally barriered procedure, user needs to extend two classes:
* {@link MasterProcedureManager} and {@link RegionServerProcedureManager}. Implementation of
* {@link MasterProcedureManager} is loaded into {@link org.apache.hadoop.hbase.master.HMaster}
* process via configuration parameter 'hbase.procedure.master.classes', while implementation of
* {@link RegionServerProcedureManager} is loaded into
* {@link org.apache.hadoop.hbase.regionserver.HRegionServer} process via
* configuration parameter 'hbase.procedure.regionserver.classes'.
*
* An example of globally barriered procedure implementation is
* {@link org.apache.hadoop.hbase.master.snapshot.SnapshotManager} and
* {@link org.apache.hadoop.hbase.regionserver.snapshot.RegionServerSnapshotManager}.
*
* A globally barriered procedure is identified by its signature (usually it is the name of the
* procedure znode). During the initialization phase, the initialize methods are called by both
* {@link org.apache.hadoop.hbase.master.HMaster}
* and {@link org.apache.hadoop.hbase.regionserver.HRegionServer} which create the procedure znode
* and register the listeners. A procedure can be triggered by its signature and an instant name
* (encapsulated in a {@link ProcedureDescription} object). When the servers are shutdown,
* the stop methods on both classes are called to clean up the data associated with the procedure.
*/
```





主要的类：

org.apache.hadoop.hbase.backup.regionserver.LogRollBackupSubprocedure#LogRollBackupSubprocedure





ROllLog的最终输出：

1.Log roll掉

2.写metatable，rslogts：${Root}${server},列名：meta:rs-log-ts,值是WAL的最大的时间戳那个timestamp