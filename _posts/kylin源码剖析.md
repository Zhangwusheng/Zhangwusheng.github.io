---
layout:     post
title:     Ambari安装HDP3.0.0
subtitle:   用Ambari2.7安装HDP3.0.0
date:       2018-09-22
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - Kylin
    - CUBE
    - HBASE
typora-copy-images-to: ..\img
typora-root-url: ..
---

# Kylin源码分析系列【[zengrui_ops](https://me.csdn.net/zengrui_ops)】

备注：来自CSDN系列

https://blog.csdn.net/zengrui_ops/article/details/85858860

## 一.任务调度

注：Kylin源码分析系列基于Kylin的2.5.0版本的源码，其他版本可以类比。

### 1.1. 相关介绍

Kylin在Web上触发Cube的相关操作后并不是马上执行相关的操作，而是将构建的任务提交到任务调度服务，任务调度服务每隔一段时间会将提交了未执行的job进行调度执行，默认是30s调度一次，可根据配置项kylin.job.scheduler.poll-interval-second来配置调度时间间隔。
    
任务调度服务的服务类为JobService，包路径：org.apache.kylin.rest.service.JobService。JobService是通过实现InitializingBean接口，继而实现afterPropertiesSet的方法 ，然后通过配置spring加载bean的方式被初始化的；具体是通过配置文件来装配bean的，涉及到的配置文件有：在./tomcat/webapps/kylin/WEB-INF/web.xml中引入了./tomcat/webapps/kylin/WEB-INF/classes/applicationContext.xml，然后在applicationContext.xml中配置有：

```java
<context:component-scan base-package="org.apache.kylin.rest"/>
```

然后spring去扫描目录org.apache.kylin.rest下的标有@Component的类，并注册成bean。由于JobService是通过实现InitializingBean接口，继而实现afterPropertiesSet的方法来初始化bean的，所以在JobService这个bean被初始化的时候，afterPropertiesSet会被调用执行，继而实现JobService的初始化，kylin中的其他服务也是这要被初始化的。

### 1.2. 源码分析

任务调度服务初始化：

```java
public void afterPropertiesSet() throws Exception {
    String timeZone = getConfig().getTimeZone();
    TimeZone tzone = TimeZone.getTimeZone(timeZone);
    TimeZone.setDefault(tzone);
    final KylinConfig kylinConfig = KylinConfig.getInstanceFromEnv(); 
 
    //获取配置的任务调度器，默认为org.apache.kylin.job.impl.threadpool.DefaultScheduler
 
    final Scheduler<AbstractExecutable> scheduler = (Scheduler<AbstractExecutable>) SchedulerFactory.scheduler(kylinConfig.getSchedulerType());
    new Thread(new Runnable() {
        @Override
        public void run() {
            try {
                //调度服务初始化
                scheduler.init(new JobEngineConfig(kylinConfig), new ZookeeperJobLock());
                if (!scheduler.hasStarted()) {
                    logger.info("scheduler has not been started");
                }
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }
    }).start();
 
    Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {
        @Override
        public void run() {
            try {
                scheduler.shutdown();
            } catch (SchedulerException e) {
                logger.error("error occurred to shutdown scheduler", e);
            }
        }
    }));
}
```

 

Kylin的任务调度器有三种：

    public Map<Integer, String> getSchedulers() {
        Map<Integer, String> r = Maps.newLinkedHashMap();
        r.put(0, "org.apache.kylin.job.impl.threadpool.DefaultScheduler");
        r.put(2, "org.apache.kylin.job.impl.threadpool.DistributedScheduler");
        r.put(77, "org.apache.kylin.job.impl.threadpool.NoopScheduler");
        r.putAll(convertKeyToInteger(getPropertiesByPrefix("kylin.job.scheduler.provider.")));
        return r;
    }

通过配置项kylin.job.scheduler.default来配置，默认配置为0，即为DefaultScheduler，下面回到任务调度服务的初始化，调用DefaultScheduler的init方法：

    public synchronized void init(JobEngineConfig jobEngineConfig, JobLock lock) throws SchedulerException {
     
        jobLock = lock;
        String serverMode = jobEngineConfig.getConfig().getServerMode();
        //只有服务模式为job和all的需要运行任务调度服务，query不需要
        if (!("job".equals(serverMode.toLowerCase()) || "all".equals(serverMode.toLowerCase()))) {
            logger.info("server mode: " + serverMode + ", no need to run job scheduler");
            return;
     
        }
        logger.info("Initializing Job Engine ....");
     
        if (!initialized) {
            initialized = true;
        } else {
            return;
        }
     
        this.jobEngineConfig = jobEngineConfig;
     
        if (jobLock.lockJobEngine() == false) {
            throw new IllegalStateException("Cannot start job scheduler due to lack of job lock");
        }
        executableManager = ExecutableManager.getInstance(jobEngineConfig.getConfig());
     
        //load all executable, set them to a consistent status
        fetcherPool = Executors.newScheduledThreadPool(1);
        int corePoolSize = jobEngineConfig.getMaxConcurrentJobLimit();
        jobPool = new ThreadPoolExecutor(corePoolSize, corePoolSize, Long.MAX_VALUE, TimeUnit.DAYS,
                new SynchronousQueue<Runnable>());
        context = new DefaultContext(Maps.<String, Executable> newConcurrentMap(), jobEngineConfig.getConfig());
        logger.info("Staring resume all running jobs.");
        executableManager.resumeAllRunningJobs();
        logger.info("Finishing resume all running jobs.");
     
        //获取调度时间间隔，
        int pollSecond = jobEngineConfig.getPollIntervalSecond();
        logger.info("Fetching jobs every {} seconds", pollSecond);
        JobExecutor jobExecutor = new JobExecutor() {
     
            @Override
            public void execute(AbstractExecutable executable) {
     
                jobPool.execute(new JobRunner(executable));
            }
     
        };
        //判断任务调度是否考虑优先级，默认不考虑，即使用DefaultFetcherRunner
        fetcher = jobEngineConfig.getJobPriorityConsidered()
                ? new PriorityFetcherRunner(jobEngineConfig, context, executableManager, jobExecutor)
                : new DefaultFetcherRunner(jobEngineConfig, context, executableManager, jobExecutor);
        logger.info("Creating fetcher pool instance:" + System.identityHashCode(fetcher));
     
        //每隔pollSecond去获取一次任务
        fetcherPool.scheduleAtFixedRate(fetcher, pollSecond / 10, pollSecond, TimeUnit.SECONDS);
        hasStarted = true;
     
    }

下面间隔性的执行DefaultFetcherRunner的run方法：

    synchronized public void run() {
     
        try (SetThreadName ignored = new SetThreadName(//
                "FetcherRunner %s", System.identityHashCode(this))) {//
            // logger.debug("Job Fetcher is running...");
            Map<String, Executable> runningJobs = context.getRunningJobs();
            // 任务调度池是否满了，默认只能同时执行10个job
            if (isJobPoolFull()) {
                return;
            }
            ......
            //获取索引的job
            for (final String id : executableManager.getAllJobIds()) {
                ......
                //根据任务id获取具体的任务
                final AbstractExecutable executable = executableManager.getJob(id);
                ......
                //添加任务到任务调度池
                addToJobPool(executable, executable.getDefaultPriority());
            }
          ......
        }
    }

主要看下是从哪获取到的所有的job，上面是调用executableManager.getAllJobIds()来获取所有的任务id的，下面看下这个函数：

    public List<String> getJobIds() throws PersistentException {
     
        try {
            NavigableSet<String> resources = store.listResources(ResourceStore.EXECUTE_RESOURCE_ROOT);
            if (resources == null) {
                return Collections.emptyList();
            }
     
            ArrayList<String> result = Lists.newArrayListWithExpectedSize(resources.size());
            for (String path : resources) {
                result.add(path.substring(path.lastIndexOf("/") + 1));
            }
            return result;
        } catch (IOException e) {
            logger.error("error get all Jobs:", e);
            throw new PersistentException(e);
        }
    }

store.listResources 到存储kylin元数据的数据库获取以“/execute”开始的元数据条目，然后截取出任务的id，接着调用executableManager.getJob(id)来获取具体的任务信息，依然是到存储kylin元数据的数据库中获取，数据库中的任务的元数据条目如下所示（使用的hbase存储的元数据）：

![20190105161719150](/img/20190105161719150.png)

最后调用addToJobPool将任务添加到任务调度池：

```java
protected void addToJobPool(AbstractExecutable executable, int priority) {
 
    String jobDesc = executable.toString();
    logger.info(jobDesc + " prepare to schedule and its priority is " + priority);
    try {
        context.addRunningJob(executable);
        //提交任务到调度池中执行
        jobExecutor.execute(executable);
        logger.info(jobDesc + " scheduled");
    } catch (Exception ex) {
        context.removeRunningJob(executable);
        logger.warn(jobDesc + " fail to schedule", ex);
    }
}
```


回到DefaultScheduler中的init函数中的jobExecutor，最终调用JobRunner的run方法来执行任务，主要是调用executable.execute(context)，kylin中的具体任务都是继承类AbstractExecutable，如果重写了execute方法，就调用具体任务的execute方法来执行相应的任务，如果未重写execute方法，则调用AbstractExecutable中的execute方法，然后调用doWork来执行任务，spark的相关任务的任务类型是SparkExecutable，该类继承自AbstractExecutable，自己实现了doWork方法来提交spark任务，spark任务提交运行的主类为SparkEntry，调用main方法，然后调用AbstractApplication的execute方法，最后调用具体任务类的execute方法运行。上面就是kylin中任务调度的相关代码，下面看下任务是怎么提交到任务调度服务的。
    

任务提交最终要调用到JobService中submitJobInternal方法，这个方法中最终调用getExecutableManager().addJob(job)来提交任务（这里的job是一个DefaultChainedExecutable的实例，里面包含各种Executable类型的task），这里的getExecutableManager获取了ExecutableManager的单例，然后调用addJob来提交任务，然后调用executableDao.addJob(parse(executable))，接着调用writeJobResource(pathOfJob(job), job)将job信息序列化后存入元数据数据库表中。



## 二.Cube构建

注：Kylin源码分析系列基于Kylin的2.5.0版本的源码，其他版本可以类比。

### 2.1.构建流程

前面一篇文章介绍了Kylin中的任务调度服务，本篇文章正式介绍Kylin的核心内容Cube，主要讲述Cube构建的过程。下面的构建过程选择使用spark构建引擎来说明（MR引擎自行类比阅读相关源码）。

首先介绍下Cube构建的整体流程，看下kylin web页面上展示的构建过程：

![img](/img/20190105162225580.png)

 

主要有如下几个步骤：

1. 首先创建一个大平表（Flat Hive Table），该表的数据是将创建cube涉及到的维度从原有的事实表和维度表中查询出来组成一条完整的数据插入到一个新的hive表中；后续的cube构建就是基于这个表的。抽取数据的过程使用的是Hive命令，Kylin使用conf/kylin_hive_conf.xml配置文件中的配置项，用户可以根据需求修改和添加相关配置项。
2. 经过第一步后，Hive会在HDFS目录下生成一些数据文件，这些数据文件可能大小不一，这就会导致后续的任务执行不均衡，有些任务执行很快，有些可能会很慢。为了是这些数据分布更均匀，Kylin增加了该步骤来重新分配各个数据文件中的数据。执行如下hive命令：

![img](/img/20190105163842222.png)

3. 接着Kylin获取维度列的distinct值（即维度基数），用于后面一步进行字典编码。

4. 这一步就根据前面获得的维度的distinct值来构建字典，通常这一步会很快，但是如果distinct值的集合很大，Kylin可能会报           错，例如，“Too high cardinality is not suitable for dictionary”。对于UHC（超大维度基数）列，请使用其他编码方式，例             如“fixed_length”，“integer”等。

5. 这步操作很简单，只是保存cube的一些相关统计数据，比如有多少cuboid，每个cuboid有多少行数据等。

6. 这一步是创建保存cube数据的hbase表，目前的版本cube数据只支持保存到hbase中，kylin社区目前正在开发将cube数据直接保存为parquet格式文件（适用于云上环境）；这里有一点需要说明一下，在建表的时候启用了hbase协处理的功能（endpoint模式），需要将协处理器的相关jar包deploy到对应的hbase表上，后面会详细介绍，这样做是为了提升Kylin的查询性能。

7. 这里就是真正的创建cube了，本文的描述是基于spark构建引擎的，使用的by layer的方式构建的，即先构建BaseCuboid，然后一层一层的往上聚合，得到其他的cuboid的数据；当使用MR引擎的时候，可以配置cube构建算法，通过kylin.cube.algorithm来配置，值有[“auto”, “layer”, “inmem”]，默认值为auto，用户根据环境的资源情况来进行配置，使用auto的时候，kylin会根据系统资源情况来选择layer还是inmem，layer算法是一层一层的计算，需要的资源较少，但是花费的时间可能会更长，而使用inmem算法则构建的更快，但是会消耗更多的内存，具体可以参考                                                       https://blog.csdn.net/sunnyyoona/article/details/52318176。

8. 这一步将Cuboid数据转化为HFile文件。

9. 将转化后的HFile文件直接load到HBase里面供后续查询使用。

10. 更新Cube的相关信息。

11. 清理Hive中的临时数据。

### 2.2.源码分析

下面从源码来看Cube的构建过程：

在Kylin页面上点击build后，触发的是一个任务提交的流程，该任务提交的流程简要介绍下：

1.页面点击Submit按钮，通过js触发rebuild事件，发送restful请求：

![img](/img/20190105164311308.png)

 

rebuild的具体处理源码在webapp/app/js/controllers/cubes.js中：

![img](/img/20190105164325735.png)

最终调用restful api接口/kylin/api/cubes/{cubeName}/rebuild将请求发送至服务端，CubeService定义在webapp/app/js/services/cubes.js。

2.Rest Server服务端接收到restful请求，根据请求的URL将请求分发到对应的控制器进行处理(使用了Spring的@Controller和@RequestMapping注解)，这里的Cube构建请求最终被分发到CubeController控制器由rebuild函数进行处理：

```java
/**
 * Build/Rebuild a cube segment
 */
@RequestMapping(value = "/{cubeName}/rebuild", method = { RequestMethod.PUT }, produces = { "application/json" })
@ResponseBody
public JobInstance rebuild(@PathVariable String cubeName, @RequestBody JobBuildRequest req) {
    return buildInternal(cubeName, new TSRange(req.getStartTime(), req.getEndTime()), null, null, null,
            req.getBuildType(), req.isForce() || req.isForceMergeEmptySegment());
}

```

然后看buildInternal函数：

```java
private JobInstance buildInternal(String cubeName, TSRange tsRange, SegmentRange segRange, //
        Map<Integer, Long> sourcePartitionOffsetStart, Map<Integer, Long> sourcePartitionOffsetEnd,
        String buildType, boolean force) {
    try {
        //获取提交任务的用户的用户名
        String submitter = SecurityContextHolder.getContext().getAuthentication().getName();
        //获取Cube实例
        CubeInstance cube = jobService.getCubeManager().getCube(cubeName);
        //检测有多少个处于即将构建的状态的job，默认只能同时提10个job，大于则会抛异常，提交失败
        checkBuildingSegment(cube);
        //通过jobService来提交任务,即为上篇文章介绍的Cube任务调度服务
        return jobService.submitJob(cube, tsRange, segRange, sourcePartitionOffsetStart, sourcePartitionOffsetEnd,
                CubeBuildTypeEnum.valueOf(buildType), force, submitter);
    } catch (Throwable e) {
        logger.error(e.getLocalizedMessage(), e);
        throw new InternalErrorException(e.getLocalizedMessage(), e);
    }
}

```

然后看JobService中的submitJob，该函数只是做了权限认证，然后直接调用了submitJobInternal：

```java
public JobInstance submitJobInternal(CubeInstance cube, TSRange tsRange, SegmentRange segRange, //
        Map<Integer, Long> sourcePartitionOffsetStart, Map<Integer, Long> sourcePartitionOffsetEnd, //
        CubeBuildTypeEnum buildType, boolean force, String submitter) throws IOException {
. . .
        try {
        if (buildType == CubeBuildTypeEnum.BUILD) {
            //获取数据源类型（HiveSource、JdbcSource、KafkaSource）
            ISource source = SourceManager.getSource(cube);
            //数据范围
            SourcePartition src = new SourcePartition(tsRange, segRange, sourcePartitionOffsetStart,
                    sourcePartitionOffsetEnd);
            //kafka数据源确定start offset和endoffset
            src = source.enrichSourcePartitionBeforeBuild(cube, src);
            //添加segment
            newSeg = getCubeManager().appendSegment(cube, src);
            //通过构建引擎来构建Job
            job = EngineFactory.createBatchCubingJob(newSeg, submitter);
        } else if (buildType == CubeBuildTypeEnum.MERGE) {
            newSeg = getCubeManager().mergeSegments(cube, tsRange, segRange, force);
            job = EngineFactory.createBatchMergeJob(newSeg, submitter);
        } else if (buildType == CubeBuildTypeEnum.REFRESH) {
            newSeg = getCubeManager().refreshSegment(cube, tsRange, segRange);
            job = EngineFactory.createBatchCubingJob(newSeg, submitter);
        } else {
            throw new BadRequestException(String.format(msg.getINVALID_BUILD_TYPE(), buildType));
        }
        //提交任务，可以参考前面任务调度的文章了解任务具体是怎么执行的
        getExecutableManager().addJob(job);
    } catch (Exception e) {
      . . . 
    }
    JobInstance jobInstance = getSingleJobInstance(job);
    return jobInstance;
}

```

接着看EngineFactory.createBatchCubingJob方法，根据cube实例中配置的引擎类型来确定使用什么引擎，目前有mapreduce和spark两种引擎，开发者也可以添加自己的构建引擎（通过kylin.engine.provider加入）。下面以spark引擎来继续分析，后面直接到SparkBatchCubingJobBuilder2的build，这个函数就是cube构建任务的核心：

```java
public CubingJob build() {
    logger.info("Spark new job to BUILD segment " + seg);
    //构建job任务（DefaultChainedExecutable类型，是一个任务链）
    final CubingJob result = CubingJob.createBuildJob(seg, submitter, config);
    final String jobId = result.getId();
    //获取cuboid在hdfs上的数据目录
    final String cuboidRootPath = getCuboidRootPath(jobId);
    // Phase 1: Create Flat Table & Materialize Hive View in Lookup Tables
    inputSide.addStepPhase1_CreateFlatTable(result);
    // Phase 2: Build Dictionary
    // 获取维度列的distinct值（即维度基数）
    result.addTask(createFactDistinctColumnsSparkStep(jobId));
    // 针对高基数维度（Ultra High Cardinality）单独起MR任务来构建字典，主要是ShardByColumns
    // 和GlobalDictionaryColumns
    if (isEnableUHCDictStep()) {
        result.addTask(createBuildUHCDictStep(jobId));
    }
    // 创建维度字典
    result.addTask(createBuildDictionaryStep(jobId));
    // 保存一些统计数据
    result.addTask(createSaveStatisticsStep(jobId));
    // add materialize lookup tables if needed
    LookupMaterializeContext lookupMaterializeContext = addMaterializeLookupTableSteps(result);
    // 创建hbase表
    outputSide.addStepPhase2_BuildDictionary(result);
    // Phase 3: Build Cube
    addLayerCubingSteps(result, jobId, cuboidRootPath); // layer cubing, only selected algorithm will execute
    //将上一步计算后的cuboid文件转换成hfile，然后将hfile load到hbase的表中
    outputSide.addStepPhase3_BuildCube(result);
    // Phase 4: Update Metadata & Cleanup
    result.addTask(createUpdateCubeInfoAfterBuildStep(jobId, lookupMaterializeContext));
    inputSide.addStepPhase4_Cleanup(result);
    outputSide.addStepPhase4_Cleanup(result);
 
    return result;
}
```

上述代码中的流程与页面上的构建过程基本一致，下面详细看下Cube计算这个步骤的实现过程，即addLayerCubingSteps(result, jobId, cuboidRootPath)。

```java
protected void addLayerCubingSteps(final CubingJob result, final String jobId, final String cuboidRootPath) {
    final SparkExecutable sparkExecutable = new SparkExecutable();
    // 设置cube计算的类
    sparkExecutable.setClassName(SparkCubingByLayer.class.getName());
    // 配置spark任务，主要为数据来源和cuboid数据保存位置
    configureSparkJob(seg, sparkExecutable, jobId, cuboidRootPath);
    // task加入到job中
    result.addTask(sparkExecutable);
}
```

接着看SparkCubingByLayer中的execute方法，最终任务调度服务调度执行job中的该task时，是调用execute方法来执行的，具体的调用过程可以参考上一篇任务调度的文章：

```java
protected void execute(OptionsHelper optionsHelper) throws Exception {
    String metaUrl = optionsHelper.getOptionValue(OPTION_META_URL);
    String hiveTable = optionsHelper.getOptionValue(OPTION_INPUT_TABLE);
    String inputPath = optionsHelper.getOptionValue(OPTION_INPUT_PATH);
    String cubeName = optionsHelper.getOptionValue(OPTION_CUBE_NAME);
    String segmentId = optionsHelper.getOptionValue(OPTION_SEGMENT_ID);
    String outputPath = optionsHelper.getOptionValue(OPTION_OUTPUT_PATH);
    Class[] kryoClassArray = new Class[] { Class.forName("scala.reflect.ClassTag$$anon$1") };
    SparkConf conf = new SparkConf().setAppName("Cubing for:" + cubeName + " segment " + segmentId);
    //serialization conf
    conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer");
    conf.set("spark.kryo.registrator", "org.apache.kylin.engine.spark.KylinKryoRegistrator");
    conf.set("spark.kryo.registrationRequired", "true").registerKryoClasses(kryoClassArray);
    KylinSparkJobListener jobListener = new KylinSparkJobListener();
    JavaSparkContext sc = new JavaSparkContext(conf);
    sc.sc().addSparkListener(jobListener);
    // 清空cuboid文件目录
    HadoopUtil.deletePath(sc.hadoopConfiguration(), new Path(outputPath));
    SparkUtil.modifySparkHadoopConfiguration(sc.sc()); // set dfs.replication=2 and enable compress
    final SerializableConfiguration sConf = new SerializableConfiguration(sc.hadoopConfiguration());
    KylinConfig envConfig = AbstractHadoopJob.loadKylinConfigFromHdfs(sConf, metaUrl);
 
    final CubeInstance cubeInstance = CubeManager.getInstance(envConfig).getCube(cubeName);
    final CubeDesc cubeDesc = cubeInstance.getDescriptor();
    final CubeSegment cubeSegment = cubeInstance.getSegmentById(segmentId);
 
    logger.info("RDD input path: {}", inputPath);
    logger.info("RDD Output path: {}", outputPath);
 
    final Job job = Job.getInstance(sConf.get());
    SparkUtil.setHadoopConfForCuboid(job, cubeSegment, metaUrl);
 
    int countMeasureIndex = 0;
    for (MeasureDesc measureDesc : cubeDesc.getMeasures()) {
        if (measureDesc.getFunction().isCount() == true) {
            break;
        } else {
            countMeasureIndex++;
        }
    }
    final CubeStatsReader cubeStatsReader = new CubeStatsReader(cubeSegment, envConfig);
    boolean[] needAggr = new boolean[cubeDesc.getMeasures().size()];
    boolean allNormalMeasure = true;
    for (int i = 0; i < cubeDesc.getMeasures().size(); i++) {
        // RawMeasureType这里为true，其他均为false
        needAggr[i] = !cubeDesc.getMeasures().get(i).getFunction().getMeasureType().onlyAggrInBaseCuboid();
        allNormalMeasure = allNormalMeasure && needAggr[i];
    }
    logger.info("All measure are normal (agg on all cuboids) ? : " + allNormalMeasure);
    StorageLevel storageLevel = StorageLevel.fromString(envConfig.getSparkStorageLevel());
    // 默认为true
    boolean isSequenceFile = JoinedFlatTable.SEQUENCEFILE.equalsIgnoreCase(envConfig.getFlatTableStorageFormat());
    // 从hive数据源表中构建出RDD，hiveRecordInputRDD得到格式为每行数据的每列的值的
    // RDD（JavaRDD<String[]>），maptoPair是按照basecubiod（每个维度都包含），计算出格式为 
    // rowkey（shard id+cuboid id+values）和每列的值的RDD encodedBaseRDD
    final JavaPairRDD<ByteArray, Object[]> encodedBaseRDD = SparkUtil.hiveRecordInputRDD(isSequenceFile, sc, inputPath, hiveTable)
            .mapToPair(new EncodeBaseCuboid(cubeName, segmentId, metaUrl, sConf));
 
    Long totalCount = 0L;
    // 默认为false
    if (envConfig.isSparkSanityCheckEnabled()) {
    // 数据总条数
        totalCount = encodedBaseRDD.count();
    }
    // 聚合度量值的具体方法
    final BaseCuboidReducerFunction2 baseCuboidReducerFunction = new BaseCuboidReducerFunction2(cubeName, metaUrl, sConf);
    BaseCuboidReducerFunction2 reducerFunction2 = baseCuboidReducerFunction;
    // 度量没有RAW的为true
    if (allNormalMeasure == false) {
        reducerFunction2 = new CuboidReducerFunction2(cubeName, metaUrl, sConf, needAggr);
    }
 
    final int totalLevels = cubeSegment.getCuboidScheduler().getBuildLevel();
    JavaPairRDD<ByteArray, Object[]>[] allRDDs = new JavaPairRDD[totalLevels + 1];
    int level = 0;
    int partition = SparkUtil.estimateLayerPartitionNum(level, cubeStatsReader, envConfig);
 
    // aggregate to calculate base cuboid
    allRDDs[0] = encodedBaseRDD.reduceByKey(baseCuboidReducerFunction, partition).persist(storageLevel);
    // 数据保存到hdfs上
    saveToHDFS(allRDDs[0], metaUrl, cubeName, cubeSegment, outputPath, 0, job, envConfig);
    // 根据base cuboid上卷聚合各个层级的数据，改变数据的rowKey，去掉相应的维度
       PairFlatMapFunction flatMapFunction = new CuboidFlatMap(cubeName, segmentId, 
       metaUrl, sConf);
    // aggregate to ND cuboids
    for (level = 1; level <= totalLevels; level++) {
        partition = SparkUtil.estimateLayerPartitionNum(level, cubeStatsReader, envConfig);
        // flatMapToPair得到上卷聚合后的数据，reduceByKey再进一步根据新的rowKey进行聚合操作， 
           因为进行flatMapToPair操作后会有部分数据的rowKey值相同
        allRDDs[level] = allRDDs[level - 1].flatMapToPair(flatMapFunction).reduceByKey(reducerFunction2, partition)
                .persist(storageLevel);
        allRDDs[level - 1].unpersist();
        if (envConfig.isSparkSanityCheckEnabled() == true) {
            sanityCheck(allRDDs[level], totalCount, level, cubeStatsReader, countMeasureIndex);
        }
        saveToHDFS(allRDDs[level], metaUrl, cubeName, cubeSegment, outputPath, level, job, envConfig);
    }
    allRDDs[totalLevels].unpersist();
    logger.info("Finished on calculating all level cuboids.");
    logger.info("HDFS: Number of bytes written=" + jobListener.metrics.getBytesWritten());
    //HadoopUtil.deleteHDFSMeta(metaUrl);
}

```

​        Cube在构建完所有的cuboid，原始的cuboid文件会存到hdfs目录下（例：/kylin/kylin_metadata/kylin-43be1d7f-4a50-b3a8-6dea-b998acec2d7b/kylin_sales_cube/cuboid），后面的createConvertCuboidToHfileStep任务会将cuboid文件转换成hfile文件保存到/kylin/kylin_metadata/kylin-43be1d7f-4a50-b3a8-6dea-b998acec2d7b/kylin_sales_cube/hfile目录下，最后会由createBulkLoadStep任务将hfile文件load到hbase表中（后面hfile目录会被删除），这样就完成了Cube的构建。这里需要注意的是cuboid文件在Cube构建完成后不会被删除，因为后面做Cube Segment的merge操作时是直接用已有的cuboid文件，而不需要重新进行计算，加快合并的速度，如果你确认后面不会进行segment的合并操作，cuboid文件可以手动删除掉以节省hdfs的存储空间。







## 三.RowKey编码

注：Kylin源码分析系列基于Kylin的2.5.0版本的源码，其他版本可以类比。
### 3.1.相关概念

前面介绍了Kylin中Cube构建的流程，但Cube数据具体是以什么样的形式存在，可能还不是特别清晰明了，这篇文章就详细介绍下Cube数据的数据格式，主要就是其rowKey的编码，看下Kylin是怎样来保存各种维度组合下的各种度量的统计值的。这里首先介绍下Cube数据立方的相关概念。

- 事实表Fact Table


事实表（Fact Table）是中心表，包含了大批数据并不冗余，其数据列可分为两类：

包含大量数据事实的列；与维表（Lookup Table）的primary key相对应的foreign key。

- 维表Lookup Table


Lookup Table包含对事实表的某些列进行扩充说明的字段。在Kylin的quick start中给出sample cube（kylin_sales_cube）——其Fact Table为购买记录，lookup table有两个：用于对购买日期PART_DT、商品的LEAF_CATEG_ID与LSTG_SITE_ID字段进行扩展说明。

- 维度Dimensions


维度是观察数据的角度，一般是一组离散的值，可以类比为数据库表中的列。每个维

度都会有一组值，这里将值的个数成为维度基数（cardinatily）。同时从一个或多个维度来观察数据，则称这一个或多个维度组合成了一个维度组合，这种维度组合在Kylin中也称之为cuboid；如果有n个维度列，则理论上的维度组合有2的N次方个，这样如果维度列很多的时候维度组合的个数就会指数型膨胀，但有些维度组合的使用价值可能会有重复，有些可能就不会用到，这样就会导致资源的浪费。

Kylin中针对维度的概念进行了进一步的细化，分为了普通维度Normal Dimensions，必要维度Mandatory Dimensions，层级维度Hierarchy Dimensions和联合维度Joint Dimensions，这样可以进一步减少cuboid的个数。

其中Mandatory Dimensions是在每次查询都会用到的维度，比如下图中A如果为Mandatory dimension，则与B、C总共构成了4个cuboid，相较于之前的cuboid（2的3次方，8)减少了一半。

http://images2015.cnblogs.com/blog/399159/201603/399159-20160303170405065-1445103588.png

![img](/img/399159-20160303170405065-1445103588.png)

Hierarchy Dimensions为带层级的维度，比如说：省份->城市， 年->季度->月->周->日；如下图所示：

![img](/img/399159-20160303170417784-1772210326.png)

Derived Dimensions指该维度与维表的primary key是一一对应关系，可以更有效地减少cuboid数量，详细的解释参看这里；并且derived dimension只能由lookup table的列生成。如下图所示：

http://images2015.cnblogs.com/blog/399159/201603/399159-20160303170425393-1379274928.png

![img](/img/399159-20160303170425393-1379274928.png)

另外Kylin还设计了一个Aggregation Groups聚合组来进一步减少cuboid的个数。

用户根据自己关注的维度组合，可以划分出自己关注的组合大类，这些大类在 Apache Kylin 里面被称为聚合组。例如下图中展示的 Cube，如果用户仅仅关注维度 AB 组合和维度 CD 组合，那么该 Cube 则可以被分化成两个聚合组，分别是聚合组 AB 和聚合组 CD。如图 2 所示，生成的 Cuboid 数目从 16 个缩减成了 8 个。

 

同时，用户关心的聚合组之间可能包含相同的维度，例如聚合组 ABC 和聚合组 BCD 都包含维度 B 和维度 C。这些聚合组之间会衍生出相同的 Cuboid，例如聚合组 ABC 会产生 Cuboid BC，聚合组 BCD 也会产生 Cuboid BC。这些 Cuboid不会被重复生成，一份 Cuboid 为这些聚合组所共有，如下图所示：

 有了聚合组用户就可以粗粒度地对 Cuboid 进行筛选，获取自己想要的维度组合。

- 度量Measures


度量即为用户关心的针对某些维度组合的统计值。kylin会自动为每一个cube创建一个聚合函数为count(1)的度量（kylin设置度量的时候必须要有COUNT），它不需要关联任何列，用户自定义的度量可以选择SUM、COUNT、DISTINCT COUNT、MIN、MAX、TOP_N、RAW、EXTENDED_COLUMN、PERCENTILE，而每一个度量定义时还可以选择这些聚合函数的参数，可以选择常量或者事实表的某一列，一般情况下我们当然选择某一列。这里我们发现kylin并不提供AVG等相对较复杂的聚合函数（方差、平均差更没有了），主要是因为kylin中或有多个cube segment进行合并计生成新的cube segment，而这些复杂的聚合函数并不能简单的对两个值计算之后得到新的值，例如需要增量合并的两个cube中某一个key对应的sum值分别为A和B，那么合并之后的则为A+B,而如果此时的聚合函数是AVG，那么我们必须知道这个key的count和sum之后才能做聚合。这就要求使用者必须自己想办法自己计算了。

其中RAW度量是为了查询数据的明细值，EXTENDED_COLUMN度量是将某些维度列设置成度量，以便在使用其他列过滤但需要查询该列时使用，PERCENTILE度量是一种百分位数统计的方法。

上面讲到segment，kylin中的每个cube（逻辑上）中会包含多个segment，每个segment对应着一个物理cube，在实际存储中对应一个hbase的表，用户在构建模型的时候需要定义根据某一个字段进行增量构建（目前仅支持时间，并且这个字段必须是hive的一个分区字段），其实这个选择是作为原始数据选择的条件，例如选择起始时间A到B的数据那么创建的cube则会只包含这个时间段的数据聚合值，创建完一个cube之后可以再次基于以前的cube进行build，每次build会生成一个新的segment，只不过原始数据不一样了（根据每次build指定的时间区间），每次查询的时候会查询所有的segment聚合之后的值进行返回，但是当segment存在过多的时候查询效率就会下降，因此需要在存在多个segment的时候将它们进行合并，合并的时候其实是指定了一个时间区间，内部会选择这个时间区间内的所有segment进行合并，合并完成之后使用新的segment（新的hbase表）替换被合并的多个segment，被合并的几个segment所对应的hbase表会被删除。

### 3.2.RowKey组成

#### 3.2.1 简介

Kylin中的RowKey由shard id + cuboid id + dimension values三部分组成，其中shard id有两个字节，cuboid有八个字节，dimension values为各个维度值经过编码后的值。

Shard id是每个cuboid的分片id，用户在配置rowkey的时候选择一个维度来划分分片，这样每个cuboid会被分成多个分片，对于目前的hbase存储，就是将每个cuboid的数据分成多个region来存储，这样就会分散到hbase的多个regionserver上，因为Kylin使用了hbase的协处理器来进行查询，这样可以将查询分散到各个regionserver上进行查询（过滤和聚合），提高查询速度。

Cuboid id为一个八字节的long类型值（Kylin最多支持63个维度），值的每一位表示维度组合中的一个维度，存在为1，不存在为0，假设有A、B、C、D、E、F、G、H八个维度（使用一个字节即可，前七个字节为0），对于base cuboid（包含所有的维度）的id值为11111111（255），对于维度组合A、B、C、D，cuboid为11110000（240），维度组合A、D、F、H的cuboid为10010101（149），其他的以此类推。

dimension values为各个维度的值，但并不是维度实际的值，而是经过编码后的值，Kylin这样做是为了减少数据的存储空间。

#### 3.2.2 编码方式

Kylin中的编码方式包括Date编码、Time编码、Integer编码、Boolean编码、Dict编码和Fixed Length编码，用户可以根据需求选择合适的编码方式。

- Date编码


将日期类型的数据使用三个字节进行编码，支持的格式包括yyyyMMdd、yyyy-MM-dd、yyyy-MM-dd HH:mm:ss、yyyy-MM-dd HH:mm:ss.SSS，其中如果包含时间戳部分会被截断。

3个字节（23位）， 支持0000-01-01到9999-01-01

- Time编码


对时间戳字段进行编码，4个字节，支持范围为[ 1970-01-01 00:00:00, 2038/01/19 03:14:07]，毫秒部分会被忽略。time编码适用于time, datetime, timestamp等类型。

- Integer编码


将数值类型字段直接用数字表示，不做编码转换。Integer编码需要提供一个额外的参数“Length”来代表需要多少个字节。Length的长度为1到8，支持的整数区间为[ -2^(8*N-1), 2^(8*N-1)]。

- Dict编码


使用字典将长的值映射成短的ID，适合中低基数的维度，默认推荐编码。但由于字典要被加载到Kylin内存中，在超高基情况下，可能引起内存不足的问题。

简单使用方法：

```java
TrieDictionaryBuilder<String> b = new TrieDictionaryBuilder<String>(new StringBytesConverter());

b.addValue("part");
b.addValue("part");
b.addValue("par");
b.addValue("partition");
b.addValue("party");
b.addValue("parties");
b.addValue("paint");

TrieDictionary<String> dict = b.build(0);
```

 

按照以上的方法构建后，会生成一颗Trie树，结构如下：
```java
-

  part - *

 -

  part - *

 -

  par - *

    t - *

 -

  par - *

    t - *
    
      ition - *

 -

  par - *

    t - *
    
      ition - *
    
      y - *

 -

  par - *

    t - *
    
      i -
    
        es - *
    
        tion - *
    
      y - *

 -

  pa -

    int - *
    
    r - *
    
      t - *
    
        i -
    
          es - *
    
          tion - *
    
        y - *
```

编码结果：0:paint  1:par  2:part  3:parties  4:partition  5:party

这些编码后的值为int类型。

根据编码获取实际维度值：

```
Bytes.toString(dict.getValueBytesFromIdWithoutCache(i))
```

根据维度值获取编码：

```
BytesConverter converter = new StringBytesConverter();
byte[] bytes = converter.convertToBytes("part");
int id = dict.getIdFromValueBytesWithoutCache(bytes, 0, bytes.length-1, 0);
```

字典编码为一颗Trie树，也叫字典树，是一种哈希树的变种，优点是利用字符串的公共前缀来减少查询时间，最大限度地减少无谓的字符串比较，查询效率比哈希树高。

它有三个基本特性：

1. 根节点不包含字符，除根节点外每一个节点都只包含一个字符；
2. 从根节点到某一节点，路径上经过的字符连接起来，为该节点对应的字符串； 
3. 每个节点的所有子节点包含的字符都不相同。



- Fixed_length编码


适用于超高基数场景，将选取字段的前N个字节作为编码值，当N小于字段长度，会造成字段截断，当N较大时，造成RowKey过长，查询性能下降。只适用于varchar或nvarchar类型。

- Fixed_Length_Hex编码


适用于字段值为十六进制字符，比如1A2BFF或者FF00FF，每两个字符需要一个字节。只适用于varchar或nvarchar类型。

#### 3.2.3 源码解析

这里是基于spark构建引擎来进行相关分析，前面一篇文章讲过Cube构建的过程，在createFactDistinctColumnsSparkStep这一步得到了各个维度的distinct值（SparkFactDistinct、MultiOutputFunction保存字典文件），然后写到文件里面（后面构建字典使用），这里对各维度进行编码主要就是针对这些distinct值来进行，源码位于CreateDictionaryJob这个类中。看下里面的run方法：

    public int run(String[] args) throws Exception {
        Options options = new Options();
        options.addOption(OPTION_CUBE_NAME);
        options.addOption(OPTION_SEGMENT_ID);
        options.addOption(OPTION_INPUT_PATH);
        options.addOption(OPTION_DICT_PATH);
        parseOptions(options, args);
        final String cubeName = getOptionValue(OPTION_CUBE_NAME);
        final String segmentID = getOptionValue(OPTION_SEGMENT_ID);
        final String factColumnsInputPath = getOptionValue(OPTION_INPUT_PATH);
        final String dictPath = getOptionValue(OPTION_DICT_PATH);
        final KylinConfig config = KylinConfig.getInstanceFromEnv();
     
        //对该segment进行字典的构建
        DictionaryGeneratorCLI.processSegment(config, cubeName, segmentID, new DistinctColumnValuesProvider() {
            @Override
            //读取文件中的对应维度的distinct值
            public IReadableTable getDistinctValuesFor(TblColRef col) {
                // 文件路径为上一步保存distinct值的文件路径
                return new SortedColumnDFSFile(factColumnsInputPath + "/" + col.getIdentity(), col.getType());
            }
        }, new DictionaryProvider() {
            @Override
            // 获取对应维度使用的编码字典
            public Dictionary<String> getDictionary(TblColRef col) throws IOException {
                CubeManager cubeManager = CubeManager.getInstance(config);
                CubeInstance cube = cubeManager.getCube(cubeName);
                List<TblColRef> uhcColumns = cube.getDescriptor().getAllUHCColumns();
                Path colDir;
                // 对于UHC维度列路径类似于
                // /kylin/kylin_metadata/kylin-20240f69-5abe-6c82-56c7- 
                // 11c0ea0ffa42/kylin_sales_cube/dict/{colName}
                if (config.isBuildUHCDictWithMREnabled() && uhcColumns.contains(col)) {
                    colDir = new Path(dictPath, col.getIdentity());
                } else {
                    // 上一步保存distinct值的文件路径,类似于
                    // /kylin/kylin_metadata/kylin-20240f69-5abe-6c82-56c7- 
                    // 11c0ea0ffa42/kylin_sales_cube/fact_distinct_columns/{colName}
                    colDir = new Path(factColumnsInputPath, col.getIdentity());
                }
                FileSystem fs = HadoopUtil.getWorkingFileSystem();
                // 过滤以{colName}.rldict开头的文件
                Path dictFile = HadoopUtil.getFilterOnlyPath(fs, colDir, col.getName() + FactDistinctColumnsReducer.DICT_FILE_POSTFIX);
                if (dictFile == null) {
                    logger.info("Dict for '" + col.getName() + "' not pre-built.");
                    return null;
                }
                // 读取字典
                try (SequenceFile.Reader reader = new SequenceFile.Reader(HadoopUtil.getCurrentConfiguration(), SequenceFile.Reader.file(dictFile))) {
                    NullWritable key = NullWritable.get();
                    ArrayPrimitiveWritable value = new ArrayPrimitiveWritable();
                    reader.next(key, value);
                    ByteBuffer buffer = new ByteArray((byte[]) value.get()).asBuffer();
                    try (DataInputStream is = new DataInputStream(new ByteBufferBackedInputStream(buffer))) {
                        String dictClassName = is.readUTF();
                        Dictionary<String> dict = (Dictionary<String>) ClassUtil.newInstance(dictClassName);
                        dict.readFields(is);
                        logger.info("DictionaryProvider read dict from file: " + dictFile);
                        return dict;
                    }
                }
            }
        });
        return 0;
    }

里面主要看new DistinctColumnValuesProvider和new DictionaryProvider，DistinctColumnValuesProvider是去获取上一步保存的各维度的distinct值，DictionaryProvider是获取对应类型的字典。看下具体的处理函数processSegment：

    public static void processSegment(KylinConfig config, String cubeName, String segmentID, DistinctColumnValuesProvider factTableValueProvider, DictionaryProvider dictProvider) throws IOException {
        //根据cube的名称和segmentID获取对应的CubeSegment实例
        CubeInstance cube = CubeManager.getInstance(config).getCube(cubeName);
        CubeSegment segment = cube.getSegmentById(segmentID);
        processSegment(config, segment, factTableValueProvider, dictProvider);
    }
     
    private static void processSegment(KylinConfig config, CubeSegment cubeSeg, DistinctColumnValuesProvider factTableValueProvider, DictionaryProvider dictProvider) throws IOException {
        CubeManager cubeMgr = CubeManager.getInstance(config);
        // dictionary
        // 获取所有需要构建字典的维度列
        for (TblColRef col : cubeSeg.getCubeDesc().getAllColumnsNeedDictionaryBuilt()) {
            logger.info("Building dictionary for " + col);
            // 读取维度列的distinct值的文件（调用前面new DistinctColumnValuesProvider()中重写的 
            // getDistinctValuesFor）
            IReadableTable inpTable = factTableValueProvider.getDistinctValuesFor(col);
            
            Dictionary<String> preBuiltDict = null;
            if (dictProvider != null) {
                // 调用前面new DictionaryProvider()中重写的方法获取预先构建的字典，如果没有预先构 
                // 建会返回null
                preBuiltDict = dictProvider.getDictionary(col);
            }
            // 如果已经构建过了则保存字典，没有则构建。字典保存的目录如：   
            // /kylin/kylin_metadata/kylin-20240f69-5abe-6c82-56c7- 
            // 11c0ea0ffa42/kylin_sales_cube/metadata/ 
            // dict/DEFAULT.KYLIN_SALES/SELLER_ID/e7cd07a8-7ad3-5ad2-1e39-6f37e12921b1.dict
            if (preBuiltDict != null) {
                logger.debug("Dict for '" + col.getName() + "' has already been built, save it");
                cubeMgr.saveDictionary(cubeSeg, col, inpTable, preBuiltDict);
            } else {
                logger.debug("Dict for '" + col.getName() + "' not pre-built, build it from " + inpTable.toString());
                cubeMgr.buildDictionary(cubeSeg, col, inpTable);
            }
        }
     
        // snapshot lookup tables
        ......
    }

到这一步各个需要进行字段编码的维度的字典就构建好了，后面再计算Cube，拼接RowKey的时候直接使用这里的字典来获取对应维度值的编码值。下面接着看下Cube数据的RowKey是怎么拼接的。前面Cube构建的文章中讲述了构建的过程，这里直接看SparkCubingByLayer中execute方法调用的EncodeBaseCuboid的call方法：

    public Tuple2<ByteArray, Object[]> call(String[] rowArray) throws Exception {
        if (initialized == false) {
            synchronized (SparkCubingByLayer.class) {
                if (initialized == false) {
                    KylinConfig kConfig = AbstractHadoopJob.loadKylinConfigFromHdfs(conf, metaUrl);
                    try (KylinConfig.SetAndUnsetThreadLocalConfig autoUnset = KylinConfig
                            .setAndUnsetThreadLocalConfig(kConfig)) {
                        CubeInstance cubeInstance = CubeManager.getInstance(kConfig).getCube(cubeName);
                        CubeDesc cubeDesc = cubeInstance.getDescriptor();
                        CubeSegment cubeSegment = cubeInstance.getSegmentById(segmentId);
                        CubeJoinedFlatTableEnrich interDesc = new CubeJoinedFlatTableEnrich(
                                EngineFactory.getJoinedFlatTableDesc(cubeSegment), cubeDesc);
                        // 计算出base cuboid id
                        long baseCuboidId = Cuboid.getBaseCuboidId(cubeDesc);
                        Cuboid baseCuboid = Cuboid.findForMandatory(cubeDesc, baseCuboidId);
                        baseCuboidBuilder = new BaseCuboidBuilder(kConfig, cubeDesc, cubeSegment, interDesc,
                                AbstractRowKeyEncoder.createInstance(cubeSegment, baseCuboid),
                                MeasureIngester.create(cubeDesc.getMeasures()), cubeSegment.buildDictionaryMap());
                        initialized = true;
                    }
                }
            }
        }
        baseCuboidBuilder.resetAggrs();
        // 根据Hive中读出的RDD（所有的维度列值）进行处理。
        // 这里的rowKey为shard id + cuboid id + values
        byte[] rowKey = baseCuboidBuilder.buildKey(rowArray);
        Object[] result = baseCuboidBuilder.buildValueObjects(rowArray);
        return new Tuple2<>(new ByteArray(rowKey), result);
    }

接着看BaseCuboidBuilder 的buildKey函数：

    public byte[] buildKey(String[] flatRow) {
        int[] rowKeyColumnIndexes = intermediateTableDesc.getRowKeyColumnIndexes();
        List<TblColRef> columns = baseCuboid.getColumns();
        String[] colValues = new String[columns.size()];
        for (int i = 0; i < columns.size(); i++) {
            colValues[i] = getCell(rowKeyColumnIndexes[i], flatRow);
        }
        //rowKey编码
        return rowKeyEncoder.encode(colValues);
    }

接着调用RowKeyEncoder的encode方法：

    public byte[] encode(String[] values) {
        byte[] bytes = new byte[this.getBytesLength()];
        //header部分有（shard id和cuboid id， 2字节+8字节）
        int offset = getHeaderLength();
        for (int i = 0; i < cuboid.getColumns().size(); i++) {
            TblColRef column = cuboid.getColumns().get(i);
            int colLength = colIO.getColumnLength(column);
            //这里填入各个维度列的编码值
            fillColumnValue(column, colLength, values[i], bytes, offset);
            offset += colLength;
        }
        //fill shard id and cuboid id
        fillHeader(bytes);
     
        return bytes;
    }

看下fillColumnValue函数：

    protected void fillColumnValue(TblColRef column, int columnLen, String valueStr, byte[] outputValue, int outputValueOffset) {
        // special null value case
        if (valueStr == null) {
            Arrays.fill(outputValue, outputValueOffset, outputValueOffset + columnLen, defaultValue());
            return;
        }
        colIO.writeColumn(column, valueStr, 0, this.blankByte, outputValue, outputValueOffset);
    }

最终的填入编码值就在RowKeyColumnIO的wireColumn函数中：

    public void writeColumn(TblColRef col, String value, int roundingFlag, byte defaultValue, byte[] output, int outputOffset) {
        // 获取维度列的编码方法，调用CubeDimEncMap的get方法
        DimensionEncoding dimEnc = dimEncMap.get(col);
        if (dimEnc instanceof DictionaryDimEnc)
            dimEnc = ((DictionaryDimEnc) dimEnc).copy(roundingFlag, defaultValue);
        // 调用对应的encode方法对维度值进行编码
        dimEnc.encode(value, output, outputOffset);
    }

这里看下字典编码方式（其他的编码方式类似），dimEnc为DictionaryDimEnc，看下encode方法：

    public void encode(String valueStr, byte[] output, int outputOffset) {
        try {
            // 根据字典获取维度值的编码值，最后将int类型的编码值转换成byte数组
            int id = dict.getIdFromValue(valueStr, roundingFlag);
            BytesUtil.writeUnsigned(id, output, outputOffset, fixedLen);
        } catch (IllegalArgumentException ex) {
            for (int i = outputOffset; i < outputOffset + fixedLen; i++) {
                output[i] = defaultByte;
            }
            logger.error("Can't translate value " + valueStr + " to dictionary ID, roundingFlag " + roundingFlag + ". Using default value " + String.format("\\x%02X", defaultByte));
        }
    // 若num为300, bytes为byte[2], offset为0, size为2
    public static void writeUnsigned(int num, byte[] bytes, int offset, int size) {
        for (int i = offset + size - 1; i >= offset; i--) {
            // bytes[1]为44, num右移8位后为1, bytes[0]为1
            bytes[i] = (byte) num;
            num >>>= 8;
        }
    }
    
        这里就完成了Cube的Base Cuboid的RowKey的编码工作，后面的各个层级的cuboid的RowKey的值均根据Base Cuboid的RowKey变换而来，Cube查询的时候也是使用这些RowKey值到hbase查询相关的数据。
    
        看完RowKey的编码，顺便看下对应的度量值是怎么保存的，在计算完各个层级的cube数据后各个RDD的格式为JavaPairRDD<ByteArray, Object[]>（看SparkCubingByLayer中的execute），然后调用saveToHDFS方法来将rdd保存为cuboid文件，该函数中会将所有的度量值编码为一个字节数组（byte[]）,编码函数位于BufferedMeasureCodec中，通过调用encode函数将各个类型的度量值转换为ByteBuffer，最终以Tuple2<org.apache.hadoop.io.Text, org.apache.hadoop.io.Text>格式存储到cuboid文件，后面继而通过createConvertCuboidToHfileStep将cuboid文件转换为hfile，直接看SparkCubeHFile中的execute函数：
    
    protected void execute(OptionsHelper optionsHelper) throws Exception {
        . . .
        // 从上一步保存的cuboid文件中读出cube数据
        JavaPairRDD<Text, Text> inputRDDs = SparkUtil.parseInputPath(inputPath, fs, sc, Text.class, Text.class);
        // 转换为hfile的格式
        final JavaPairRDD<RowKeyWritable, KeyValue> hfilerdd;
        if (quickPath) {
            // 只有一个Column Family
            hfilerdd = inputRDDs.mapToPair(new PairFunction<Tuple2<Text, Text>, RowKeyWritable, KeyValue>() {
                @Override
                public Tuple2<RowKeyWritable, KeyValue> call(Tuple2<Text, Text> textTextTuple2) throws Exception {
                    KeyValue outputValue = keyValueCreators.get(0).create(textTextTuple2._1,
                            textTextTuple2._2.getBytes(), 0, textTextTuple2._2.getLength());
                    return new Tuple2<>(new RowKeyWritable(outputValue.createKeyOnly(false).getKey()), outputValue);
                }
            });
        } else {
            hfilerdd = inputRDDs.flatMapToPair(new PairFlatMapFunction<Tuple2<Text, Text>, RowKeyWritable, KeyValue>() {
                @Override
                public Iterator<Tuple2<RowKeyWritable, KeyValue>> call(Tuple2<Text, Text> textTextTuple2)
                        throws Exception {
     
                    List<Tuple2<RowKeyWritable, KeyValue>> result = Lists.newArrayListWithExpectedSize(cfNum);
                    Object[] inputMeasures = new Object[cubeDesc.getMeasures().size()];
                    // 从字节数组中反序列化出所有的度量值
                    inputCodec.decode(ByteBuffer.wrap(textTextTuple2._2.getBytes(), 0, textTextTuple2._2.getLength()),
                            inputMeasures);
     
                    for (int i = 0; i < cfNum; i++) {
                        // 创建KeyValue，里面的value值又被序列化为ByteBuffer
                        KeyValue outputValue = keyValueCreators.get(i).create(textTextTuple2._1, inputMeasures);
                        result.add(new Tuple2<>(new RowKeyWritable(outputValue.createKeyOnly(false).getKey()),
                                outputValue));
                    }
     
                    return result.iterator();
                }
            });
        }
     
        hfilerdd.repartitionAndSortWithinPartitions(new HFilePartitioner(keys),
                RowKeyWritable.RowKeyComparator.INSTANCE)
                .mapToPair(new PairFunction<Tuple2<RowKeyWritable, KeyValue>, ImmutableBytesWritable, KeyValue>() {
                    @Override
                    public Tuple2<ImmutableBytesWritable, KeyValue> call(
                            Tuple2<RowKeyWritable, KeyValue> rowKeyWritableKeyValueTuple2) throws Exception {
                        return new Tuple2<>(new ImmutableBytesWritable(rowKeyWritableKeyValueTuple2._2.getKey()),
                                rowKeyWritableKeyValueTuple2._2);
                    }
                }).saveAsNewAPIHadoopDataset(job.getConfiguration());
     
        logger.info("HDFS: Number of bytes written=" + jobListener.metrics.getBytesWritten());
     
        Map<String, String> counterMap = Maps.newHashMap();
        counterMap.put(ExecutableConstants.HDFS_BYTES_WRITTEN, String.valueOf(jobListener.metrics.getBytesWritten()));
     
        // save counter to hdfs
        HadoopUtil.writeToSequenceFile(sc.hadoopConfiguration(), counterPath, counterMap);
     
        //HadoopUtil.deleteHDFSMeta(metaUrl);
    }

2.4 总结

上面就是Kylin中Cube数据的RowKey和各个度量值的编码保存过程，cube数据最后存储在hbase中，通过hbase shell查看形式如下：

 ![img](/img/20190105164801104.png)

前面是RowKey值，后面是ColumnFamily和Qualifier，看到有两个（F1:M和F2:M），与前面创建cube时的配置一致。前面Cube配置如下：

![img](/img/20190105164817881.png)



## 四.Cube查询

注：Kylin源码分析系列基于Kylin的2.5.0版本的源码，其他版本可以类比。

### 4.1. 简介

前面文章介绍了Cube是如何构建的，那构建完成后用户肯定是需要对这些预统计的数据进行相关的查询操作，这篇文章就介绍下Kylin中是怎样通过SQL语句来进行Cube数据的查询的。Kylin中的查询是在web页面上输入sql语句然后提交来执行相关查询，页面上的提交也是向Kylin的Rest Server发送restful请求，方法与前面文章介绍的Cube构建的触发方式类似，通过angularJS发送restful请求，请求url为/kylin/api/query，Kylin的Rest Server接收到该请求后，进行Cube数据的查询。

Kylin中使用的是Apache Calcite查询引擎。Apache Calcite是面向 Hadoop 的查询引擎，它提供了标准的 SQL 语言、多种查询优化和连接各种数据源的能力，除此之外，Calcite 还提供了 OLAP 和流处理的查询引擎。

Apache Calcite具有以下几个技术特性

    支持标准SQL 语言；
    独立于编程语言和数据源，可以支持不同的前端和后端；
    支持关系代数、可定制的逻辑规划规则和基于成本模型优化的查询引擎；
    支持物化视图（materialized view）的管理（创建、丢弃、持久化和自动识别）；
    基于物化视图的 Lattice 和 Tile 机制，以应用于 OLAP 分析；
    支持对流数据的查询。

这里不详细介绍每个特性，读者可以自行去学习了解。Kylin之所以选择这个查询引擎正是由于Calcite 可以很好地支持物化视图和星模式这些 OLAP 分析的关键特性。

### 4.2. 源码解析

  Rest Server接收到查询的RestFul请求后，根据url将其分发到QueryController控制器来进行处理：

    @RequestMapping(value = "/query", method = RequestMethod.POST, produces = { "application/json" })
    @ResponseBody
    public SQLResponse query(@RequestBody PrepareSqlRequest sqlRequest) {
        return queryService.doQueryWithCache(sqlRequest);
    }

  后面就由QueryService来进行查询处理：

    public SQLResponse doQueryWithCache(SQLRequest sqlRequest) {
        long t = System.currentTimeMillis();
        //检查权限
        aclEvaluate.checkProjectReadPermission(sqlRequest.getProject());
        logger.info("Check query permission in " + (System.currentTimeMillis() - t) + " ms.");
        return doQueryWithCache(sqlRequest, false);
    }
    public SQLResponse doQueryWithCache(SQLRequest sqlRequest, boolean isQueryInspect) {
        Message msg = MsgPicker.getMsg();
        // 获取用户名
        sqlRequest.setUsername(getUserName());
     
        KylinConfig kylinConfig = KylinConfig.getInstanceFromEnv();
        String serverMode = kylinConfig.getServerMode();
        // 服务模式不为query和all的无法进行查询
        if (!(Constant.SERVER_MODE_QUERY.equals(serverMode.toLowerCase())
                || Constant.SERVER_MODE_ALL.equals(serverMode.toLowerCase()))) {
            throw new BadRequestException(String.format(msg.getQUERY_NOT_ALLOWED(), serverMode));
        }
        // project不能为空
        if (StringUtils.isBlank(sqlRequest.getProject())) {
            throw new BadRequestException(msg.getEMPTY_PROJECT_NAME());
        }
        // project not found
        ProjectManager mgr = ProjectManager.getInstance(KylinConfig.getInstanceFromEnv());
        if (mgr.getProject(sqlRequest.getProject()) == null) {
            throw new BadRequestException(msg.getPROJECT_NOT_FOUND());
        }
        // sql语句不能为空
        if (StringUtils.isBlank(sqlRequest.getSql())) {
            throw new BadRequestException(msg.getNULL_EMPTY_SQL());
        }
     
        // 用于保存用户查询输入的相关参数，一般用于调试
        if (sqlRequest.getBackdoorToggles() != null)
            BackdoorToggles.addToggles(sqlRequest.getBackdoorToggles());
        // 初始化查询上下文，设置了queryId和queryStartMillis
        final QueryContext queryContext = QueryContextFacade.current();
        // 设置新的查询线程名
        try (SetThreadName ignored = new SetThreadName("Query %s", queryContext.getQueryId())) {
            SQLResponse sqlResponse = null;
            // 获取查询的sql语句
            String sql = sqlRequest.getSql();
            String project = sqlRequest.getProject();
            // 是否开启了查询缓存，kylin.query.cache-enabled默认开启
            boolean isQueryCacheEnabled = isQueryCacheEnabled(kylinConfig);
            logger.info("Using project: " + project);
            logger.info("The original query:  " + sql);
            // 移除sql语句中的注释
    sql = QueryUtil.removeCommentInSql(sql);
     
            Pair<Boolean, String> result = TempStatementUtil.handleTempStatement(sql, kylinConfig);
            boolean isCreateTempStatement = result.getFirst();
            sql = result.getSecond();
            sqlRequest.setSql(sql);
     
            // try some cheap executions
            if (sqlResponse == null && isQueryInspect) {
                sqlResponse = new SQLResponse(null, null, 0, false, sqlRequest.getSql());
            }
     
            if (sqlResponse == null && isCreateTempStatement) {
                sqlResponse = new SQLResponse(null, null, 0, false, null);
            }
            // 缓存中直接查询
            if (sqlResponse == null && isQueryCacheEnabled) {
                sqlResponse = searchQueryInCache(sqlRequest);
            }
     
            // real execution if required
            if (sqlResponse == null) {
                // 并发查询限制, kylin.query.project-concurrent-running-threshold, 默认为0, 无 
                // 限制
                try (QueryRequestLimits limit = new QueryRequestLimits(sqlRequest.getProject())) {
                    // 查询，如有必要更新缓存
                    sqlResponse = queryAndUpdateCache(sqlRequest, isQueryCacheEnabled);
                }
            }
            sqlResponse.setDuration(queryContext.getAccumulatedMillis());
            logQuery(queryContext.getQueryId(), sqlRequest, sqlResponse);
            try {
                recordMetric(sqlRequest, sqlResponse);
            } catch (Throwable th) {
                logger.warn("Write metric error.", th);
            }
            if (sqlResponse.getIsException())
                throw new InternalErrorException(sqlResponse.getExceptionMessage());
            return sqlResponse;
        } finally {
            BackdoorToggles.cleanToggles();
            QueryContextFacade.resetCurrent();
        }
    }


  下面接着调用queryAndUpdateCache，看下具体源码：

    private SQLResponse queryAndUpdateCache(SQLRequest sqlRequest, boolean queryCacheEnabled) {
        KylinConfig kylinConfig = KylinConfig.getInstanceFromEnv();
        Message msg = MsgPicker.getMsg();
        final QueryContext queryContext = QueryContextFacade.current();
        SQLResponse sqlResponse = null;
        try {
            // 判断是不是select查询语句
            final boolean isSelect = QueryUtil.isSelectStatement(sqlRequest.getSql());
            if (isSelect) {
                sqlResponse = query(sqlRequest, queryContext.getQueryId());
              // 查询下推到其他的查询引擎，比如直接通过hive查询
            } else if (kylinConfig.isPushDownEnabled() && kylinConfig.isPushDownUpdateEnabled()) {
                sqlResponse = update(sqlRequest);
            } else {
                logger.debug("Directly return exception as the sql is unsupported, and query pushdown is disabled");
                throw new BadRequestException(msg.getNOT_SUPPORTED_SQL());
            }
    . . . 
        return sqlResponse;
    }
    public SQLResponse query(SQLRequest sqlRequest, String queryId) throws Exception {
        SQLResponse ret = null;
        try {
            final String user = SecurityContextHolder.getContext().getAuthentication().getName();
            // 加入到查询队列，BadQueryDetector会对该查询进行检测，看是否超时或是否为慢查询（默认 
            // 90S）
            badQueryDetector.queryStart(Thread.currentThread(), sqlRequest, user, queryId);
            ret = queryWithSqlMassage(sqlRequest);
            return ret;
        } finally {
            String badReason = (ret != null && ret.isPushDown()) ? BadQueryEntry.ADJ_PUSHDOWN : null;
            badQueryDetector.queryEnd(Thread.currentThread(), badReason);
            Thread.interrupted(); //reset if interrupted
        }
    }
    private SQLResponse executeRequest(String correctedSql, SQLRequest sqlRequest, Connection conn) throws Exception {
        Statement stat = null;
        ResultSet resultSet = null;
        boolean isPushDown = false;
     
        Pair<List<List<String>>, List<SelectedColumnMeta>> r = null;
        try {
            stat = conn.createStatement();
            processStatementAttr(stat, sqlRequest);
            resultSet = stat.executeQuery(correctedSql);
            r = createResponseFromResultSet(resultSet); 
        } catch (SQLException sqlException) {
            r = pushDownQuery(sqlRequest, correctedSql, conn, sqlException);
            if (r == null)
                throw sqlException;
            isPushDown = true;
        } finally {
            close(resultSet, stat, null); //conn is passed in, not my duty to close
        }
        return buildSqlResponse(isPushDown, r.getFirst(), r.getSecond());
    }

stat.executeQuery(correctedSql)接着就是calcite对SQL语句的解析优化处理，该部分内容这里不详细描述，具体的堆栈信息如下：

下面接着看OLAPEnumerator中的queryStorage：

    private ITupleIterator queryStorage() {
        logger.debug("query storage...");
        // bind dynamic variables
        olapContext.bindVariable(optiqContext);
        olapContext.resetSQLDigest();
        SQLDigest sqlDigest = olapContext.getSQLDigest();
        // query storage engine
        // storageEngine为CubeStorageQuery，继承GTCubeStorageQueryBase
        IStorageQuery storageEngine = StorageFactory.createQuery(olapContext.realization);
        ITupleIterator iterator = storageEngine.search(olapContext.storageContext, sqlDigest,
                olapContext.returnTupleInfo);
        if (logger.isDebugEnabled()) {
            logger.debug("return TupleIterator...");
        }
        return iterator;
    }

然后调用GTCubeStorageQueryBase的search方法，在该方法中为每个cube segment创建一个CubeSegmentScanner：

    public ITupleIterator search(StorageContext context, SQLDigest sqlDigest, TupleInfo returnTupleInfo) {
        // 这一步有个很重要的步骤就是根据查询条件找到对应的cuboid（findCuboid）
        GTCubeStorageQueryRequest request = getStorageQueryRequest(context, sqlDigest, returnTupleInfo);
        List<CubeSegmentScanner> scanners = Lists.newArrayList();
        SegmentPruner segPruner = new SegmentPruner(sqlDigest.filter);
        for (CubeSegment cubeSeg : segPruner.listSegmentsForQuery(cubeInstance)) {
            CubeSegmentScanner scanner;
            scanner = new CubeSegmentScanner(cubeSeg, request.getCuboid(), request.getDimensions(), //
                    request.getGroups(), request.getDynGroups(), request.getDynGroupExprs(), //
                    request.getMetrics(), request.getDynFuncs(), //
                    request.getFilter(), request.getHavingFilter(), request.getContext());
            if (!scanner.isSegmentSkipped())
                scanners.add(scanner);
        }
        if (scanners.isEmpty())
            return ITupleIterator.EMPTY_TUPLE_ITERATOR;
        return new SequentialCubeTupleIterator(scanners, request.getCuboid(), request.getDimensions(),
                request.getDynGroups(), request.getGroups(), request.getMetrics(), returnTupleInfo, request.getContext(), sqlDigest);
    }
     
    public CubeSegmentScanner(CubeSegment cubeSeg, Cuboid cuboid, Set<TblColRef> dimensions, //
            Set<TblColRef> groups, List<TblColRef> dynGroups, List<TupleExpression> dynGroupExprs, //
            Collection<FunctionDesc> metrics, List<DynamicFunctionDesc> dynFuncs, //
            TupleFilter originalfilter, TupleFilter havingFilter, StorageContext context) {
        logger.info("Init CubeSegmentScanner for segment {}", cubeSeg.getName());
        this.cuboid = cuboid;
        this.cubeSeg = cubeSeg;
        //the filter might be changed later in this CubeSegmentScanner (In ITupleFilterTransformer)
        //to avoid issues like in https://issues.apache.org/jira/browse/KYLIN-1954, make sure each CubeSegmentScanner
        //is working on its own copy
        byte[] serialize = TupleFilterSerializer.serialize(originalfilter, StringCodeSystem.INSTANCE);
        TupleFilter filter = TupleFilterSerializer.deserialize(serialize, StringCodeSystem.INSTANCE);
        // translate FunctionTupleFilter to IN clause
        ITupleFilterTransformer translator = new BuiltInFunctionTransformer(cubeSeg.getDimensionEncodingMap());
        filter = translator.transform(filter);
        CubeScanRangePlanner scanRangePlanner;
        try {
            scanRangePlanner = new CubeScanRangePlanner(cubeSeg, cuboid, filter, dimensions, groups, dynGroups,
                    dynGroupExprs, metrics, dynFuncs, havingFilter, context);
        } catch (RuntimeException e) {
            throw e;
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
        scanRequest = scanRangePlanner.planScanRequest();
        // gtStorage为配置项kylin.storage.hbase.gtstorage, 默认值为
        // org.apache.kylin.storage.hbase.cube.v2.CubeHBaseEndpointRPC
        String gtStorage = ((GTCubeStorageQueryBase) context.getStorageQuery()).getGTStorage();
        scanner = new ScannerWorker(cubeSeg, cuboid, scanRequest, gtStorage, context);
    }

然后在CubeSegmentScanner中构建ScannerWorker:

    public ScannerWorker(ISegment segment, Cuboid cuboid, GTScanRequest scanRequest, String gtStorage,
            StorageContext context) {
        inputArgs = new Object[] { segment, cuboid, scanRequest, gtStorage, context };
        if (scanRequest == null) {
            logger.info("Segment {} will be skipped", segment);
            internal = new EmptyGTScanner();
            return;
        }
        final GTInfo info = scanRequest.getInfo();
        try {
            // 这里的rpc为org.apache.kylin.storage.hbase.cube.v2.CubeHBaseEndpointRPC
            IGTStorage rpc = (IGTStorage) Class.forName(gtStorage)
                    .getConstructor(ISegment.class, Cuboid.class, GTInfo.class, StorageContext.class)
                    .newInstance(segment, cuboid, info, context); // default behavior
             // internal为每个segment的查询结果，后面会调用iterator获取结果，calcite会将各个segment 
             // 的结果进行聚合, EnumerableDefaults中的aggregate
            internal = rpc.getGTScanner(scanRequest);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
        checkNPE();
    }

接着调用CubeHBaseEndpointRPC中的getGTScanner方法，然后调用runEPRange方法：

    private void runEPRange(final QueryContext queryContext, final String logHeader, final boolean compressionResult,
            final CubeVisitProtos.CubeVisitRequest request, final Connection conn, byte[] startKey, byte[] endKey,
            final ExpectedSizeIterator epResultItr) {
        final String queryId = queryContext.getQueryId();
        try {
            final Table table = conn.getTable(TableName.valueOf(cubeSeg.getStorageLocationIdentifier()),
                    HBaseConnection.getCoprocessorPool());
            table.coprocessorService(CubeVisitService.class, startKey, endKey, //
                    new Batch.Call<CubeVisitService, CubeVisitResponse>() {
                        public CubeVisitResponse call(CubeVisitService rowsService) throws IOException {
                            . . .
                            ServerRpcController controller = new ServerRpcController();
                            BlockingRpcCallback<CubeVisitResponse> rpcCallback = new BlockingRpcCallback<>();
                            try {
                                //发送请求到hbase的协处理器进行数据查询
                                rowsService.visitCube(controller, request, rpcCallback);
                                CubeVisitResponse response = rpcCallback.get();
                                if (controller.failedOnException()) {
                                    throw controller.getFailedOn();
                                }
                                return response;
                            } catch (Exception e) {
                                throw e;
                            } finally {
                                // Reset the interrupted state
                                Thread.interrupted();
                            }
                        }
                    }, new Batch.Callback<CubeVisitResponse>() {
                        // 接收到协处理器发回的查询结果
                        @Override
                        public void update(byte[] region, byte[] row, CubeVisitResponse result) {
                            . . .
                            // 获取hbase协处理器返回的查询结果中的相关状态数据
                            Stats stats = result.getStats();
                            queryContext.addAndGetScannedRows(stats.getScannedRowCount());
                            queryContext.addAndGetScannedBytes(stats.getScannedBytes());
                            queryContext.addAndGetReturnedRows(stats.getScannedRowCount()
                                    - stats.getAggregatedRowCount() - stats.getFilteredRowCount());
                            RuntimeException rpcException = null;
                            if (result.getStats().getNormalComplete() != 1) {
                                // record coprocessor error if happened
                                rpcException = getCoprocessorException(result);
                            }
                            queryContext.addRPCStatistics(storageContext.ctxId, stats.getHostname(),
                                    cubeSeg.getCubeDesc().getName(), cubeSeg.getName(), cuboid.getInputID(),
                                    cuboid.getId(), storageContext.getFilterMask(), rpcException,
                                    stats.getServiceEndTime() - stats.getServiceStartTime(), 0,
                                    stats.getScannedRowCount(),
                                    stats.getScannedRowCount() - stats.getAggregatedRowCount()
                                            - stats.getFilteredRowCount(),
                                    stats.getAggregatedRowCount(), stats.getScannedBytes());
                            if (queryContext.getScannedBytes() > cubeSeg.getConfig().getQueryMaxScanBytes()) {
                                rpcException = new ResourceLimitExceededException(
                                        "Query scanned " + queryContext.getScannedBytes() + " bytes exceeds threshold "
                                                + cubeSeg.getConfig().getQueryMaxScanBytes());
                            } else if (queryContext.getReturnedRows() > cubeSeg.getConfig().getQueryMaxReturnRows()) {
                                rpcException = new ResourceLimitExceededException(
                                        "Query returned " + queryContext.getReturnedRows() + " rows exceeds threshold "
                                                + cubeSeg.getConfig().getQueryMaxReturnRows());
                            }
                            if (rpcException != null) {
                                queryContext.stop(rpcException);
                                return;
                            }
                            try {
                                // 对返回的查询结果数据进行处理（查询结果数据可能被压缩）
                                if (compressionResult) {
                                    epResultItr.append(CompressionUtils.decompress(
                                            HBaseZeroCopyByteString.zeroCopyGetBytes(result.getCompressedRows())));
                                } else {
                                    epResultItr.append(
                                            HBaseZeroCopyByteString.zeroCopyGetBytes(result.getCompressedRows()));
                                }
                            } catch (IOException | DataFormatException e) {
                                throw new RuntimeException(logHeader + "Error when decompressing", e);
                            }
                        }
                    });
        } catch (Throwable ex) {
            queryContext.stop(ex);
        }
          . . .
       }

Kylin通过发送visitCube请求到HBase协处理器进行查询，协处理器中执行的函数位于CubeVisitService中，函数名为visitCube：

    public void visitCube(final RpcController controller, final CubeVisitProtos.CubeVisitRequest request,
            RpcCallback<CubeVisitProtos.CubeVisitResponse> done) {
        List<RegionScanner> regionScanners = Lists.newArrayList();
        HRegion region = null;
        StringBuilder sb = new StringBuilder();
        byte[] allRows;
        String debugGitTag = "";
        CubeVisitProtos.CubeVisitResponse.ErrorInfo errorInfo = null;
        // if user change kylin.properties on kylin server, need to manually redeploy coprocessor jar to update KylinConfig of Env.
        KylinConfig kylinConfig = KylinConfig.createKylinConfig(request.getKylinProperties());
        // 获取请求中的查询ID
        String queryId = request.hasQueryId() ? request.getQueryId() : "UnknownId";
        logger.info("start query {} in thread {}", queryId, Thread.currentThread().getName());
        try (SetAndUnsetThreadLocalConfig autoUnset = KylinConfig.setAndUnsetThreadLocalConfig(kylinConfig);
                SetThreadName ignored = new SetThreadName("Query %s", queryId)) { 
            final long serviceStartTime = System.currentTimeMillis();
            region = (HRegion) env.getRegion();
            region.startRegionOperation();
            debugGitTag = region.getTableDesc().getValue(IRealizationConstants.HTableGitTag);
            final GTScanRequest scanReq = GTScanRequest.serializer
                    .deserialize(ByteBuffer.wrap(HBaseZeroCopyByteString.zeroCopyGetBytes(request.getGtScanRequest())));
            // 获取查询超时时间
            final long deadline = scanReq.getStartTime() + scanReq.getTimeout();
            checkDeadline(deadline);
            List<List<Integer>> hbaseColumnsToGT = Lists.newArrayList();
            // 获取要查询的hbase的 Column列（例如，F1:M） 
            for (IntList intList : request.getHbaseColumnsToGTList()) {
                hbaseColumnsToGT.add(intList.getIntsList());
            }
            StorageSideBehavior behavior = StorageSideBehavior.valueOf(scanReq.getStorageBehavior());
            // 从request请求体中获RawScan
            final List<RawScan> hbaseRawScans = deserializeRawScans(
                    ByteBuffer.wrap(HBaseZeroCopyByteString.zeroCopyGetBytes(request.getHbaseRawScan())));
            appendProfileInfo(sb, "start latency: " + (serviceStartTime - scanReq.getStartTime()), serviceStartTime);
            final List<InnerScannerAsIterator> cellListsForeachRawScan = Lists.newArrayList();
            for (RawScan hbaseRawScan : hbaseRawScans) {
                if (request.getRowkeyPreambleSize() - RowConstants.ROWKEY_CUBOIDID_LEN > 0) {
                    //if has shard, fill region shard to raw scan start/end
                    updateRawScanByCurrentRegion(hbaseRawScan, region,
                            request.getRowkeyPreambleSize() - RowConstants.ROWKEY_CUBOIDID_LEN);
                }
                // 根据RawScan来构建HBase的Scan（确定startRow，stopRow，fuzzyKeys和hbase 
                // columns）
                Scan scan = CubeHBaseRPC.buildScan(hbaseRawScan);
                RegionScanner innerScanner = region.getScanner(scan);
                regionScanners.add(innerScanner);
                InnerScannerAsIterator cellListIterator = new InnerScannerAsIterator(innerScanner);
                cellListsForeachRawScan.add(cellListIterator);
            }
            final Iterator<List<Cell>> allCellLists = Iterators.concat(cellListsForeachRawScan.iterator());
            if (behavior.ordinal() < StorageSideBehavior.SCAN.ordinal()) {
                //this is only for CoprocessorBehavior.RAW_SCAN case to profile hbase scan speed
                List<Cell> temp = Lists.newArrayList();
                int counter = 0;
                for (RegionScanner innerScanner : regionScanners) {
                    while (innerScanner.nextRaw(temp)) {
                        counter++;
                    }
                }
                appendProfileInfo(sb, "scanned " + counter, serviceStartTime);
            }
            if (behavior.ordinal() < StorageSideBehavior.SCAN_FILTER_AGGR_CHECKMEM.ordinal()) {
                scanReq.disableAggCacheMemCheck(); // disable mem check if so told
            }
            final long storagePushDownLimit = scanReq.getStoragePushDownLimit();
            ResourceTrackingCellListIterator cellListIterator = new ResourceTrackingCellListIterator(allCellLists,
                    scanReq.getStorageScanRowNumThreshold(), // for old client (scan threshold)
                    !request.hasMaxScanBytes() ? Long.MAX_VALUE : request.getMaxScanBytes(), // for new client
                    deadline);
            IGTStore store = new HBaseReadonlyStore(cellListIterator, scanReq, hbaseRawScans.get(0).hbaseColumns,
                    hbaseColumnsToGT, request.getRowkeyPreambleSize(), behavior.delayToggledOn(),
                    request.getIsExactAggregate()); 
            IGTScanner rawScanner = store.scan(scanReq);
            // 这里会根据查询中是否有聚合来将rawScanner进行包装，包装成GTAggregateScanner来对这个 
            // region中查询出来的数据进行聚合操作
            IGTScanner finalScanner = scanReq.decorateScanner(rawScanner, behavior.filterToggledOn(),
                    behavior.aggrToggledOn(), false, request.getSpillEnabled());
            ByteBuffer buffer = ByteBuffer.allocate(BufferedMeasureCodec.DEFAULT_BUFFER_SIZE);
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream(BufferedMeasureCodec.DEFAULT_BUFFER_SIZE);//ByteArrayOutputStream will auto grow
            long finalRowCount = 0L;
            try {
     // 对查询的每条Record进行处理
     for (GTRecord oneRecord : finalScanner) {
                    buffer.clear();
                    try {
                        oneRecord.exportColumns(scanReq.getColumns(), buffer);
                    } catch (BufferOverflowException boe) {
                        buffer = ByteBuffer.allocate(oneRecord.sizeOf(scanReq.getColumns()) * 2);
                        oneRecord.exportColumns(scanReq.getColumns(), buffer);
                    }
                    outputStream.write(buffer.array(), 0, buffer.position());
                    finalRowCount++;
                    //if it's doing storage aggr, then should rely on GTAggregateScanner's limit check
                    if (!scanReq.isDoingStorageAggregation()
                            && (scanReq.getStorageLimitLevel() != StorageLimitLevel.NO_LIMIT
                                    && finalRowCount >= storagePushDownLimit)) {
                        //read one more record than limit
                        logger.info("The finalScanner aborted because storagePushDownLimit is satisfied");
                        break;
                    }
                }
            } catch (KylinTimeoutException e) {
                logger.info("Abort scan: {}", e.getMessage());
                errorInfo = CubeVisitProtos.CubeVisitResponse.ErrorInfo.newBuilder()
                        .setType(CubeVisitProtos.CubeVisitResponse.ErrorType.TIMEOUT).setMessage(e.getMessage())
                        .build();
            } catch (ResourceLimitExceededException e) {
                logger.info("Abort scan: {}", e.getMessage());
                errorInfo = CubeVisitProtos.CubeVisitResponse.ErrorInfo.newBuilder()
                        .setType(CubeVisitProtos.CubeVisitResponse.ErrorType.RESOURCE_LIMIT_EXCEEDED)
                        .setMessage(e.getMessage()).build();
            } finally {
                finalScanner.close();
            }
            long rowCountBeforeAggr = finalScanner instanceof GTAggregateScanner
                    ? ((GTAggregateScanner) finalScanner).getInputRowCount()
                    : finalRowCount;
            appendProfileInfo(sb, "agg done", serviceStartTime);
            logger.info("Total scanned {} rows and {} bytes", cellListIterator.getTotalScannedRowCount(),
                    cellListIterator.getTotalScannedRowBytes());
            //outputStream.close() is not necessary
            byte[] compressedAllRows;
            if (errorInfo == null) {
                allRows = outputStream.toByteArray();
            } else {
                allRows = new byte[0];
            }
            if (!kylinConfig.getCompressionResult()) {
                compressedAllRows = allRows;
            } else {
                // 对结果进行压缩传输，减少网络传输数据量
                compressedAllRows = CompressionUtils.compress(allRows);
            }
            appendProfileInfo(sb, "compress done", serviceStartTime);
            logger.info("Size of final result = {} ({} before compressing)", compressedAllRows.length, allRows.length);
            OperatingSystemMXBean operatingSystemMXBean = (OperatingSystemMXBean) ManagementFactory
                    .getOperatingSystemMXBean();
            double systemCpuLoad = operatingSystemMXBean.getSystemCpuLoad();
            double freePhysicalMemorySize = operatingSystemMXBean.getFreePhysicalMemorySize();
            double freeSwapSpaceSize = operatingSystemMXBean.getFreeSwapSpaceSize();
            appendProfileInfo(sb, "server stats done", serviceStartTime);
            sb.append(" debugGitTag:" + debugGitTag);
            CubeVisitProtos.CubeVisitResponse.Builder responseBuilder = CubeVisitProtos.CubeVisitResponse.newBuilder();
            if (errorInfo != null) {
                responseBuilder.setErrorInfo(errorInfo);
            }
            // 向请求端发送查询结果
            done.run(responseBuilder.//
                    setCompressedRows(HBaseZeroCopyByteString.wrap(compressedAllRows)).//too many array copies 
                    setStats(CubeVisitProtos.CubeVisitResponse.Stats.newBuilder()
                            .setFilteredRowCount(cellListIterator.getTotalScannedRowCount() - rowCountBeforeAggr)
                            .setAggregatedRowCount(rowCountBeforeAggr - finalRowCount)
                            .setScannedRowCount(cellListIterator.getTotalScannedRowCount())
                            .setScannedBytes(cellListIterator.getTotalScannedRowBytes())
                            .setServiceStartTime(serviceStartTime).setServiceEndTime(System.currentTimeMillis())
                            .setSystemCpuLoad(systemCpuLoad).setFreePhysicalMemorySize(freePhysicalMemorySize)
                            .setFreeSwapSpaceSize(freeSwapSpaceSize)
                            .setHostname(InetAddress.getLocalHost().getHostName()).setEtcMsg(sb.toString())
                            .setNormalComplete(errorInfo == null ? 1 : 0).build())
                    .build());
        } catch (DoNotRetryIOException e) {
            . . .
               } catch (IOException ioe) {
                 . . .
               } finally {
                      . . .
                   }
           . . .
        }
    }

例子：

Cube的涉及维度如下：

 ![img](/img/20190105165313771.png)

度量为：

 ![img](/img/20190105165320556.png)

维度和rowKey设计如下：

 ![img](/img/20190105165344905.png)

针对查询语句：select minute_start, count(*), sum(amount), sum(qty) from kylin_streaming_table where user_age in(10,11,12,13,14,15) and country in('CHINA','CANADA','INDIA') group by minute_start order by minute_start

如上述代码流程所示：

首先会根据查询涉及的列计算出cuboid的id为265（100001001）,由于涉及minute_start，而minute_start、hour_start和day_start为衍生维度，所以最终的cuboid为457（111001001），后面会根据查询的条件计算出scan，包括范围(5个维度列和3个度量列)为[null, null, null, 10, CANADA, null, null, null]（pkStart）到[null, null, null, 15, INDIA, null, null, null]（pkEnd）（后面的三个null值会被忽略掉）和根据笛卡尔积会计算出18个filter值（fuzzyKeys）：

 ![img](/img/20190105165402208.png)

用于后面查询过滤（使用FuzzyRowFilter过滤器）；还有就是查询hbase涉及的column也会根据查询语句中涉及的列来进行确定。然后后面会使用getGTScanner中的preparedHBaseScans来对scan的range（pkStart和pkEnd）和fuzzyKeys进行编码转化然后序列化形成请求体中的hbaseRawScan，后面的hbase协处理器就是用这个参数来构建HBase的Scan进行查询。

### 4.3. 总结

之前有测试Kylin的查询，发现其查询性能非常稳定，不会随查询的数据量的增长而大幅的增长，通过上面的源码分析基本可以知道其原因，Kylin通过Calcite将SQL语句解析优化后，得到具体的hbase的scan查询，然后使用hbase的协处理器（endpoint模式）来查询，将查询请求通过protobuf协议发送到hbase的regionServer，然后通过协处理器来进行过滤查询和初步聚合，最后会将查询结果进行压缩然后发回请求端，然后再进一步聚合得到最终的查询结果。

## 五.Cube构建过程中如何实现降维

https://blog.csdn.net/zengrui_ops/article/details/85857320



### 5.1维度简述

Kylin中Cube的描述类CubeDesc有两个字段，rowkey和aggregationGroups。

@JsonProperty("rowkey")
private RowKeyDesc rowkey;

@JsonProperty("aggregation_groups")
private List<AggregationGroup> aggregationGroups;

    @JsonProperty("rowkey")
    private RowKeyDesc rowkey;
    
    @JsonProperty("aggregation_groups")
    private List<AggregationGroup> aggregationGroups;

其中rowkey描述的是该Cube中所有维度，在将统计结果存储到HBase中，各维度在rowkey中的排序情况，如下是rowkey的一个样例，包含6个维度。在描述一种维度组合时，是通过二进制来表示。
如这6个维度，都包含时，是 111111。
如 111001，则表示只包含INSERT_DATE、VISIT_MONTH、VISIT_QUARTER、IS_CLICK这四个维度。
二进制从左到右表示的就是rowkey_columns中各个维度的包含与否，1包含，0不包含。
这样的一个二进制组合就是一个cuboid，用long整型表示。

```
"rowkey": {
    "rowkey_columns": [
        {
            "column": "DW_OLAP_CPARAM_INFO_VERSION2.INSERT_DATE",
            "encoding": "dict",
            "isShardBy": false
        },
        {
            "column": "DW_OLAP_CPARAM_INFO_VERSION2.VISIT_MONTH",
            "encoding": "dict",
            "isShardBy": false
        },
        {
            "column": "DW_OLAP_CPARAM_INFO_VERSION2.VISIT_QUARTER",
            "encoding": "dict",
            "isShardBy": false
        },
        {
            "column": "DW_OLAP_CPARAM_INFO_VERSION2.BUSINESS_TYPE",
            "encoding": "dict",
            "isShardBy": false
        },
        {
            "column": "DW_OLAP_CPARAM_INFO_VERSION2.SHOP_TYPE",
            "encoding": "dict",
            "isShardBy": false
        },
        {
            "column": "DW_OLAP_CPARAM_INFO_VERSION2.IS_CLICK",
            "encoding": "dict",
            "isShardBy": false
        },
    ]
}
```

而aggregationGroups则描述的是这些维度的分组情况，也就是在一个Cube中的所有维度，可以分成多个分组，每个分组就是一个AggregationGroup，各AggregationGroup之间是相互独立的。

对于所有的维度为什么要做分组？

在Kylin中会预先把所有维度的各种组合下的统计结果原先计算出来，假设维度有N个，那么维度的组合就有2^N中组合，比如N=6，则总的维度组合就有2^6=64种。

如果能够根据实际查询的需求，发现某些维度之间是不会有交叉查询的，那其实把这些维度组合的统计结果计算出来，也是浪费，因为后续的查询中，压根不会用到，这样既浪费了计算资源，更浪费了存储资源，所有可以按实际的查询需求，将维度进行分组，比如6个维度，分成2组，一组4个维度，一组2个维度，则总的维度组合则是2^4+2^2=20，比64小了很多，这里的分组这是举例说明分组，可以有效的减少维度组合，从而缩减存储空间，另外各个分组之间是可以有共享维度的，比如6个维度，可以分成两组，一组4个，另一组3个，两个分组中的共享维度，在后续计算中，其对应的统计结果不会被计算两次，只会计算一次，这也是Kylin聪明的地方。

一个AggragationGroup中包含includes和selectRule两个字段，其中includes就是该分组中包含了哪些维度，是一个字符串数组。

```
@JsonProperty("includes")
private String[] includes;

@JsonProperty("select_rule")
private SelectRule selectRule;
```

AggregationGroup详见 https://mp.weixin.qq.com/s?__biz=MzAwODE3ODU5MA==&mid=2653077921&idx=1&sn=89ae88bc63e71098166b74df7106c7bf&chksm=80a4bf50b7d3364692903aac3e901d09a516a8ff635e690e1e22b1d96abb4b2925c98cdace82&scene=21#wechat_redirect

强制维度——在每一个维度组合中都必须出现的维度，详见 https://mp.weixin.qq.com/s?__biz=MzAwODE3ODU5MA==&mid=2653077943&idx=1&sn=007d2ba345d0e25ec12807aa47f9913d&chksm=80a4bf46b7d33650465d33e20dac7edc09a7ad9308d77de6a501685c8ae00cba661c1d612074&scene=21#wechat_redirect

层级维度——则是那些有层级关系的维度，如省、市、县，详见 https://mp.weixin.qq.com/s?__biz=MzAwODE3ODU5MA==&mid=2653077929&idx=1&sn=c76ed1fbb745945a077d9ca99f159a4d&chksm=80a4bf58b7d3364e0346ad9c433d4e32c57d45f41b361ae653c64c7fcebab21238793d2f66cb&scene=21#wechat_redirect

联合维度——则是那些要么不出现，要出现就必须一起出现的维度，详见 https://mp.weixin.qq.com/s?__biz=MzAwODE3ODU5MA==&mid=2653077926&idx=1&sn=a0037628bd102ec8e607d67204cbfa7c&chksm=80a4bf57b7d336419896c9e801a51f08ead2f7727d0d0ec0f9e3b7799ae3c302ebea54f93cc0&scene=21#wechat_redirect

如下是只有一个分组的样例。

```
"aggregation_groups": [
    {
        "includes": [
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCID_SEARCH",
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.BUSINESS_TYPE",
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCID0”,
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCID1”,
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCID2”,
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCID3",
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCNAME0",
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCNAME1",
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCNAME2",
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCNAME3",
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.INSERT_DATE",
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.SHOP_TYPE”
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.USERID",
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.SHOPID"
                    ],
        "select_rule": {
            "hierarchy_dims": [
                [
                    "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCID0",
                    "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCID1",
                    "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCID2",
                    "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCID3"
                ],
                [
                    "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCNAME0",
                    "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCNAME1",
                    "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCNAME2",
                    "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.FCNAME3"
                ]
            ],
        "mandatory_dims": [
                            "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.INSERT_DATE",
                            "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.BUSINESS_TYPE"
                ],
        "joint_dims": [
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.USERID",
                        "DW_OLAP_AD_NORMAL_CONTRAST_VERSION2.SHOPID"
                    ]
        }
    }
]
```

### 5.2cuboid的有效性判断

在进行降维分析之前，先简单减少一下，给定的一个cuboid的，比如 110011 ，这样一个cuboid，如何判断在一个AggregationGroup中是否是有效的？判断逻辑在Cuboid类的isValid方法中，就是用来判断给定的一个cuboidID，在一个AggregationGroup中是否是一个合法有效的cuboidID。

static boolean isValid(AggregationGroup agg, long cuboidID) {
    // 前面说明，一个cuboidID就是一组维度的组合，1位包含，0为不包含，所以cuboidID必定大于0
    if (cuboidID <= 0) {
        return false; //cuboid must be greater than 0    
    }

    // 一个cuboidID在一个AggregationGroup中是否有效的前提，是它包含的维度必须都要是该AggregationGroup中的维度才行
    // agg.getPartialCubeFullMask()获取的就是该AggregationGroup中所有维度组成的一个掩码
    if ((cuboidID & ~agg.getPartialCubeFullMask()) != 0) {
        return false; //a cuboid's parent within agg is at most partialCubeFullMask    
    }
    
    // 接下来则分别进行了强制维度、层级维度、联合维度的校验，都校验通过时，才能算是有效合法的
    return checkMandatoryColumns(agg, cuboidID) && checkHierarchy(agg, cuboidID) && checkJoint(agg, cuboidID);
}

从上面的逻辑可以看出，判断一个cuboidID在一个AggregationGroup中是否合法有效的逻辑很清晰，首先该cuboidID要至少包含一个维度，然后包含的维度需要是该AggregationGroup中维度的子集，最后就是在进行强制维度、层级维度、联合维度的规则校验。

强制维度的校验逻辑，简单说就是cuboidID中需要包含强制维度的所有维度，另外当，cuboidID中只包含强制维度的维度时，则根据配置中是否允许这种情况，进行判断，具体逻辑如下：

```java
private static boolean checkMandatoryColumns(AggregationGroup agg, long cuboidID) {
    // agg.getMandatoryColumnMask() 获取的是所有强制维度组成的二进制
    long mandatoryColumnMask = agg.getMandatoryColumnMask();

    // 如果没有包含所有强制维度,则返回false 
    if ((cuboidID & mandatoryColumnMask) != mandatoryColumnMask) {
        return false;
    } else {
        // 如果包含了整个cube的所有维度，则总是返回true的
        if (cuboidID == getBaseCuboidId(agg.getCubeDesc())) {
            return true;
        }
    
        // 如果配置中允许该cuboidID中的维度都是强制维度,则返回true 
        // 如果不允许全部,则cuboidID中需要包含除强制维度以为的维度        
        return agg.isMandatoryOnlyValid() || (cuboidID & ~mandatoryColumnMask) != 0;
    }
}
```

层级维度的校验逻辑，校验逻辑简单明了，只要cuboidID中包含某个层级维度中的维度，则必须与该层级维度的某个具体的组合相匹配才行，否则就是无效的。

比如省、市、县这样一个层级维度，当cuboidID中包含省、市、县这三个维度中的某些维度的时候，也即是cuboidID & hierarchyMasks.fullMask 大于0的时候，则cuboidID中包含的这个层级维度的组合只能是 《省》、《省、市》、《省、市、县》这三种组合，如果包含的是《省、县》或者《市、县》或者其他组合，则都是无效的。具体逻辑如下。

```java
private static boolean checkHierarchy(AggregationGroup agg, long cuboidID) {
    List<HierarchyMask> hierarchyMaskList = agg.getHierarchyMasks();
    // if no hierarchy defined in metadata    
    if (hierarchyMaskList == null || hierarchyMaskList.size() == 0) {
        return true;
    }

    hier: for (HierarchyMask hierarchyMasks : hierarchyMaskList) {
        // 如果包含了某个层级维度组中的维度,则就需要包含该层级维度组中的某种具体组合才行     
       long result = cuboidID & hierarchyMasks.fullMask;
        if (result > 0) {
            for (long mask : hierarchyMasks.allMasks) {
                if (result == mask) {
                    continue hier;
                }
            }
            return false;
        }
    }
    return true;
}
```

联合维度的校验逻辑，联合维度顾名思义，就是连在一起的，要么一起出现，要么都不出现，校验逻辑如下：

```java
private static boolean checkJoint(AggregationGroup agg, long cuboidID) {
    for (long joint : agg.getJoints()) {
        long common = cuboidID & joint;
        // 如果包含了某个联合组中的维度,则就必须包含该联合组中的全部维度      
    if (!(common == 0 || common == joint)) {
            return false;
        }
    }
    return true;
}
```

上述分析了判断一个cuboidID在一个AggregationGroup中是否有效的判断，那判断一个cuboidID在一个Cube中是否有效，就是判断这个cuboidID在该Cube的所有AggregationGroup中都是有效的，逻辑如下：

```
public static boolean isValid(CubeDesc cube, long cuboidID) {
    //base cuboid is always valid    
    if (cuboidID == getBaseCuboidId(cube)) {
        return true;
    }

    // 就是这个循环，遍历了所有的AggregationGroup
    for (AggregationGroup agg : cube.getAggregationGroups()) {
        if (isValid(agg, cuboidID)) {
            return true;
        }
    }
    return false;
}
```
### 5.3降维逻辑

对于维度的升降操作主要在类CuboidScheduler中，对应的方法则是
```
public Set<Long> getPotentialChildren(long parent) {
    ...
}

public long getParent(long child) {
    ...
}
```
首先来看getPotentialChildren这个方法，就是给定一个cuboid，找出其所有的潜在的子cuboid，这里的子cuboid就是说parent通过减少一个或者多个维度，得到的新的cuboid。
```
public Set<Long> getPotentialChildren(long parent) {
    // Cuboid.getBaseCuboid(cubeDesc).getId() 获取的就是该Cube的所有维度都存在的cuboid，比如6个维度，则111111
    // Cuboid.isValid(cubeDesc, parent) 是判断parent这个cuboid是不是一个有效的cuboid
    // 这里就是判断给的parent这个cuboid是否是一个有效的cuboid
    if (parent != Cuboid.getBaseCuboid(cubeDesc).getId() && !Cuboid.isValid(cubeDesc, parent)) {
        throw new IllegalStateException();
    }

    HashSet<Long> set = Sets.newHashSet();
    if (Long.bitCount(parent) == 1) {
        // 如果parent中只包含一个维度了，则就不需要在进一步降维了，再降维就是空了     
        return set;
    }
    
    // 如果parent包含了Cube中的所有维度
    if (parent == Cuboid.getBaseCuboidId(cubeDesc)) {
        //那么这个时候，parent的子cuboidID中，就应该包含Cube中的所有AggregationGroup的BaseCuboidID      
        for (AggregationGroup agg : cubeDesc.getAggregationGroups()) {
            long partialCubeFullMask = agg.getPartialCubeFullMask();
            if (partialCubeFullMask != parent && Cuboid.isValid(agg, partialCubeFullMask)) {
                set.add(partialCubeFullMask);
            }
        }
    }
    
    // Cuboid.getValidAggGroupForCuboid(cubeDesc, parent)就是找出Cube中，parent在其中合法的AggregationGroup
    // 然后依次遍历这些AggregationGroup
    for (AggregationGroup agg : Cuboid.getValidAggGroupForCuboid(cubeDesc, parent)) {
    
        // 对于普通的维度，就是除去强制维度、层级维度、联合维度之后，还剩下的维度        
        for (long normalDimMask : agg.getNormalDims()) {
            long common = parent & normalDimMask;
            long temp = parent ^ normalDimMask;
            // 对于每一个普通维度             
            // 如果在parent中存在,则将其从parent中移除后降维得到的temp,如果在该group中,仍然是一个有效的cuboidID,则算一个parent的child 
           if (common != 0 && Cuboid.isValid(agg, temp)) {
                set.add(temp);
            }
        }
    
        // 特别注意一下,这里为了简单理解,所以假设的parent和层级维度的取值,都是顺序的,
        // dims一次为00000100、00000010、00000001,         
        // 真实的情况是dims的取值可能为 00000001、10000000、00010000,这里的顺序都是反映了该维度在rowkey中的顺序         *
    
        // 针对层级维度的降维         
        // 建设parent为 11111111 
        // 层级维度为 fullMask 00000111 , allMasks 为 00000100、00000110、00000111, dims为 00000100、00000010、00000001
        // for (int i = hierarchyMask.allMasks.length - 1; i >= 0; i--)这层循环,allMasks[i]遍历顺序为 00000111、00000110、00000100
        // 比如第一次循环allMasks[i]取00000111,与parent与操作,就是判断allMasks[i]中的维度是否都包含在parent中,如果都包含在parent中,进入if条件
        // 这时候取出allMasks[i]为00000111,这个组合中的最低级的维度为00000001,然后判断该维度是否是联合维度的一员,如果不是,进入if条件         
        // 然后将层级维度的最末一级去掉,这里就是去掉00000001这一维度,去掉后的cuboidID为 11111111^00000001=11111110         
        // 然后判断11111110是否在该group中是一个有效的cuboidID,如果是,则作为parent的child         
        for (AggregationGroup.HierarchyMask hierarchyMask : agg.getHierarchyMasks()) {
            for (int i = hierarchyMask.allMasks.length - 1; i >= 0; i--) {
                 // 只有当层级维度中的某个组合中的维度都在parent中时,才进入if条件
                if ((parent & hierarchyMask.allMasks[i]) == hierarchyMask.allMasks[i]) {
                    // 所有联合维度中都不包含当前层级维度组合中的最低维度时,进入if条件
                    if ((agg.getJointDimsMask() & hierarchyMask.dims[i]) == 0) {
                            if (Cuboid.isValid(agg, parent ^ hierarchyMask.dims[i])) {
                                //only when the hierarchy dim is not among joints                            
                                set.add(parent ^ hierarchyMask.dims[i]);
                            }
                    }
                    break;    //if hierarchyMask 111 is matched, won't check 110 or 100                }
            }
        }
    
        //joint dim section        
        // 联合维度相对比较简单,如果包含某个联合维度,则将其全部去除,再判断其有效性,如果有效,则加入parent的child队列 
        for (long joint : agg.getJoints()) {
            if ((parent & joint) == joint) {
                if (Cuboid.isValid(agg, parent ^ joint)) {
                    set.add(parent ^ joint);
                }
            }
        }
    
    }
    
    return set;
}
```
降维操作主要是就是针对3类维度进行降维操作，普通维度（一个AggregationGroup的所有维度除去强制维度、层级维度、联合维度之后还剩余的维度）、层级维度、联合维度。

普通维度的降维就是首先判断parent是否包含该普通维度，如果包含，则将其从parent中移除，然后判断移除后的cuboidID在该AggregationGroup中是否有效合法；

层级维度的降维，首先parent中需要包含某个层级维度的某种组合，然后再将该层级维度组合中的最末级的维度移除，得到的cuboidID再去校验合法性；

联合维度的降维最直接明了，包含就全部去除，然后校验合法性。

以上就是通过一个给定的cuboidID，获取所有可能的子cuboidID的逻辑，也就是降维的过程。

### 5.4升维逻辑

那既然进行降维操作已经有了，为什么还要有一个getParent方法呢？其实从方法名中可以一探一二，getPotentialChildren获取可能的孩子，这就是说getPotentialChildren方法的逻辑获取的所有child只是说，可能是parent的child，但未必真的是，所以在getSpanningCuboid方法中，先通过getPotentialChildren获取了所以潜在的child，然后又对每一个potential，都去获取其对应的父亲，看是否与给定的这个parent一致，如果一致，才说明父子相认，也就是父亲认了儿子，同时也需要儿子认了父亲才行。
```
public List<Long> getSpanningCuboid(long cuboid) {
    if (cuboid > max || cuboid < 0) {
        throw new IllegalArgumentException("Cuboid " + cuboid + " is out of scope 0-" + max);
    }

    List<Long> result = cache.get(cuboid);
    if (result != null) {
        return result;
    }
    
    result = Lists.newArrayList();
    Set<Long> potentials = getPotentialChildren(cuboid);
    for (Long potential : potentials) {
        if (getParent(potential) == cuboid) {
            result.add(potential);
        }
    }
    
    cache.put(cuboid, result);
    return result;
}
```
    接着看下getParent的逻辑，getParent方法的逻辑与getPotentialChildren的逻辑刚好反过来，是一个升维的过程。

```
public long getParent(long child) {
    List<Long> candidates = Lists.newArrayList();
    long baseCuboidID = Cuboid.getBaseCuboidId(cubeDesc);

    // 如果该child等于fullMask 或者 该child不是有效的cuboidID,则抛异常  
    // 这也好理解，fullMask是不可能存在父亲的，因为它就是所有cuboidID的老祖宗
   if (child == baseCuboidID || !Cuboid.isValid(cubeDesc, child)) {
        throw new IllegalStateException();
    }

    // 这里与getPotentialChildren一样，也是首选找出所有可能的AggregationGroup，然后开始遍历
    for (AggregationGroup agg : Cuboid.getValidAggGroupForCuboid(cubeDesc, child)) {
    
        // thisAggContributed 这个变量标识 当前该AggregationGroup是否已经贡献出了一个parent
       boolean thisAggContributed = false;
    
        // 这里也好理解，如果child就是该AggregationGroup的基cuboidID，那么它的父亲只能是Cube的基cuboidID
       if (agg.getPartialCubeFullMask() == child) {        
            return baseCuboidID;
    
        }
    
        //+1 dim
        //add one normal dim (only try the lowest dim)        
        // 这里只会添加lowest维度,是跟最后的Collections.min有呼应的         
        // 因为最后只会选择所有满足条件中的维度数最少,在相同维度数中,值最小的那个候选者,         
        // 所以这里就没有必要把高位的维度添加进去,反正最后也会被过滤掉
        // 这一点在后面的升维中都会有所体现
       long normalDimsMask = (agg.getNormalDimsMask() & ~child);
        if (normalDimsMask != 0) {
            candidates.add(child | Long.lowestOneBit(normalDimsMask));
            thisAggContributed = true;
        }
    
        // 开始层级维度的升维
        for (AggregationGroup.HierarchyMask hierarchyMask : agg.getHierarchyMasks()) {
            if ((child & hierarchyMask.fullMask) == 0) {
                // 这里只加入最高级的那个维度,其他维度不继续处理的原因,也是跟最后的排序,只取维度最少有关 
                candidates.add(child | hierarchyMask.dims[0]);
                thisAggContributed = true;
            } else {
                for (int i = hierarchyMask.allMasks.length - 1; i >= 0; i--) {
                    // 只有与层级维度的某个组合匹配时，才会进入if条件
                    if ((child & hierarchyMask.allMasks[i]) == hierarchyMask.allMasks[i]) {
                        if (i == hierarchyMask.allMasks.length - 1) {
                            // 感觉这里应该用break,而不是continue,虽然这里用contine也不会有问题
                            // 如果某个层级维度的所有维度都已经在child中,则child无法再添加维度来形成parent了
                            // 比如省、市、县，如果child中已经包含了省、市、县，则没法再进一步添加这个层级的维度了
                        continue;//match the full hierarchy                        }
                        if ((agg.getJointDimsMask() & hierarchyMask.dims[i + 1]) == 0) {
                            // 如果是 省、市，则可以添加一个 县 维度进来，如果是省，则可以添加一个 市 维度进来
                            if ((child & hierarchyMask.dims[i + 1]) == 0) {
                                //only when the hierarchy dim is not among joints                                
                                candidates.add(child | hierarchyMask.dims[i + 1]);
                                thisAggContributed = true;
                            }
                        }
                        // 这里的break，就是说，如果已经有一个多维层级组合满足要求了，就无需进一步检查少维度的层级组合了
                        // 比如已经 省、市，这个组合已经满足了，就没必要再去检查 省 这个维度组合了。
                        break;//if hierarchyMask 111 is matched, won't check 110 or 100                    }
                }
            }
        }
    
        // 如果经过上面的普通维度和层级维度,添加维度操作后,已经找到了候选parent,则无需再进行联合维度的操作
        // 因为联合维度至少会加2个维度进来,根据最后的Collections.min,会优先选维度数少的
       if (thisAggContributed) {
            //next section is going to append more than 2 dim to child            
            //thisAggContributed means there's already 1 dim added to child            
            //which can safely prune the 2+ dim candidates.            
            continue;
        }
    
        //2+ dim candidates        
        // 联合维度的很简单，如果没有包含，则直接全部加入
       for (long joint : agg.getJoints()) {
            if ((child & joint) == 0) {
                candidates.add(child | joint);
            }
        }
    }
    
    if (candidates.size() == 0) {
        throw new IllegalStateException();
    }
    
    // 这里的Collections.min就是上述很多地方可以提前结束的原因
    return Collections.min(candidates, Cuboid.cuboidSelectComparator);
}
```
 这个升维的过程，在进入AggregationGroup遍历后，主要通过增加一个维度的升维，和增加2个或以上维度的升维，主要也即是联合维度了。

对于增加1个维度的升维：
对于普通维度，则从所有普通维度中，选择一个在rowkey中排在最后面的那个维度，然后添加到child中；

对于层级维度，如果是该层级维度中的维度都不包含，则取该层级维度中最高级的那个维度添加到child中；如果是child只包含了该层级维度中所有维度的部分维度，比如对于省、市、县这个层级维度，只包含了省或者省市，则可以新增一个市或者县到child中；

如果在1个维度的升维中已经找到了一个候选的parent，则联合维度就不需在进行了，因为联合维度至少会加入两个维度。

再来看一下getParent方法的最后一句代码，就明白为什么升维的过程中，很多潜在的parent可以直接忽略掉。

Cuboid.cuboidSelectComparator的实现如下。

也就是对于任何两个cuboidID，先从中选出包含维度少的那个cuboidID，如果两个cuboidID包含的维度数相同，则在进一步比较，值小的为所需要的cuboidID。

也即是getParent获取的所有候选parent的集合candidates，经过这个比较器排序后，最小的那个cuboidID，就是包含维度最少，且在相同纬度的不同cuboidID中，值是最小的那个。
```
//smaller is better
public final static Comparator<Long> cuboidSelectComparator = new Comparator<Long>() {
    @Override    
    public int compare(Long o1, Long o2) {
        return ComparisonChain.start().compare(Long.bitCount(o1), Long.bitCount(o2)).compare(o1, o2).result();
    }
};
```



## 六.Cube构建算法

http://cxy7.com/articles/2018/06/09/1528549073259.html



### 6.1Layer Cubing算法

也可称为“逐层算法”，通过启动N+1轮MapReduce计算。第一轮读取原始数据（RawData），去掉不相关的列，只保留相关的。同时对维度列进行压缩编码，第一轮的结果，我们称为Base   Cuboid，此后的每一轮MapReuce，输入是上一轮的输出，以重用之前的计算结果，去掉要聚合的维度，计算出新的Cuboid，以此向上，直到最后算出所有的Cuboid。

![by-layer-cubing.png](/img/1528546585112020323.png)

如上图所示，展示了一个4维的Cube构建过程

此算法的Mapper和Reducer都比较简单。Mapper以上一层Cuboid的结果（Key-Value对）作为输入。由于Key是由各维度值拼接在一起，从其中找出要聚合的维度，去掉它的值成新的Key，并对Value进行操作，然后把新Key和Value输出，进而Hadoop   MapReduce对所有新Key进行排序、洗牌（shuffle）、再送到Reducer处；Reducer的输入会是一组有相同Key的Value集合，对这些Value做聚合计算，再结合Key输出就完成了一轮计算。

每一轮的计算都是一个MapReduce任务，且串行执行； 一个N维的Cube，至少需要N次MapReduce Job。



**算法优点**

- 此算法充分利用了MapReduce的能力，处理了中间复杂的排序和洗牌工作，故而算法代码清晰简单，易于维护；
- 受益于Hadoop的日趋成熟，此算法对集群要求低，运行稳定；在内部维护Kylin的过程中，很少遇到在这几步出错的情况；即便是在Hadoop集群比较繁忙的时候，任务也能完成。



**算法缺点**

- 当Cube有比较多维度的时候，所需要的MapReduce任务也相应增加；由于Hadoop的任务调度需要耗费额外资源，特别是集群较庞大的时候，反复递交任务造成的额外开销会相当可观；
- 由于Mapper不做预聚合，此算法会对Hadoop  MapReduce输出较多数据;  虽然已经使用了Combiner来减少从Mapper端到Reducer端的数据传输，所有数据依然需要通过Hadoop  MapReduce来排序和组合才能被聚合，无形之中增加了集群的压力;
- 对HDFS的读写操作较多：由于每一层计算的输出会用做下一层计算的输入，这些Key-Value需要写到HDFS上；当所有计算都完成后，Kylin还需要额外的一轮任务将这些文件转成HBase的HFile格式，以导入到HBase中去；
- 总体而言，该算法的效率较低，尤其是当Cube维度数较大的时候；时常有用户问，是否能改进Cube算法，缩短时间。



### 6.2 Fast(in-mem) Cubing算法

也被称作“逐段”(By Segment) 或“逐块”(By Split) 算法

从1.5.x开始引入该算法，利用Mapper端计算先完成大部分聚合，再将聚合后的结果交给Reducer，从而降低对网络瓶颈的压力。



**主要思想:**

对Mapper所分配的数据块，将它计算成一个完整的小Cube 段（包含所有Cuboid）；

每个Mapper将计算完的Cube段输出给Reducer做合并，生成大Cube，也就是最终结果；下图解释了此流程

![by-segment-cubing.png](/img/1528546572368066122.png)



与旧算法的不同之处:

- Mapper会利用内存做预聚合，算出所有组合；Mapper输出的每个Key都是不同的，这样会减少输出到Hadoop MapReduce的数据量，Combiner也不再需要；
- 一轮MapReduce便会完成所有层次的计算，减少Hadoop任务的调配。



**举一个例子**

一个cube有4个维度：A，B，C，D;每个Mapper都有100万个源记录要处理;Mapper中的列基数是Car（A），Car（B），Car（C）和Car（D）; 

当将源记录聚集到base   cuboid（1111）时，使用旧的“逐层”算法，Mapper将向Hadoop输出1百万条记录;使用快速立方算法，在预聚合之后，它只向Hadoop输出[distinct  A，B，C，D]记录的数量，这肯定比源数据小;在正常情况下，它可以是源记录大小的1/10到1/1000; 

当从父cuboid聚合到子cuboid时，从base  cuboid（1111）到3维cuboid 0111，将会聚合维度A;我们假设维度A与其他维度是独立的，聚合后，cuboid  0111的维度约为base cuboid的1 / Card（A）;所以在这一步输出将减少到原来的1 / Card（A）。

总的来说，假设维度的平均基数是Card（N），从Mapper到Reducer的写入记录可以减少到原始维度的1 / Card（N）; Hadoop的输出越少，I/O和计算越少，性能就越好。



**子立方体生成树(Cuboid Spanning Tree)的遍历次序**

在旧算法中，Kylin按照层级，也就是广度优先遍历(Broad  First Search)的次序计算出各个Cuboid；在快速Cube算法中，Mapper会按深度优先遍历（Depth First  Search）来计算各个Cuboid。深度优先遍历是一个递归方法，将父Cuboid压栈以计算子Cuboid，直到没有子Cuboid需要计算时才出栈并输出给Hadoop；最多需要暂存N个Cuboid，N是Cube维度数。

- 采用DFS，是为了兼顾CPU和内存：
- 从父Cuboid计算子Cuboid，避免重复计算；
- 只压栈当前计算的Cuboid的父Cuboid，减少内存占用。

![cube-spanning-tree.png](/img/1528547284221042953.png)

上图是一个四维Cube的完整生成树；

按照DFS的次序，在0维Cuboid  输出前的计算次序是 ABCD -> BCD -> CD -> D -> ， ABCD, BCD,  CD和D需要被暂存；在被输出后，D可被输出，内存得到释放；在C被计算并输出后，CD就可以被输出； ABCD最后被输出。

使用DFS访问顺序，Mapper的输出已完全排序（除了一些特殊情况），因为Cuboid ID位于行键的开始位置，而内部Cuboid中的行已排序：

```
`0000``0001[D0]``0001[D1]``....``0010[C0]``0010[C1]``....``0011[C0][D0]``0011[C0][D1]``....``....``1111[A0][B0][C0][D0]``....`
```

由于mapper的输出已经排序，Hadoop的排序效率会更高，

此外，mapper的预聚合发生在内存中，这样可以避免不必要的磁盘和网络I / O，并且减少了Hadoop的开销;

在开发阶段，我们在mapper中遇到了OutOfMemory错误;这可能发生在：



- Mapper的JVM堆大小很小;
- 使用“dictinct count”度量（HyperLogLog占用空间）
- 生成树太深（维度太多）;
- 给Mapper的数据太大

我们意识到Kylin不能认为Mapper总是有足够的内存;Cubing算法需要自适应各种情况;

当主动检测到OutOfMemory错误时，会优化内存使用并将数据spilling到磁盘上;结果是有希望的，OOM错误现在很少发生;



**优缺点**

优点

它比旧的方法更快;从我们的比较测试中可以减少30％到50％的build总时间;

它在Hadoop上产生较少的工作负载，并在HDFS上留下较少的中间文件;

Cubing和Spark等其他立方体引擎可以轻松地重复使用该立方体代码;

缺点

该算法有点复杂;这增加了维护工作;

虽然该算法可以自动将数据spill到磁盘，但它仍希望Mapper有足够的内存来获得最佳性能;

用户需要更多知识来调整立方体;



### 6.3 By-layer Spark Cubing算法

我们知道，RDD（弹性分布式数据集）是Spark中的一个基本概念。  N维立方体的集合可以很好地描述为RDD，N维立方体将具有N + 1个RDD。这些RDD具有parent/child关系，因为parent  RDD可用于生成child RDD。通过将父RDD缓存在内存中，子RDD的生成可以比从磁盘读取更有效。下图描述了这个过程



![spark-cubing-layer.png](/img/1528548363447061649.png)



**改进**

- 每一层的cuboid视作一个RDD
- 父亲RDD被尽可能cache到内存
- RDD被导出到sequence file
- 通过将“map”替换为“flatMap”，以及把“reduce”替换为“reduceByKey”，可以复用大部分代码



**Spark中Cubing的过程**

下图DAG，它详细说明了这个过程：

在“Stage 5”中，Kylin使用HiveContext读取中间Hive表，然后执行一个一对一映射的“map”操作将原始值编码为KV字节。完成后Kylin得到一个中间编码的RDD。

在“Stage  6”中，中间RDD用一个“reduceByKey”操作聚合以获得RDD-1，这是base  cuboid。接下来，在RDD-1上做一个“flatMap”（一对多map），因为base  cuboid有N个子cuboid。以此类推，各级RDD得到计算。在完成时，这些RDD将完整地保存在分布式文件系统，但可以缓存在内存中用于下一级的计算。当生成子cuboid时，它将从缓存中删除。

![spark-dag.png](/img/1528548691210002263.png)



### 6.4 性能测试

![image.png](/img/1528549701204082092.png)

![spark-mr-performance.png](/img/1528548758980066743.png)

在所有这三种情况下，Spark都比MR快，总体而言，它可以减少约一半的时间。



### 6.5不同Cubing算法的对比

![image.png](/img/1528549911910049594.png)









# Kylin构建cube优化

(https://www.cnblogs.com/ulysses-you/p/9483634.html) 

## 前言

下面通过对kylin构建cube流程的分析来介绍cube优化思路。

 

## 创建hive中间表

kylin会在cube构建的第一步先构建一张hive的中间表，该表关联了所有的事实表和维度表，也就是一张宽表。

优化点：

1. hive表分区优化，在构建宽表的时候，kylin需要遍历hive表，事实表和维度表如果是分区表，那么会减少遍历时间

2. hive相关配置调整，join相关配置，mapreduce相关配置等

 

创建完成后，为了防止文件大小不一致的情况，kylin又基于hive做了一次重均衡操作，

`kylin.engine.mr.mapper-input-rows=1000000`，默认每个文件包含100w的数据量

 

代码 `CreateFlatHiveTableStep`

## 找出所有维度的基数

通过HyperLogLog 算法找出去重后的维度列，如果某个维度的基数很大，那么这种维度为被称为ultra high cardinality column（UHC），也就是超高基数维度。那么如何处理这类维度呢？

### 业务层处理UHC

比如时间戳维度基数可能是亿级的，可以转成为日期，基数降到几十万.

 

### 技术层处理UHC

kylin通过mapreduce进行此步骤，在reduce端，一个维度用一个reduce去重，因此当某个维度的基数很大时，会导致该维度所在的reduce运行很慢，甚至内存溢出，为了应对这种场景，kylin提供了两种解决方案

1. 全局唯一维度，也就是在count_dintinct中选择0错误率的统计分析。

2. 需要被shard by的维度，在rowkey构建时配置的维度。

接着可以通过配置`kylin.engine.mr.uhc-reducer-count=1`来声明这些列需要被分割成多少个reducer执行

 

当然，kylin也支持基于cuboid个数来进行reducer个数的分配，`kylin.engine.mr.hll-max-reducer-number=1`，默认情况下kylin不开启此功能，可以修改配置来提高最小个数；然后通过配置`kylin.engine.mr.per-reducer-hll-cuboid-number`来调整具体的reduce数量



```
int nCuboids = cube.getCuboidScheduler().getAllCuboidIds().size();
int shardBase = (nCuboids - 1) / cube.getConfig().getHadoopJobPerReducerHLLCuboidNumber() + 1;

int hllMaxReducerNumber = cube.getConfig().getHadoopJobHLLMaxReducerNumber();
if (shardBase > hllMaxReducerNumber) {
    shardBase = hllMaxReducerNumber;
}
```

最终的reducer数量由UHC和cuboids两个部分相加得到，具体代码参考

`FactDistinctColumnsReducerMapping`构造函数

 

\# 配置UHC增加另外步骤，需要配置zk的地址（作为全局分布式锁使用）

\# 因为在跑mapreduce的过程中，kylin没有将hbase-site.xml等配置上传到yarn，所以只能在kylin.properties中额外配置一遍

kylin.engine.mr.build-uhc-dict-in-additional-step=true

kylin.env.zookeeper-connect-string=host:port,host:port

 

代码 `FactDistinctColumnsJob`, `UHCDictionaryJob`

## 构建维度字典

找出所有维度的基数后，kyin为每个维度构建一个数据字典，字典的metadata存储在hdfs上，实际数据存储在hbase

**字典在hdfs的路径规则为**

kylin/kylin_meta_data/kylin-$jobid/%cubeid/metadata/dict/$catalog.$table/$dimension/$uuid.dict

 

**字典数据在hbase的rowkey规则为**

/dict/$catalog.$table/$dimension/$uuid.dict

 

### rowkey长度

过长的rowkey会占用很大的存储空间，所以需要对rowkey长度进行控制。

当前kylin直接在当前进程内做了字典编码，也就是把string映射成int，如果维度列的基数很大，那么可能会出现内存溢出的情况（当列的基础大于1kw），这时候就需要考虑更改维度列的编码方式，改用`fixed_length`等。如果一个维度的长度超过`fixed_length`，那么超过的部分会被截断。

 

### rowkey构建

对rowkey的构建也有一定的要求，一般而言，需要把基数大的字段放在前面，这样可以在scan的过程中尽可能的跳过更多的rowkey。

另一方面将基数小的列放在rowkey的后面，可以减少构建的重复计算，有些cuboid可以通过一个以上的父cuboid聚合而成，在这种情况下，Kylin将会选择最小的父cuboid。例如，AB能够通过ABC（id：1110）和ABD（id：1101）聚合生成，因此ABD会被作为父cuboid使用，因为它的id比ABC要小。基于以上处理，如果D的基数很小，那么此次聚合操作就会花费很小的代价。因此，当设计cube的rowkey顺序的时候，请记住，将低基数的维度列放在尾部。这不仅对cube的构建过程有好处，而且对cube查询也有好处，因为后聚合（应该是指在HBase查找对应cuboid的过程）也遵循这个规则。

 

### 维度分片

在构建rowkey过程中，有一个选项，可以声明哪个维度用于shard。
这个shard的作用是，将该shard维度和总shard数hash，得到的hash结果插入到encoding后的rowkey中，这样就可以让该维度下相同的数据尽可能的分配到一个shard中，而在hbase存储里，一个shard对应的是一个region，这样处理另一个好处是，在聚合的时候可以很好的把相同数据合并一起，减少网络传输io。参考类`RowKeyEncoder`。一个encoding的rowkey的结构是这样的

```
head+shard+dim1+dim2+…+dimn
```

一个segment的总shard数计算方式如下，参考类`CreateHTableJob`，其中，estimatedSize参数类`CubeStatsReader.estimateCuboidStorageSize`

```
int shardNum = (int) (estimatedSize * magic / mbPerRegion + 1);
```

因此，声明的shard维度最好是被频繁group by的维度或者是基数很大的维度，这样在coprocess处理的时候可以加速



## 构建cube

### 构建引擎

可以选择spark或者mapreduce来构建cube，通常来说，构建引擎的选择方式是这样的

1. 内存消耗型的cube选择mapreduce，例如Count Distinct, Top-N
2. 简单的cube选择spark，例如SUM/MIN/MAX/COUNT

 

**spark引擎**

spark构建引擎采用` by-layer`算法，也就是分层计算

比如有3个维度ABC，cube会构建A,B,C,AB,AC,ABC6种组合，这里就有3层，

第1层：A,B,C

第2层：AB,AC

第3层：ABC

每一层在计算对于spark而言都是一个action，并且该层计算的rdd会依赖其上一层的结果继续计算，这样避免了很大重复性计算工作。

 

代码` SparkCubingByLayer`

### 设计模式

参考[《kylin介绍》](https://www.cnblogs.com/ulysses-you/p/9286987.html)中的cube设计模式



## 数据转换为HFile

kylin将生成的cube通过生成HFile的方式导入到hbase，这个优化点可以配置hbase的相关参数。

1. region数量默认是1，如果数据量大的话可以提高region数量
2. region大小默认是5GB，也就是hbae官方建议的大小；如果cube大小比这个值小太多，可以减小单region的大小
3. hfile文件大小，默认是1GB，由于是通过mapreduce写入的，小文件意味着写入快，但是读取慢，大文件意味着写入慢，读取快

 

代码`CubeHFileJob`

## cleanup

1. 清理hive中的中间表，
2. 清理hbase表
3. 清理hdfs数据

 

**清理命令**

**# 查看需要清理的数据**

./bin/kylin.sh org.apache.kylin.tool.StorageCleanupJob --delete false

**# 清理**

./bin/kylin.sh org.apache.kylin.tool.StorageCleanupJob --delete true

 

// clean参考

http://kylin.apache.org/docs20/howto/howto_cleanup_storage.html

 

[回到顶部](https://www.cnblogs.com/ulysses-you/p/9483634.html#_labelTop)

## 总结

基于kylin的ui，可以看到kylin在构建cube时各个流程的耗时，可以依据这些耗时做相应的优化，常见的，可以从耗时最长的步骤开始优化，比如：

1. 遇到创建hive中间表时间很长，考虑对hive表进行分区处理，对表中的文件格式更改，使用orc，parquet等高性能的文件格式
2. 遇到cube构建时间过长，查看cube设计是否合理，维度的组合关系是否可以再减少，构建引擎是否可以优化

 

优化的思路还是以cube为中心，优化cube的整个生命周期，其中涉及到的所有组件都是优化点，具体情况还是要和实际的数据维度和业务结合起来。

 

