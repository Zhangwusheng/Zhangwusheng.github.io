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



widnows下面编译;
首先下载字体,编译成动态库
https://download.savannah.gnu.org/releases/freetype/freetype-2.8.1.tar.bz2

bash ./configure with_toolsdir="/cygdrive/c/Program Files (x86)/Microsoft Visual Studio/2017/Enterprise/VC/Auxiliary/Build" --with-freetype=/cygdrive/C/Users/zhangwusheng/Downloads/soft/openjdk-8u60/freetype-2.8.1/objs/vc2010/Win32
下载编译好的freetype64位
https://github.com/ubawurinna/freetype-windows-binaries/tree/master/win64


Microsoft (R) C/C++ Optimized Compiler for x64 Version 19.16.27027.1


代码树以及简单介绍

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


编译命令:
bash ./configure with_toolsdir="/cygdrive/c/Program Files (x86)/Microsoft Visual Studio/2017/Enterprise/VC/Auxiliary/Build" --with-freetype=/cygdrive/c/Work/Source/openjdk-8u60/freetype-win64 --without-x

"C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\Common7\IDE\devenv.exe"

下载编译好的freetype64位
https://github.com/ubawurinna/freetype-windows-binaries/tree/master/win64

主要修改:1.设置VS的环境变量2设置VS编译器的参数
其中的版本号是自己运行CL得来的,CL输出的是中文,会影响程序运行
21968行:
	COMPILER_VENDOR="Microsoft CL.EXE"
	COMPILER_VERSION_TEST="Microsoft (R) C/C++ Optimized Compiler for x64 Version 19.16.27027.1"
	COMPILER_VERSION="19.16.27027.1"
    COMPILER_CPU_TEST="x64"
20359:
    COMPILER_VENDOR="Microsoft CL.EXE"
	COMPILER_VERSION_TEST="Microsoft (R) C/C++ Optimized Compiler for x64 Version 19.16.27027.1"
	COMPILER_VERSION="19.16.27027.1"
    COMPILER_CPU_TEST="x64"	
16927:
  if test "x$OPENJDK_TARGET_CPU_BITS" = x32; then 
	VCVARSFILE="VC/Auxiliary/Build/vcvars32.bat" 
  else 
	VCVARSFILE="VC/Auxiliary/Build/vcvars64.bat" # 这里改为VS2017的路径 
  fi
16949:多了一个..
  if test "x$VS_ENV_CMD" = x; then
    VS100BASE="$with_toolsdir/../../.."
  
  C:\Users\zhangwusheng\Downloads\soft\openjdk-8u60\hotspot/make/windows/get_msc_ver.sh
    MSC_VER_MAJOR=19
  MSC_VER_MINOR=16
  MSC_VER_MICRO=27027
  
  
生成工程:
set HOTSPOTMKSHOME=C:\cygwin64\bin
确保grep可以运行
create "C:\Users\zhangwusheng\Downloads\soft\openjdk-8u60\build\windows-x86_64-normal-server-release\images\j2sdk-image"



C:\Users\zhangwusheng\Downloads\soft\openjdk-8u60\hotspot\src\share\vm\utilities\globalDefinitions_visCPP.hpp
注释掉vsnprintf

几个关于格式化字符串的宏,在前后加上空格

https://blog.csdn.net/ttcttcttc/article/details/79301637






mkdir ZWS-BUILDS
cd ZWS-BUILDS
tar zxvf ../jdk8u60-d8f4022fe0cd.tar.gz -C .
mv jdk8u60-d8f4022fe0cd/* .
rm -rf jdk8u60-d8f4022fe0cd/
cp ../jdk-935758609767.zip .
unzip ./jdk-935758609767.zip
 mv jdk-935758609767 jdk
rm -f ./jdk-935758609767.zip

cp ../corba-594da4d5c1a2.zip .
mv ./corba-594da4d5c1a2 ./corba
rm -f ./corba-594da4d5c1a2.zip


cp ../hotspot-37240c1019fd.zip .
unzip ./hotspot-37240c1019fd.zip
mv ./hotspot-37240c1019fd ./hotspot
rm -f ./hotspot-37240c1019fd.zip

cp ../jaxp-4dcdddcc8659.zip .
unzip ./jaxp-4dcdddcc8659.zip
mv jaxp-4dcdddcc8659 jaxp
rm -f jaxp-4dcdddcc8659.zip


cp ../jaxws-51bafda870a9.zip  .
unzip ./jaxws-51bafda870a9.zip
mv jaxws-51bafda870a9 jaxws
rm -f jaxws-51bafda870a9.zip

cp ../langtools-b9abf5c3d057.zip  .
unzip ./langtools-b9abf5c3d057.zip
mv langtools-b9abf5c3d057  langtools
rm -f langtools-b9abf5c3d057.zip

cp ../nashorn-5a6f6f81ffdf.zip .
unzip ./nashorn-5a6f6f81ffdf.zip
mv ./nashorn-5a6f6f81ffdf nashorn
rm -rf ./nashorn-5a6f6f81ffdf.zip


参考 https://blog.csdn.net/ciqingloveless/article/details/81950308

vi C:\Work\Source\openjdk-8u60\ZWS-BUILDS\common\autoconf\generated-configure.sh
查找 VCVARSFILE
替换为:
  if test "x$OPENJDK_TARGET_CPU_BITS" = x32; then
    VCVARSFILE="Auxiliary/Build/vcvars32xp.bat"  
  else
    VCVARSFILE="Auxiliary/Build/vcvars64.bat"    
  fi

注释一下代码:
共有两处,需要注释:
关键字:Target CPU mismatch

if test "x$OPENJDK_TARGET_CPU" = "xx86"; then
      if test "x$COMPILER_CPU_TEST" != "x80x86"; then
        as_fn_error $? "Target CPU mismatch. We are building for $OPENJDK_TARGET_CPU but CL is for \"$COMPILER_CPU_TEST\"; expected \"80x86\"." "$LINENO" 5
      fi
    elif test "x$OPENJDK_TARGET_CPU" = "xx86_64"; then
      if test "x$COMPILER_CPU_TEST" != "xx64"; then
        as_fn_error $? "Target CPU mismatch. We are building for $OPENJDK_TARGET_CPU but CL is for \"$COMPILER_CPU_TEST\"; expected \"x64\"." "$LINENO" 5
      fi
    fi

 bash ./configure with_toolsdir="/cygdrive/c/Program Files (x86)/Microsoft Visual Studio/2017/Enterprise/VC/Auxiliary/Build" --with-freetype=/cygdrive/c/Work/Source/openjdk-8u60/freetype-win64 --without-x -with-target-bits=64
 
 
 bash ./configure with_toolsdir="/cygdrive/c/Program Files (x86)/Microsoft Visual Studio/2017/Enterprise/VC/Auxiliary/Build" --with-freetype=/cygdrive/c/Users/zhangwusheng/Downloads/jdk8u/freetype-win64 --without-x -with-target-bits=64 --with-toolchain-version=2017

  bash ./configure with_toolsdir="/cygdrive/c/Program Files (x86)/Microsoft Visual Studio 14.0/VC" --with-freetype=/cygdrive/c/Users/zhangwusheng/Downloads/jdk8u/freetype-win64 --without-x -with-target-bits=64 --with-toolchain-version=2015


 C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC
 make images
 
 vi ./hotspot/make/windows/get_msc_ver.sh
 
 第70行,或者搜索关键字:MSC_VER=1399
#MSC_VER=`"$EXPR" $MSC_VER_MAJOR \* 100 + $MSC_VER_MINOR`
	MSC_VER=1700
	
	
	错误:error C2956: sized deallocation function 'operator delete(void*, size_t)' would be chosen as placement deallocation function.
	
	vi  ZWS-BUILDS\hotspot\make\windows\makefiles\adlc.make
	 ADLC_CXX_FLAGS增加:  /Zc:sizedDealloc-
	 
	 错误:C:\Work\Source\openjdk-8u60\ZWS-BUILDS\hotspot\src\share\vm\utilities/globalDefinitions_visCPP.hpp(190): error C2084: 函数“int vsnprintf(char *const ,const size_t,const char *const ,va_list)”已有主体
C:\Program Files (x86)\Windows Kits\10\include\10.0.17763.0\ucrt\stdio.h(1430): note: 参见“vsnprintf”的前一个定义

	 vi C:\Work\Source\openjdk-8u60\ZWS-BUILDS\hotspot\src\share\vm\utilities\globalDefinitions_visCPP.hpp
	 190line 注释:vsnprintf
	 
	 
	  error C2220: 警告被视为错误 - 没有生成“object”文件
	  vi C:\Work\Source\openjdk-8u60\ZWS-BUILDS\hotspot\make\windows\makefiles\compile.make
	  去掉 /WX
	  #CXX_FLAGS=$(EXTRA_CFLAGS) /nologo /W3 /WX
CXX_FLAGS=$(EXTRA_CFLAGS) /nologo /W3


错误:.inline.hpp(98): error C3680: 
参见 https://bugs.openjdk.java.net/browse/JDK-8204872,在8u201 已经修正
C:\Work\Source\openjdk-8u60\ZWS-BUILDS\hotspot\src\share\vm\memory/threadLocalAllocBuffer.inline.hpp
增加空格
vi C:\Work\Source\openjdk-8u60\ZWS-BUILDS\hotspot\src\share\vm\trace/traceStream.hpp
增加空格
vi C:\Work\Source\openjdk-8u60\ZWS-BUILDS\hotspot\src\share\vm\classfile/dictionary.hpp
373 行增肌空格
vi C:\Work\Source\openjdk-8u60\ZWS-BUILDS\hotspot\src\share\vm\code\nmethod.cpp
增加空格

vi C:\Work\Source\openjdk-8u60\ZWS-BUILDS\hotspot\src\share\vm\code\exceptionHandlerTable.cpp
zengjie space