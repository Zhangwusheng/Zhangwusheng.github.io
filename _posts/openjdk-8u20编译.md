yum install libXtst-devel libXt-devel libXrender-devel
yum install -y cups-devel
yum install alsa-lib-devel -y
yum install ccache


下载地址:
http://hg.openjdk.java.net/jdk8u/

dk8u60	[READ-ONLY] JDK 8 Update 60 Master	jdk8u-dev@openjdk.java.net	2015-10-13	 
	corba			2015-10-13	 
	hotspot			2015-10-13	 
	jaxp			2015-10-13	 
	jaxws			2015-10-13	 
	jdk				2015-10-13	 
	langtools		2015-10-13	 
	nashorn			2015-10-13
备注:分别点击jdk8u60以及下面的子链接,在页面左边栏点击gz或者zip下载包.

然后首先解压jdk8u60对应的到一个目录下面,假设为jdk8u60,然后将子目录对应的zip解压到对应的目录下面,即corba-XXXX.zip解压到corba目录下面,hotspot-xxx.zip解压到hotspot目录下面,示意如下:

[root@ecs-f259 jdk8u60-d8f4022fe0cd]# pwd
/root/jdk-src/openjdk-8u20/jdk8u60-d8f4022fe0cd
[root@ecs-f259 jdk8u60-d8f4022fe0cd]# ls -al
total 124252
drwxr-xr-x 14 root root     4096 Feb 18 14:11 .
drwxr-xr-x  3 root root     4096 Feb 18 13:02 ..
-rwxr-xr-x  1 root root     8536 Feb 18 13:04 a.out
-rw-r--r--  1 root root     1503 Oct 13  2015 ASSEMBLY_EXCEPTION
drwxr-xr-x  3 root root     4096 Feb 18 13:04 build
drwxr-xr-x  6 root root     4096 Feb 18 13:01 common
-rw-r--r--  1 root root     1235 Oct 13  2015 configure
lrwxrwxrwx  1 root root       18 Feb 18 13:03 corba -> corba-594da4d5c1a2
drwxr-xr-x  5 root root     4096 Feb 18 13:02 corba-594da4d5c1a2
-rw-r--r--  1 root root  2779330 Feb 18 11:22 corba-594da4d5c1a2.zip
-rw-r--r--  1 root root     3095 Oct 13  2015 get_source.sh
-rw-r--r--  1 root root      154 Oct 13  2015 .hg_archival.txt
-rw-r--r--  1 root root       70 Oct 13  2015 .hgignore
-rw-r--r--  1 root root    23202 Oct 13  2015 .hgtags
lrwxrwxrwx  1 root root       20 Feb 18 13:03 hotspot -> hotspot-37240c1019fd
drwxr-xr-x  7 root root     4096 Feb 18 13:02 hotspot-37240c1019fd
-rw-r--r--  1 root root 14654846 Feb 18 11:13 hotspot-37240c1019fd.zip
lrwxrwxrwx  1 root root       17 Feb 18 13:04 jaxp -> jaxp-4dcdddcc8659
drwxr-xr-x  6 root root     4096 Feb 18 13:02 jaxp-4dcdddcc8659
-rw-r--r--  1 root root  6351541 Feb 18 11:30 jaxp-4dcdddcc8659.zip
lrwxrwxrwx  1 root root       18 Feb 18 13:04 jaxws -> jaxws-51bafda870a9
drwxr-xr-x  6 root root     4096 Feb 18 13:02 jaxws-51bafda870a9
-rw-r--r--  1 root root  7988721 Feb 18 11:36 jaxws-51bafda870a9.zip
drwxr-xr-x  2 root root     4096 Feb 18 13:01 .jcheck
lrwxrwxrwx  1 root root       16 Feb 18 14:09 jdk -> jdk-935758609767
drwxr-xr-x  6 root root     4096 Feb 18 13:03 jdk-935758609767
-rw-r--r--  1 root root 80880817 Feb 18 12:35 jdk-935758609767.zip
lrwxrwxrwx  1 root root       22 Feb 18 13:03 langtools -> langtools-b9abf5c3d057
drwxr-xr-x  6 root root     4096 Feb 18 13:02 langtools-b9abf5c3d057
-rw-r--r--  1 root root  8522103 Feb 18 11:07 langtools-b9abf5c3d057.zip
-rw-r--r--  1 root root    19263 Oct 13  2015 LICENSE
drwxr-xr-x  6 root root     4096 Feb 18 13:01 make
-rw-r--r--  1 root root     6232 Oct 13  2015 Makefile
lrwxrwxrwx  1 root root       20 Feb 18 14:11 nashorn -> nashorn-5a6f6f81ffdf
drwxr-xr-x 12 root root     4096 Feb 18 14:11 nashorn-5a6f6f81ffdf
-rw-r--r--  1 root root  5413690 Feb 18 11:36 nashorn-5a6f6f81ffdf.zip
-rw-r--r--  1 root root     1549 Oct 13  2015 README
-rw-r--r--  1 root root   129333 Oct 13  2015 README-builds.html
drwxr-xr-x  3 root root     4096 Feb 18 13:01 test
-rw-r--r--  1 root root   177094 Oct 13  2015 THIRD_PARTY_README

cd  jdk8u60
bash configure
make images


验证:
cd /root/jdk-src/openjdk-8u20/jdk8u60-d8f4022fe0cd/build/linux-x86_64-normal-server-release/jdk/bin
./java -version









https://hllvm-group.iteye.com/group/topic/26998#193368%20RednaxelaFX

```
├─agent                            Serviceability Agent的客户端实现
├─make                             用来build出HotSpot的各种配置文件
├─src                              HotSpot VM的源代码
│  ├─cpu                            CPU相关代码（汇编器、模板解释器、ad文件、部分runtime函数在这里实现）
│  ├─os                             操作系相关代码
│  ├─os_cpu                         操作系统+CPU的组合相关的代码
│  └─share                          平台无关的共通代码
│      ├─tools                        工具
│      │  ├─hsdis                      反汇编插件
│      │  ├─IdealGraphVisualizer       将server编译器的中间代码可视化的工具
│      │  ├─launcher                   启动程序“java”
│      │  ├─LogCompilation             将-XX:+LogCompilation输出的日志（hotspot.log）整理成更容易阅读的格式的工具
│      │  └─ProjectCreator             生成Visual Studio的project文件的工具
│      └─vm                           HotSpot VM的核心代码
│          ├─adlc                       平台描述文件（上面的cpu或os_cpu里的*.ad文件）的编译器
│          ├─asm                        汇编器接口
│          ├─c1                         client编译器（又称“C1”）
│          ├─ci                         动态编译器的公共服务/从动态编译器到VM的接口
│          ├─classfile                  类文件的处理（包括类加载和系统符号表等）
│          ├─code                       动态生成的代码的管理
│          ├─compiler                   从VM调用动态编译器的接口
│          ├─gc_implementation          GC的实现
│          │  ├─concurrentMarkSweep      Concurrent Mark Sweep GC的实现
│          │  ├─g1                       Garbage-First GC的实现（不使用老的分代式GC框架）
│          │  ├─parallelScavenge         ParallelScavenge GC的实现（server VM默认，不使用老的分代式GC框架）
│          │  ├─parNew                   ParNew GC的实现
│          │  └─shared                   GC的共通实现
│          ├─gc_interface               GC的接口
│          ├─interpreter                解释器，包括“模板解释器”（官方版在用）和“C++解释器”（官方版不在用）
│          ├─libadt                     一些抽象数据结构
│          ├─memory                     内存管理相关（老的分代式GC框架也在这里）
│          ├─oops                       HotSpot VM的对象系统的实现
│          ├─opto                       server编译器（又称“C2”或“Opto”）
│          ├─prims                      HotSpot VM的对外接口，包括部分标准库的native部分和JVMTI实现
│          ├─runtime                    运行时支持库（包括线程管理、编译器调度、锁、反射等）
│          ├─services                   主要是用来支持JMX之类的管理功能的接口
│          ├─shark                      基于LLVM的JIT编译器（官方版里没有使用）
│          └─utilities                  一些基本的工具类
└─test                             单元测试
```