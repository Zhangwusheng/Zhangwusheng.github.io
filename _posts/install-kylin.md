1.下载安装包
wget -c 'http://mirrors.shu.edu.cn/apache/kylin/apache-kylin-2.6.1/apache-kylin-2.6.1-bin-hadoop3.tar.gz'
2.下载spark安装包
wget -c 'http://mirrors.shu.edu.cn/apache/spark/spark-2.4.0/spark-2.4.0-bin-hadoop2.7.tgz'

下载后,解压到指定目录,目前是/data2,

我们hadoop安装的是HDP的3.0版本,使用ambari 2.7.0安装,各个组件的版本信息如下:

网络环境:纯内网

java版本:

java version "1.8.0_181"
Java(TM) SE Runtime Environment (build 1.8.0_181-b13)
Java HotSpot(TM) 64-Bit Server VM (build 25.181-b13, mixed mode)



| HDFS       | 3.1.0 | **Installed** | Apache Hadoop Distributed File System                        |
| ---------- | ----- | ------------- | ------------------------------------------------------------ |
| YARN       | 3.1.0 | **Installed** | Apache Hadoop NextGen MapReduce (YARN)                       |
| MapReduce2 | 3.1.0 | **Installed** | Apache Hadoop NextGen MapReduce (YARN)                       |
| Tez        | 0.9.1 | **Installed** | Tez is the next generation Hadoop Query Processing framework written on top of YARN. |
| Hive       | 3.1.0 | **Installed** | Data warehouse system for ad-hoc queries & analysis of large datasets and table & storage management service |
| HBase      | 2.0.0 | **Installed** | Non-relational distributed database and centralized service for configuration management & synchronization |
| Spark2     | 2.3.1 | **Installed** | Apache Spark 2.3 is a fast and general engine for large-scale data processing. |





```bash
#if [ "${client_mode}" == "beeline" ]
#then
#    beeline_shell=`$KYLIN_HOME/bin/get-properties.sh kylin.source.hive.beeline-shell`
#    beeline_params=`bash ${KYLIN_HOME}/bin/get-properties.sh kylin.source.hive.beeline-params`
#    hive_env=`${beeline_shell} ${hive_conf_properties} ${beeline_params} --outputformat=dsv -e "set;" 2>&1 | grep --text 'env:CLASSPATH' `
#else
#    source ${dir}/check-hive-usability.sh
#    hive_env=`hive -n hive -p hive ${hive_conf_properties} -e set 2>&1 | grep 'env:CLASSPATH'`
#fi


hive_env=`beeline ${hive_conf_properties} ${beeline_params} --outputformat=dsv -e "set;" 2>&1 | grep --text 'env:CLASSPATH' `

echo "==================================================="
echo "hive_env=${hive_env}"
echo "==================================================="

```











安装完组件后设置了如下环境变量:

export JAVA_HOME=/usr/local/jdk
export KYLIN_HOME=/data2/apache-kylin-2.6.1-bin-hadoop3
export HADOOP_HOME=/usr/hdp/3.0.0.0-1634/hadoop
export SPARK_HOME=/usr/hdp/3.0.0.0-1634/spark2



然后cd /data2/apache-kylin-2.6.1-bin-hadoop3/

运行:

$KYLIN_HOME/bin/check-env.sh

Retrieving hadoop conf dir...
KYLIN_HOME is set to /data2/apache-kylin-2.6.1-bin-hadoop3

echo $?结果为0,显示运行正常

然后运行

 $KYLIN_HOME/bin/kylin.sh start



Retrieving hadoop conf dir...
KYLIN_HOME is set to /data2/apache-kylin-2.6.1-bin-hadoop3
Retrieving hive dependency... ################这里特别慢



A new Kylin instance is started by root. To stop it, run 'kylin.sh stop'
Check the log at /data2/apache-kylin-2.6.1-bin-hadoop3/logs/kylin.log

启动成功之后,

netstat -anp|grep 8180 (我修改了server.xml的端口)

可以看到有监听,然后查看 Kylin.log



**2019-04-08 09:24:35,966 WARN  [localhost-startStop-1] [localhost].[/kylin]:164 : Exception sending context initialized event to listener instance of class [org.springframework.web.context.ContextLoaderListener]
org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping': Invocation of init method failed; nested exception is java.lang.NoClassDefFoundError: org/apache/commons/configuration/ConfigurationException
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.initializeBean(AbstractAutowireCapableBeanFactory.java:1628)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:555)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:483)
        at org.springframework.beans.factory.support.AbstractBeanFactory$1.getObject(AbstractBeanFactory.java:306)
        at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:230)
        at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:302)
        at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:197)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.preInstantiateSingletons(DefaultListableBeanFactory.java:761)
        at org.springframework.context.support.AbstractApplicationContext.finishBeanFactoryInitialization(AbstractApplicationContext.java:867)
        at org.springframework.context.support.AbstractApplicationContext.refresh(AbstractApplicationContext.java:543)
        at org.springframework.web.context.ContextLoader.configureAndRefreshWebApplicationContext(ContextLoader.java:443)
        at org.springframework.web.context.ContextLoader.initWebApplicationContext(ContextLoader.java:325)
        at org.springframework.web.context.ContextLoaderListener.contextInitialized(ContextLoaderListener.java:107)
        at org.apache.catalina.core.StandardContext.listenerStart(StandardContext.java:4792)
        at org.apache.catalina.core.StandardContext.startInternal(StandardContext.java:5256)
        at org.apache.catalina.util.LifecycleBase.start(LifecycleBase.java:150)
        at org.apache.catalina.core.ContainerBase.addChildInternal(ContainerBase.java:754)
        at org.apache.catalina.core.ContainerBase.addChild(ContainerBase.java:730)
        at org.apache.catalina.core.StandardHost.addChild(StandardHost.java:734)
        at org.apache.catalina.startup.HostConfig.deployWAR(HostConfig.java:985)
        at org.apache.catalina.startup.HostConfig$DeployWar.run(HostConfig.java:1857)
        at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
        at java.util.concurrent.FutureTask.run(FutureTask.java:266)
        at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
        at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
        at java.lang.Thread.run(Thread.java:748)
Caused by: java.lang.NoClassDefFoundError: org/apache/commons/configuration/ConfigurationException
        at java.lang.Class.getDeclaredMethods0(Native Method)
        at java.lang.Class.privateGetDeclaredMethods(Class.java:2701)
        at java.lang.Class.getDeclaredMethods(Class.java:1975)
        at org.springframework.util.ReflectionUtils.getDeclaredMethods(ReflectionUtils.java:613)
        at org.springframework.util.ReflectionUtils.doWithMethods(ReflectionUtils.java:524)
        at org.springframework.core.MethodIntrospector.selectMethods(MethodIntrospector.java:68)
        at org.springframework.web.servlet.handler.AbstractHandlerMethodMapping.detectHandlerMethods(AbstractHandlerMethodMapping.java:230)
        at org.springframework.web.servlet.handler.AbstractHandlerMethodMapping.initHandlerMethods(AbstractHandlerMethodMapping.java:214)
        at org.springframework.web.servlet.handler.AbstractHandlerMethodMapping.afterPropertiesSet(AbstractHandlerMethodMapping.java:184)
        at org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping.afterPropertiesSet(RequestMappingHandlerMapping.java:127)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.invokeInitMethods(AbstractAutowireCapableBeanFactory.java:1687)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.initializeBean(AbstractAutowireCapableBeanFactory.java:1624)
        ... 25 more
Caused by: java.lang.ClassNotFoundException: org.apache.commons.configuration.ConfigurationException
        at org.apache.catalina.loader.WebappClassLoaderBase.loadClass(WebappClassLoaderBase.java:1309)
        at org.apache.catalina.loader.WebappClassLoaderBase.loadClass(WebappClassLoaderBase.java:1137)
        ... 37 more
2019-04-08 09:24:35,967 WARN  [localhost-startStop-1] core.StandardContext:155 : One or more listeners failed to start. Full details will be found in the appropriate container log file
2019-04-08 09:24:35,973 WARN  [localhost-startStop-1] core.StandardContext:155 : Context [/kylin] startup failed due to previous errors
2019-04-08 09:24:35,975 INFO  [localhost-startStop-1] [localhost].[/kylin]:119 : Closing Spring root WebApplicationContext
2019-04-08 09:24:35,982 INFO  [localhost-startStop-1] [localhost].[/kylin]:119 : Shutting down log4j**




