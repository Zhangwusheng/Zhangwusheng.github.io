

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

