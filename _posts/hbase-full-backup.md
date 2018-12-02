```
/**
 * This class provides API to access backup meta table<br>
 *
 * Backup meta table schema:<br>
 * <p><ul>
 * <li>1. Backup sessions rowkey= "session:"+backupId; value =serialized BackupInfo</li>
 * <li>2. Backup start code rowkey = "startcode:"+backupRoot; value = startcode</li>
 * <li>3. Incremental backup set rowkey="incrbackupset:"+backupRoot; value=[list of tables]</li>
 * <li>4. Table-RS-timestamp map rowkey="trslm:"+backupRoot+table_name;
 * value = map[RS-> last WAL timestamp]</li>
 * <li>5. RS - WAL ts map rowkey="rslogts:"+backupRoot +server; value = last WAL timestamp</li>
 * <li>6. WALs recorded rowkey="wals:"+WAL unique file name;
 * value = backupId and full WAL file name</li>
 * </ul></p>
 */
```

备份元数据表：backup:system 

备份的阶段：

```
/**
 * BackupPhase - phases of an ACTIVE backup session (running), when state of a backup session is
 * BackupState.RUNNING
 */
public static enum BackupPhase {
  REQUEST, SNAPSHOT, PREPARE_INCREMENTAL, SNAPSHOTCOPY, INCREMENTAL_COPY, STORE_MANIFEST;
}
```

1.CreateCommand



首先调用基类的execute函数：

org.apache.hadoop.hbase.backup.impl.BackupCommands.Command#execute



- requiresNoActiveSession：



这个函数里面上来会判断是否需要requiresNoActiveSession，即只能运行一个活跃的会话，只有三个类改写了这个函数：

CreateCommand

DeleteCommand

和MergeCommand

也就是说在创建，删除和Merge时，是不能同时跑多个会话的，其他的都可以。



检查的逻辑是：

在backup:system 表中扫描所有的"session:"的key，然后反序列化为BackupInfo对象，判断状态：

如果是BackupState.ANY 或者是BackupState.RUNNING状态

- requiresConsistentState

CreateCommand和MergeCommand需要检查，检查的逻辑是：

rowkey为：delete_op_row，cf为meta

rowkey为：merge_op_row，cf为meta

就是删除和合并的时候，也也不能有失败的行为；如果以前有失败的，那么也不能进行下一次的合并或者删除了

