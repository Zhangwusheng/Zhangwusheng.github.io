---
layout:     post
title:     Hbase HFile
subtitle:   Apache HBase I/O – HFile
date:       2018-09-21
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - hbase
    - memstore

typora-copy-images-to: ..\img
typora-root-url: ..
---

[原文在此](https://blog.csdn.net/zhangxiongcolin/article/details/82011080) 以及 [这一篇](https://blog.csdn.net/zhangxiongcolin/article/details/82011100)

https://cwiki.apache.org/confluence/display/AMBARI/Defining+a+Custom+Stack+and+Services



# Ambari组件文件配置  

我们以Spark2为例来看看Ambari是如何编排目录文件的  

![ambari-redis-20180824082117823](/img/ambari-redis-20180824082117823.png)



configuration目录下存放的是spark2的属性配置文件，对应Ambari页面的属性配置页面，可以设置默认值，类型，描述等信息  

package/scripts目录下存放服务操作相关的脚本，如服务的启动，服务停止，服务检查等  

package/templates该目录可选，存放的是组件属性的配置信息，和configuration目录下的配置对应，这个关系是若果我们在Ambari页面修改了属性信息，则修改信息会自动填充该目录下文件的属性，所以，这个目录下的属性是最新的，并且是服务要调用的  

package/alerts目录存放告警配置，如程序断掉或者其他原因未运行时会出现告警或者可以定义其他告警  

quicklinks该目录下存放的是快速链接配置，Ambari页面通过该配置可以跳转到我们想要跳转的页面，如HDFS，快速链接页面指向的地址是 http://node:50070  

metrics.json用来配置指标显示  

kerberos.json用来配置kerberos认证 

 metainfo.json这个文件很重要，主要是配置服务名，服务类型，服务操作脚本，metrics以及快速链接等 

# RPM包制作  

Ambari中，组件都是以RPM包的方式安装的，因此我们自定义的组件也需要打包RPM，下面我们介绍一下如何制作RPM包  

1. 安装rpm-build  yum install rpm-build  

2. 编写SPEC文件  

   SPEC文件关键字  

   SPEC文件是RPM文件的组织说明，主要配置项如下所述  Name:软件包的名称，后面可以使用%{name}的方式引用  Summary：软件包的内容概要  Version：软件的实际版本号，如，1.1.0，后面可使用%{version}来引用  Release：发布序列号，如，BDP等，标明第几次打包，后面可以使用%{Release}引用  Group: 软件分组，建议使用标准分组  License: 软件授权方式，通常就是GPL  Source: 源代码包，可以带多个用Source1、Source2等源，后面也可以用%{source1}、%{source2}引用  BuildRoot: 这个是安装或编译时使用的“虚拟目录”，考虑到多用户的环境，一般定义为：%{tmppath}/{name}-%{version}-%{release}-root或%{tmppath}/%{name}-%{version}-%{release}-buildroot-%%__id_u} -n}.该参数非常重要，因为在生成rpm的过程中，执行make install时就会把软件安装到上述的路径中，在打包的时候，同样依赖“虚拟目录”为“根目录”进行操作。后面可使用$RPM_BUILD_ROOT 方式引用。  URL: 软件的主页  Vendor: 发行商或打包组织的信息，例如RedFlag Co,Ltd  Disstribution: 发行版标识  Patch: 补丁源码，可使用Patch1、Patch2等标识多个补丁，使用%patch0或%{patch0}引用  Prefix: %{_prefix} 这个主要是为了解决今后安装rpm包时，并不一定把软件安装到rpm中打包的目录的情况。这样，必须在这里定义该标识，并在编写%install脚本的时候引用，才能实现rpm安装时重新指定位置的功能  Prefix: %{sysconfdir} 这个原因和上面的一样，但由于%{prefix}指/usr，而对于其他的文件，例如/etc下的配置文件，则需要用%{_sysconfdir}标识  Build Arch: 指编译的目标处理器架构，noarch标识不指定，但通常都是以/usr/lib/rpm/marcros中的内容为默认值  Requires: 该rpm包所依赖的软件包名称，可以用>=或<=表示大于或小于某一特定版本，例如：libpng-devel >= 1.0.20 zlib ※“>=”号两边需用空格隔开，而不同软件名称也用空格分开,还有例如PreReq、Requires(pre)、Requires(post)、Requires(preun)、Requires(postun)、BuildRequires等都是针对不同阶段的依赖指定  Provides: 指明本软件一些特定的功能，以便其他rpm识别  Packager: 打包者的信息  description 软件的详细说明 SPEC脚本主体  %setup -n %{name}-%{version}** 把源码包解压并放好通常是从/usr/src/asianux/SOURCES里的包解压到/usr/src/asianux/BUILD/%{name}-%{version}中。一般用%setup -c就可以了，但有两种情况：一就是同时编译多个源码包，二就是源码的tar包的名称与解压出来的目录不一致，此时，就需要使用-n参数指定一下了。  %patch 打补丁通常补丁都会一起在源码tar.gz包中，或放到SOURCES目录下。一般参数为：  %patch -p1 使用前面定义的Patch补丁进行，-p1是忽略patch的第一层目  %Patch2 -p1 -b xxx.patch 打上指定的补丁，-b是指生成备份文件  %setup -n %{name}-%{version}** 把源码包解压并放好通常是从/usr/src/asianux/SOURCES里的包解压到/usr/src/asianux/BUILD/%{name}-%{version}中。一般用%setup -c就可以了，但有两种情况：一就是同时编译多个源码包，二就是源码的tar包的名称与解压出来的目录不一致，此时，就需要使用-n参数指定一下了。  %patch 打补丁通常补丁都会一起在源码tar.gz包中，或放到SOURCES目录下。一般参数为：  %patch -p1 使用前面定义的Patch补丁进行，-p1是忽略patch的第一层目  %Patch2 -p1 -b xxx.patch 打上指定的补丁，-b是指生成备份文件 Redis组件添加  1.在ambari-server/resource/statck/HDP/2.6目录下创建REDIS目录，注意大写  2.在REDIS目录下创建 metainfo.xml文件，文件内容及说明如下  2.0 REDIS(服务名称，必须大写) Redis(显示名称) Redis(描述) 4.0.10(版本) REDIS_SERVER(服务名称) Redis-Server(显示名称) MASTER(角色) 1+(节点数) true REDIS 300 redis.conf(配置文件) true 3.在REDIS目录下创建 package/scripts，package/templates目录  4.将redis文件包中的redis.conf拷贝到templates目录下并命名为redis.conf.j2  5.在redis.conf.j2中配置要修改的属性，如，bind:{{bind}}  6.在scripts目录下创建params.py，params_linux.py,redis.py,redis_server.py,redis_service.py,service_check.py,status_params.py以及upgrade.py  params.py:判断操作系统，引用不同的变量定义文件，如Linux系统引用params_linux.py文件  params_linus.py:定义变量，引用系统变量，定义在5中配置的属性变量，如：port = config[‘configurations’][‘redis.conf’][‘port’]  redis.py:创建目录及文件夹  redis_server.py:定义服务启动，停止，重启操作  redis_service.py:redis_server.py中服务启动，停止重启操作的具体实现，如下图所示标识启动redis服务  其中，redis_script = format(“{redis_bin}/redis-server”)，redis_cmd = format(“{redis_script} {config_dir}/redis.conf”)  service_check.py:服务状态检查  status_params.py：服务版本状态  upgrade.py：服务升级  7.在REDIS目录下创建configuration目录，在configuration目录下创建redis.conf.xml,其内容为我们在5中定义的属性  8.在REDIS目录下创建alert.json文件，存放告警配置，当redis宕掉后会触发  通过以上步骤，Redis在Ambari中的配置就已完成，重新编译Ambari源码 Redis RPM包制作  1.到官网下载redis源码包，最新版本为4.0.10，解压并且编译  make PREFIX=/opt/redis install  2.在/opt/redis/bin目录可以看到编译后的文件  3.创建 redis_2_6_2_0_205-4.0.10.2.6.2.0/usr/hdp/2.6.2.0-205/redis/目录  mkdir -p /opt/redis_2_6_2_0_205-4.0.10.2.6.2.0/usr/hdp/2.6.2.0-205/redis/  4.在3中的目录下创建bin，etc/redis及conf软链,r软链指向/etc/redis/conf  mkdir bin,mkdir etc/redis  创建软链是需要注意，由于系统中/etc/redis/conf目录是不存在的，所以先要创建，然后执行 ln /etc/redis/conf conf  创建完成后，可以将/etc/redis/conf删除  5.将2中bin目录下的文件拷贝到 /opt/redis_2_6_2_0_205-4.0.10.2.6.2.0/usr/hdp/2.6.2.0-205/redis/bin目录下，将redis.conf拷贝到/opt/redis_2_6_2_0_205-4.0.10.2.6.2.0/usr/hdp/2.6.2.0-205/redis/etc/redis 目录下  6.将redis_2_6_2_0_205-4.0.10.2.6.2.0压缩成tar.gz  tar zcvf ./redis_2_6_2_0_205-4.0.10.2.6.2.0.tar.gz ./redis_2_6_2_0_205-4.0.10.2.6.2.0  7.创建redis spec文件–redis_2_6_2_0_205-4.0.10.2.6.2.0-205.noarch.rpm.spec  8.创建打包所需要的路径  mkdir -p ~/rpmbuild/{RPMS,SRPMS,BUILD,SOURCES,SPECS,tmp}  9.将spec文件拷贝到创建的SPECS目录下  10.将tar.gz包放到SOURCES目录下  11.执行打包  rpmbuild -bb –target noarch SPECS/redis_2_6_2_0_205-4.0.10.2.6.2.0-205.noarch.rpm.spec  12.安装并验证  验证安装完后，记得要卸载，rpm -e redis_2_6_2_0_205，不然后续安装会出现问题 以上就是Ambari中添加自定义组件的部分内容，下一篇将介绍自定义组件如何集成到Ambari框架及组件metrics开发 --------------------- 本文来自 zhangiongcolin 的CSDN 博客 ，全文地址请点击：https://blog.csdn.net/zhangxiongcolin/article/details/82011080?utm_source=copy  