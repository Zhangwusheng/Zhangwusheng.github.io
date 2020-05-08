# Streaming压测方案

主要是为了分析日志分析程序各个环节的最大处理能力，对系统性能有深入了解。



## 1.资源情况：

### 1.1 总体资源

- 33个Nodemanager，
- 1254个VCore，
- 6.96 TB 内存

其中ETL队列配置如下：

- Absolute Used Capacity: 	16.1%
- Absolute Configured Capacity: 	30.0% 

总共可用2T内存

### 1.2 资源使用情况

streaming占用了30%，即可用2T内存，目前两个streaming占用了一半的内存，即1T内存左右
其中

- CDN的配置如下：

```json
  "spark.executor.cores": "4",
  "spark.executor.instances": "40",
  "spark.executor.memory": "8g",
  "spark.executor.memoryOverhead": "20g",
  "spark.streaming.kafka.maxRatePerPartition": "15000",
  "spark.sql.shuffle.partitions": "40",
```

- 对象存储的配置如下：

```
  "spark.executor.cores": "1",
  "spark.executor.instances": "5",
  "spark.executor.memory": "3g",
  "spark.executor.memoryOverhead": "2g",
  "spark.sql.shuffle.partitions": "5",
```

### 1.3 测试资源分配

从目前的使用情况看， 可以使用ETL队列剩余资源进行同等数据量的测试。
***配置和CDN目前一样***



## 2.压测程序开发

### 2.1 Kafka

开发新的数据生成程序，用于从Kafka读取数据，写入测试的队列

### 2.2 分析程序

计划在cdn-log-analysis master的基础上，拉一个perf分支出来，性能测试相关的，在perf基础上进行修改



## 3.程序部署

1. 按照开发环境的模式，新部署一套程序，不同于原来开发环境的是，可以不用新增用户，因为机器数够用，所以可以挑选其他机器，使用cdnlog用户部署即可。这样队列不用重新配置权限。
2. 程序部署到指定机器的目录
3. 修改配置：
   1. 程序stream的名称
   2.  hive的输出
   3.  hbase的输出。
4. 屏蔽如下输出(如果有)：
   1. kafka的通知
   2. zk的通知

## 4.测试步骤

> 目前程序的主要逻辑有：
>
> ***第零步***：从Kafka加载数据
>
> 第一步：ConsumerRecordToOriginalRow进行数据解析
>
> 第二步：CorrectLogFilter数据过滤（耗时比较少）
>
> 第三步：originalDataSet.write().parquet(originalPath);保存原始数据
>
> 第四步：业务处理OriToBaseMapFunction（耗时比较少）
>
> 第五步：Dataset<Row> outputDataSet = spark.sql生成汇总统计数据
>
> 第六步：汇总数据写入hive表

测试思路：首先摸清楚每一个主要的耗时步骤的耗时，以及最大的吞吐，主要是看

1. 最大能从Kafka读取多少数据
2. 落盘耗时，占五分钟的比例
3. 消费能否跟得上生产的速度

上述数据有的从SparkUI能看到耗时，但是是和运算耦合在一起的，可以单独评估一下耗时。



测试步骤：

1. 使用新的压测程序，产生压测数据

2.    编写新的map函数，只统计读取的记录数，设置
      
      ```
      spark.streaming.backpressure.enabled=true
      spark.streaming.receiver.maxRate unset
      spark.streaming.kafka.maxRatePerPartition unset
      ```
      
      这样利用spark自己的背压设置看看系统最大能读取多少kafka的数据
      
      这样利用spark自己的背压设置看看系统最大能读取多少kafka的数据
      
      此处对应***第零步***
      
3. 在ConsumerRecordToOriginalRow map增加一个action，比如count，评估一下数据解析的耗时

4. 跟踪保存原始数据的耗时

5. sql运行完毕后，增加一个action，查看sql的耗时

6. 保存到hive后，跟踪这个action的耗时



第二步的spark.streaming.backpressure.enabled的含义如下：

> Enables or disables Spark Streaming's internal backpressure mechanism (since 1.5).    This enables the Spark Streaming to control the receiving rate based on the    current batch scheduling delays and processing times so that the system receives    only as fast as the system can process. Internally, this dynamically sets the    maximum receiving rate of receivers. This rate is upper bounded by the values    `spark.streaming.receiver.maxRate` and `spark.streaming.kafka.maxRatePerPartition`    if they are set (see below).  



## 5.迭代测试

1. 调整executor的数量与内存占用数，对测试数据分析和性能进行系统调优，查看效果
2. 调整测试数据的分布，增加汇总维度的值的多样性，查看程序性能



# Kylin压测方案

待补充