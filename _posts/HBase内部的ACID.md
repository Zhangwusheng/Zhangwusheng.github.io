https://blog.csdn.net/u010010428/article/details/51732270

偶然看到的一篇文章，里面不只是阐述了某一个问题，而是对ACID在HBase的各个组件的应用情况作了详细的说明，所以有必要翻译出来，整理一下。

​        众所周知，ACID，即指：原子性(Atomicity)，一致性(Consistency)，隔离性(Isolation)，持久性(Durability)。
​        HBase 支持特定场景下的 ACID，即当对同一行进行 Put 操作时保证完全的 ACID(HBASE-3584增加了多操作事务，HBASE-5229增加了多行事务，但原理是一样的)
​        那么 HBase 内部的 ACID 是怎么样实现的呢？
​        HBase 实现了一种 MVCC，并且 HBase 没有混合读写事务。
​       由于历史的原因，HBase 的命名有点奇怪。每个 RegionServer 拥有严格地单调递增的事务号。
​       当一个写事务(一组 puts 或 deletes)开始时，该事务获取下一个最大的事务号，在 HBase 内叫做 WriteNumber。
​       当一个读事务(一个 scan 或 get)开始时，该事务获取先前最新提交事务的事务号，在 HBase 内叫做 ReadPoint。
​       每个新创建的 KeyValue 对象用它所在事务的 WriteNumber 标记(由于历史的原因，这个标记在 HBase 内叫做 memstore timestamp，注意这个要和我们常说的时间戳区分开)。
​       

​       宏观地，HBase 写事务的流程是这样的：
​       对行(一行或多行)加锁，屏蔽对相同行的并发写；
​       获取当前的 WriteNumber；
​       提交修改到 WAL；
​       提交修改到 Memstore(用前面获取的 WriteNumber 标记修改的 KeyValues)；
​       提交事务，也就是把 ReadPoint 更新为当前获取的 WriteNumber；
​       释放行(一行或多行)锁。


​       宏观地，HBase 读事务的流程是这样的：
​       打开 scanner；
​       获取当前的 ReadPoint；
​       用获取的标记memstore timestamp即ReadPoint 过滤所有扫描到的 KeyValues，只看 ReadPoint 之前的；
​       关闭 scanner(scanner 由客户端初始化)。
​       实际在实现的时候会比上面说的复杂，但是上述也足够说明问题。注意，reader 在读的过程中是完全不加锁的，但是我们依旧保证了 ACID。
​       需要注意的是：上述的机制只有在事务严格顺序提交的情况下管用。否则的话，一个先开始却未提交的事务将会对一个后开始先提交的事务可见（破坏了隔离性）。但是，HBase 中的事务一般都很短，所以这不是个问题。
​       HBase 确实实现了：所有事务顺序提交。
​       HBase 中提交一个事务，意味着将当前的的 ReadPoint 更新为该事务的 WriteNumber，这样就将事务提交的更改对所有新的 scan 可见。

​       HBase 维护一个未完成事务的列表，一个事务的提交会被推迟，直到先前的事务提交。注意：HBase 可以支持并发、所有的修改立即生效，只是提交的时候是顺序的。
​       由于 HBase 不保证任何 Region 之间(每个 Region 只保存在一个 Region Server 上)的一致性，故 MVCC 的数据结果只需保存在每个 RegionServer 各自的内存中。
​       下一个有趣的事儿，在 compaction 期间发生了什么？
​       HBase 的 Compaction 过程，通常将多个小的 store 文件(将 memstore flush 到磁盘时产生)合并成一个大点儿的，并在合并过程中移除垃圾。这里的"垃圾"要么是寿命超过了列族的 TTL(Time-To-Live)或 VERSIONS 设置、要么是被标记删除的那些 KeyValues。
​       假设在一个 scanner 扫描 KeyValues 过程中发生了 Compaction，scanner 可能会看到一个不完整的行，即该行数据不可能从任何一种顺序事务调度得到，即数据发生了不一致。
​       HBase 的方案是跟踪所有打开的 scanner 使用的 ReadPoint 中最早的一个，然后滤掉所有大于该 ReadPoint 的 KeyValues。这一逻辑连同其它的优化在HBASE-2856中增加进来，这一补丁后，允许 HBase 在并发 flush 的场景下保证 ACID。
​       HBASE-5569 为 delete marker 实现了同样的逻辑，HBase 是标记删除的，故实现了并发删除的 ACID。
​       最后注意，当一个 KeyValue 的 memstore timestamp 比最老的scanner(实际是 scanner 持有的 ReadPoint)还要老时，会被清零(置为0)，这样该 KeyValue会对所有的 scanner 可见，当然，此时比该 KeyValue 原 memstore timestamp 更早的 scanner 都已经结束了。
​       额外的几点：
​       即使写事务失败了，ReadPoint 也会被更新，以避免阻拦后面等待提交的事务(从实现上说，其实是同一个过程，没什么特别的处理，更新 ReadPoint 的代码写在 Java 代码final{}语句块内)。
​       更新写入到 WAL 后，所有的修改都只创建了一条记录(record)，没有单独的 commit record。
​       当一台 RegionServer 挂掉，如果 WAL 已经完整写入，所有执行中的事务可以重放日志以恢复，如果 WAL 未写完，则未完成的事务会丢掉(相关的数据也丢失了)。