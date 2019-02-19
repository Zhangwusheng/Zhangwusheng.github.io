https://blog.csdn.net/chenpeng19910926/article/details/81903985





# 函数性能对比工具之JMH



# 概述

JMH 是一个由 OpenJDK/Oracle 里面那群开发了 Java 编译器的大牛们所开发的 Micro Benchmark Framework 。何谓 Micro Benchmark 呢？简单地说就是在 **method** 层面上的 benchmark，精度可以精确到微秒级。可以看出 JMH 主要使用在当你已经找出了热点函数，而需要对热点函数进行进一步的优化时，就可以使用 JMH 对优化的效果进行定量的分析。

比较典型的使用场景还有：

- 想定量地知道某个函数需要执行多长时间，以及执行时间和输入 n 的相关性
- 一个函数有两种不同实现（例如实现 A 使用了 FixedThreadPool，实现 B 使用了 ForkJoinPool），不知道哪种实现性能更好

尽管 JMH 是一个相当不错的 Micro Benchmark Framework，但很无奈的是网上能够找到的文档比较少，而官方也没有提供比较详细的文档，对使用造成了一定的障碍。但是有个好消息是官方的 [Code Sample](http://hg.openjdk.java.net/code-tools/jmh/file/tip/jmh-samples/src/main/java/org/openjdk/jmh/samples/) 写得非常[浅显易懂](https://www.baidu.com/s?wd=%E6%B5%85%E6%98%BE%E6%98%93%E6%87%82&tn=24004469_oem_dg&rsv_dl=gh_pl_sl_csd)，推荐在需要详细了解 JMH 的用法时可以通读一遍——本文则会介绍 JMH 最典型的用法和部分常用选项。

 

# 第一个例子

如果你使用 maven 来管理你的 Java 项目的话，引入 JMH 是一件很简单的事情——只需要在 `pom.xml`里增加 JMH 的依赖即可

```
<properties>
    <jmh.version>1.14.1</jmh.version>
</properties>

<dependencies>
    <dependency>
        <groupId>org.openjdk.jmh</groupId>
        <artifactId>jmh-core</artifactId>
        <version>${jmh.version}</version>
    </dependency>



    <dependency>



        <groupId>org.openjdk.jmh</groupId>



        <artifactId>jmh-generator-annprocess</artifactId>



        <version>${jmh.version}</version>



        <scope>provided</scope>



    </dependency>



</dependencies>
@BenchmarkMode(Mode.AverageTime)



@OutputTimeUnit(TimeUnit.MICROSECONDS)



@State(Scope.Thread)



public class FirstBenchmark {



 



    @Benchmark



    public int sleepAWhile() {



        try {



            Thread.sleep(500);



        } catch (InterruptedException e) {



            // ignore



        }



        return 0;



    }



 



    public static void main(String[] args) throws RunnerException {



        Options opt = new OptionsBuilder()



                .include(FirstBenchmark.class.getSimpleName())



                .forks(1)



                .warmupIterations(5)



                .measurementIterations(5)



                .build();



 



        new Runner(opt).run();



    }



}
```

结果：

```
# JMH 1.14.1 (released 39 days ago)



# VM version: JDK 1.8.0_11, VM 25.11-b03



# VM invoker: /Library/Java/JavaVirtualMachines/jdk1.8.0_11.jdk/Contents/Home/jre/bin/java



# VM options: -Didea.launcher.port=7535 -Didea.launcher.bin.path=/Applications/IntelliJ IDEA 15 CE.app/Contents/bin -Dfile.encoding=UTF-8



# Warmup: 5 iterations, 1 s each



# Measurement: 5 iterations, 1 s each



# Timeout: 10 min per iteration



# Threads: 1 thread, will synchronize iterations



# Benchmark mode: Average time, time/op



# Benchmark: com.dyng.FirstBenchmark.sleepAWhile



 



# Run progress: 0.00% complete, ETA 00:00:10



# Fork: 1 of 1



# Warmup Iteration   1: 503.440 ms/op



# Warmup Iteration   2: 503.885 ms/op



# Warmup Iteration   3: 503.714 ms/op



# Warmup Iteration   4: 504.333 ms/op



# Warmup Iteration   5: 502.596 ms/op



Iteration   1: 504.352 ms/op



Iteration   2: 502.583 ms/op



Iteration   3: 501.256 ms/op



Iteration   4: 501.655 ms/op



Iteration   5: 504.212 ms/op



 



Result "sleepAWhile":



  502.811 ±(99.9%) 5.495 ms/op [Average]



  (min, avg, max) = (501.256, 502.811, 504.352), stdev = 1.427



  CI (99.9%): [497.316, 508.306] (assumes normal distribution)



 



# Run complete. Total time: 00:00:12



 



Benchmark                   Mode  Cnt    Score   Error  Units



FirstBenchmark.sleepAWhile  avgt    5  502.811 ± 5.495  ms/op
```

对 `sleepAWhile()` 的测试结果显示执行时间平均约为502毫秒。因为我们的测试对象 `sleepAWhile()` 正好就是睡眠500毫秒，所以 JMH 显示的结果可以说很符合我们的预期。

那好，现在我们再来详细地解释代码的意义。不过在这之前，需要先了解一下 JMH 的几个基本概念。

## 基本概念

### Mode

*Mode* 表示 JMH 进行 Benchmark 时所使用的模式。通常是测量的维度不同，或是测量的方式不同。目前 JMH 共有四种模式：

- `Throughput`: 整体吞吐量，例如“1秒内可以执行多少次调用”。
- `AverageTime`: 调用的平均时间，例如“每次调用平均耗时xxx毫秒”。
- `SampleTime`: 随机取样，最后输出取样结果的分布，例如“99%的调用在xxx毫秒以内，99.99%的调用在xxx毫秒以内”
- `SingleShotTime`: 以上模式都是默认一次 iteration 是 1s，唯有 `SingleShotTime` 是**只运行一次**。往往同时把 warmup 次数设为0，用于测试冷启动时的性能。

### Iteration

*Iteration* 是 JMH 进行测试的最小单位。在大部分模式下，一次 *iteration* 代表的是一秒，JMH 会在这一秒内不断调用需要 benchmark 的方法，然后根据模式对其采样，计算吞吐量，计算平均执行时间等。

### Warmup

*Warmup* 是指在实际进行 benchmark 前先进行预热的行为。为什么需要预热？因为 JVM 的 JIT 机制的存在，如果某个函数被调用多次之后，JVM 会尝试将其编译成为机器码从而提高执行速度。所以为了让 benchmark 的结果更加接近真实情况就需要进行预热。

## 注解

现在来解释一下上面例子中使用到的注解，其实很多注解的意义完全可以[望文生义](https://www.baidu.com/s?wd=%E6%9C%9B%E6%96%87%E7%94%9F%E4%B9%89&tn=24004469_oem_dg&rsv_dl=gh_pl_sl_csd) :)

### @Benchmark

表示该方法是需要进行 benchmark 的对象，用法和 JUnit 的 `@Test` 类似。

### @Mode

`Mode` 如之前所说，表示 JMH 进行 Benchmark 时所使用的模式。

### @State

`State` 用于声明某个类是一个“状态”，然后接受一个 `Scope` 参数用来表示该状态的共享范围。因为很多 benchmark 会需要一些表示状态的类，JMH 允许你把这些类以依赖注入的方式注入到 benchmark 函数里。`Scope` 主要分为两种。

- `Thread`: 该状态为每个线程独享。
- `Benchmark`: 该状态在所有线程间共享。

关于`State`的用法，官方的 code sample 里有比较好的[例子](http://hg.openjdk.java.net/code-tools/jmh/file/cb9aa824b55a/jmh-samples/src/main/java/org/openjdk/jmh/samples/JMHSample_03_States.java)。

### @OutputTimeUnit

benchmark 结果所使用的时间单位。

## 启动选项

解释完了注解，再来看看 JMH 在启动前设置的参数。

```
Options opt = new OptionsBuilder()



        .include(FirstBenchmark.class.getSimpleName())



        .forks(1)



        .warmupIterations(5)



        .measurementIterations(5)



        .build();



 



new Runner(opt).run();
```

### include

benchmark 所在的类的名字，注意这里是**使用正则表达式对所有类进行匹配**的。

### fork

进行 fork 的次数。如果 fork 数是2的话，则 JMH 会 fork 出两个进程来进行测试。

### warmupIterations

预热的迭代次数。

### measurementIterations

实际测量的迭代次数。

# 第二个例子

在看过第一个完全只为示范的例子之后，再来看一个有实际意义的例子。

问题：

> 计算 1 ~ n 之和，比较串行算法和并行算法的效率，看 n 在大约多少时并行算法开始超越串行算法

首先定义一个表示这两种实现的接口

```
public interface Calculator {



    /**



     * calculate sum of an integer array



     * @param numbers



     * @return



     */



    public long sum(int[] numbers);



 



    /**



     * shutdown pool or reclaim any related resources



     */



    public void shutdown();



}
```

由于这两种算法的实现不是这篇文章的重点，而且本身并不困难，所以实际代码就不赘述了。如果真的感兴趣的话，可以看最后的附录。以下仅说明一下我所指的串行算法和并行算法的含义。

- 串行算法：使用 `for-loop` 来计算 n 个正整数之和。
- 并行算法：将所需要计算的 n 个正整数分成 m 份，交给 m 个线程分别计算出和以后，再把它们的结果相加。

进行 benchmark 的代码如下

```
@BenchmarkMode(Mode.AverageTime)



@OutputTimeUnit(TimeUnit.MICROSECONDS)



@State(Scope.Benchmark)



public class SecondBenchmark {



    @Param({"10000", "100000", "1000000"})



    private int length;



 



    private int[] numbers;



    private Calculator singleThreadCalc;



    private Calculator multiThreadCalc;



 



    public static void main(String[] args) throws RunnerException {



        Options opt = new OptionsBuilder()



                .include(SecondBenchmark.class.getSimpleName())



                .forks(2)



                .warmupIterations(5)



                .measurementIterations(5)



                .build();



 



        new Runner(opt).run();



    }



 



    @Benchmark



    public long singleThreadBench() {



        return singleThreadCalc.sum(numbers);



    }



 



    @Benchmark



    public long multiThreadBench() {



        return multiThreadCalc.sum(numbers);



    }



 



    @Setup



    public void prepare() {



        numbers = IntStream.rangeClosed(1, length).toArray();



        singleThreadCalc = new SinglethreadCalculator();



        multiThreadCalc = new MultithreadCalculator(Runtime.getRuntime().availableProcessors());



    }



 



    @TearDown



    public void shutdown() {



        singleThreadCalc.shutdown();



        multiThreadCalc.shutdown();



    }



}
```

注意到这里用到了3个之前没有使用的注解。

### @Param

`@Param` 可以用来指定某项参数的多种情况。特别适合用来测试一个函数在不同的参数输入的情况下的性能。

### @Setup

`@Setup` 会在执行 benchmark 之前被执行，正如其名，主要用于初始化。

### @TearDown

`@TearDown` 和 `@Setup` 相对的，会在所有 benchmark 执行结束以后执行，主要用于资源的回收等。

最后来猜猜看实际结果如何？并行算法在哪个问题集下能够超越串行算法？

我在自己的 mac 上跑下来的结果，总数在10000时并行算法不如串行算法，总数达到100000时并行算法开始和串行算法接近，总数达到1000000时并行算法所耗时间约是串行算法的一半左右。

# 常用选项

还有一些 JMH 的常用选项没有提及的，简单地在此介绍一下

### CompilerControl

控制 compiler 的行为，例如强制 inline，不允许编译等。

### Group

可以把多个 benchmark 定义为同一个 group，则它们会被同时执行，主要用于测试多个相互之间存在影响的方法。

### Level

用于控制 `@Setup`，`@TearDown` 的调用时机，默认是 `Level.Trial`，即benchmark开始前和结束后。

### Profiler

JMH 支持一些 profiler，可以显示等待时间和运行时间比，热点函数等。

# 延伸阅读

## IDE插件

IntelliJ 有 JMH 的[插件](https://github.com/artyushov/idea-jmh-plugin)，提供 benchmark 方法的自动生成等便利功能。

## JMH 教程

Jenkov 的 JMH [教程](http://tutorials.jenkov.com/java-performance/jmh.html)，相比于这篇文章介绍得更为详细，非常推荐。顺便 Jenkov 的其他 Java 教程也非常值得一看。

# 附录

## 代码清单

```
public class SinglethreadCalculator implements Calculator {



    public long sum(int[] numbers) {



        long total = 0L;



        for (int i : numbers) {



            total += i;



        }



        return total;



    }



 



    @Override



    public void shutdown() {



        // nothing to do



    }



}



 



public class MultithreadCalculator implements Calculator {



    private final int nThreads;



    private final ExecutorService pool;



 



    public MultithreadCalculator(int nThreads) {



        this.nThreads = nThreads;



        this.pool = Executors.newFixedThreadPool(nThreads);



    }



 



    private class SumTask implements Callable<Long> {



        private int[] numbers;



        private int from;



        private int to;



 



        public SumTask(int[] numbers, int from, int to) {



            this.numbers = numbers;



            this.from = from;



            this.to = to;



        }



 



        public Long call() throws Exception {



            long total = 0L;



            for (int i = from; i < to; i++) {



                total += numbers[i];



            }



            return total;



        }



    }



 



    public long sum(int[] numbers) {



        int chunk = numbers.length / nThreads;



 



        int from, to;



        List<SumTask> tasks = new ArrayList<SumTask>();



        for (int i = 1; i <= nThreads; i++) {



            if (i == nThreads) {



                from = (i - 1) * chunk;



                to = numbers.length;



            } else {



                from = (i - 1) * chunk;



                to = i * chunk;



            }



            tasks.add(new SumTask(numbers, from, to));



        }



 



        try {



            List<Future<Long>> futures = pool.invokeAll(tasks);



 



            long total = 0L;



            for (Future<Long> future : futures) {



                total += future.get();



            }



            return total;



        } catch (Exception e) {



            // ignore



            return 0;



        }



    }



 



    @Override



    public void shutdown() {



        pool.shutdown();



    }



}
```

 





http://tutorials.jenkov.com/java-performance/jmh.html

# JMH - Java Microbenchmark Harness

- [Why Are Java Microbenchmarks Hard?](http://tutorials.jenkov.com/java-performance/jmh.html#why-are-java-microbenchmarks-hard)
- [Getting Started With JMH](http://tutorials.jenkov.com/java-performance/jmh.html#getting-started-with-jmh)
- [Your First JMH Benchmark](http://tutorials.jenkov.com/java-performance/jmh.html#your-first-jmh-benchmark)
- [Building Your JMH Benchmark](http://tutorials.jenkov.com/java-performance/jmh.html#building-your-jmh-benchmark)
- [The benchmarks.jar File](http://tutorials.jenkov.com/java-performance/jmh.html#the-benchmarks-jar-file)
- [Running Your JMH Benchmarks](http://tutorials.jenkov.com/java-performance/jmh.html#running-your-jmh-benchmarks)
- [JMH Benchmark Modes](http://tutorials.jenkov.com/java-performance/jmh.html#jmh-benchmark-modes)
- [Benchmark Time Units](http://tutorials.jenkov.com/java-performance/jmh.html#benchmark-time-units)
- Benchmark State
  - [State Scope](http://tutorials.jenkov.com/java-performance/jmh.html#state-scope)
  - [State Class Requirements](http://tutorials.jenkov.com/java-performance/jmh.html#state-class-requirements)
  - [State Object @Setup and @TearDown](http://tutorials.jenkov.com/java-performance/jmh.html#state-setup-and-teardown)
- [Writing Good Benchmarks](http://tutorials.jenkov.com/java-performance/jmh.html#writing-good-benchmarks)
- [Loop Optimizations](http://tutorials.jenkov.com/java-performance/jmh.html#loop-optimizations)
- Dead Code Elimination
  - [Avoiding Dead Code Elimination](http://tutorials.jenkov.com/java-performance/jmh.html#avoiding-dead-code-elimination)
  - [Return Value From Benchmark Method](http://tutorials.jenkov.com/java-performance/jmh.html#return-value-from-benchmark-method)
  - [Passing Value to a Black Hole](http://tutorials.jenkov.com/java-performance/jmh.html#passing-value-to-a-black-hole)
- Constant Folding
  - [Avoiding Constant Folding](http://tutorials.jenkov.com/java-performance/jmh.html#avoiding-constant-folding)

|      | Jakob Jenkov Last update: 2015-09-16[![img](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABpElEQVRIx2NgwAOUlZWVFBUVqxQUFPYC8XMg/gvFIPZekBxIDQOpQAkIgAashhr2nwAGqVkN0kOU4UBXxQA1fCbCYHT8GaSXkOFlZBiMgkFm4HM5RYYjWYLqE2iYkxMsOIMLJU6gEUqqIaCUdB1PQlgNT4rYFAG9uRVXqgHKpejp6TFBfa8BFJsPpEHx9xtZHTgJQ9M5hkEqKipyQLkkIPs7mtxM9PizsLBgAloQBZR7jObIKgZoJsKwAKjBCOpCNSB/KcwioKYIbIkEKLceizl7GaBhiS0lLNXS0mKCGaCmpsYDtMwO6G05HBZgSyTPGXBFEtAgI3V1dS5iMqeqqqoIrvjCaQEQzyW2aAH6NgSfBc9xSILioQIYTByELACq3Y4rKeOMZGg81BEyHOgIFzx5ZS/OZIqEF4LiA4fhckD5p3gcWIUro4GS5FsgPg5UVASMRC4shpsA5R/iK8bhdQWWogJkwUSgIXrIhurr64MylBkoAaDlWtxFBRGF3Xsgvgwtd4gtED9jVEA0La6RLKFdhYPmE9pUmWhxQptKHxlQo9kCAHsFA8aGHksTAAAAAElFTkSuQmCC)](https://twitter.com/#!/jjenkov) [![img](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABEklEQVRIx2NgwAOUlZWVFBUVqxQUFPYC8XMg/gvFIPZekBxIDQOpQAkIgAashhr2nwAGqVkN0kOU4UBXxQA1fCbCYHT8GaSXkOFlZBiMgkFm4HM5RYYjWYLqE2iYkxMsOIMLJU6gEYpL8XcoJtWS1fCkiCe1fAfKy4AwGZb8BSdhaDr/TwMLQHFRxQDNRP9pEEQgvJcBmitxKkKKp/9IKa5bTU2NT0VFRQoovh+P/ucMhHIrNguABosAg00MmgJ18MUDWRYA2beB+D6IbW1tzUTIApKDCCbX0tLChMzHFUR7aWjBXkLJlCILwMmUQEajBP+F1xUEigpy8Wr6FXY0L67pUuHQpcpEixPaVPrIgBrNFgAzO0iIN1MJVQAAAABJRU5ErkJggg==)](http://www.linkedin.com/pub/jakob-jenkov/0/a8/4a3) [![img](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABNElEQVRIx7VWSwrCMBANxYW48gTS2kJFaBfiHdq1uxbP4cJNz+K6eIQeR3oAlyI6T0Zpwlj7MYEHJZN5k8zMS6pUy/B9f+l53tF13YpQE+4MfFewYY3qO5Y0iKBksscPYE0Jn07ktKs9OVw7EJu4wvcX+WEAsQZwtO18FHkjiH4SzvmQtHxNl1YTLui/yN8oP60odMuFjrkLgmARhuE8juNpkiSToigcAN+Ygw1rsBY+Zne9Wpj73Mxh3re14SPwHBWLSDNgV4Lo3LYA8BHSVClWpWaIomhmEtD8jXCi2q2lAPARAtRKUmue544QoKncMwXaNu1ZljmSyscE2HQN0DdFq74psltk623aVWhpmg4TGufX3lWBYf2y4xzau64bQew9OMZJ7DyZRk3sPPqGuEb/tjwB4iHvG88CuqcAAAAASUVORK5CYII=)](https://www.youtube.com/user/jjenkov) [![img](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABvElEQVRIx2NgwAOUlZWVFBUVqxQUFPYC8XMg/gvFIPZekBxIDQOpQAkIgAashhr2nwAGqVkN0kOU4UBXxQA1fCbCYHT8GaSXkOFlZBiMgkFm4HM5RYYjWYLqE2iYowfLX6DCbqBUBDAiXUDqjIyMmDQ1NbmAcguR1YLk0IMLJU6gEYrhVSC2g0U0kD0V6tOp6GqxWADCq+FJEUtq+a2mpgZyaTeyONBRGqqqqhLIBqMD5BAAJ2FoOsdIEdgiHchP0NbWZiPSByD1VQzQTIQhCXStEdAFMkD2RyQNfkAcQawFILMZoLkSm+RloCUqQGwAZC8GGtwOZHuRmEeeMxDIrb+B+CTQYDOoK9+SmGT/ErIAFjRh0DhJgVpKkgU4gwhoYBHQ9TlAXALEFnp6ekxA2g45XogJImyRvFxdXR2UTNeiiR9WUVHhgfqEGAv2Yk2mQEPkgOJxOIIrBygvQ2SRUYU1o+no6HABJaNwWQBNWQTDH15XoBcVQENKgEHEAmQvRdO0E5iTBYD0ZiIsWE2osFsIilCggTpAl9gAg8UEaHEAUPw4EYZ/xqiAaFpc06XCoUuVSZdKHxlQo9kCAHcMPgoKWH+jAAAAAElFTkSuQmCC)](https://plus.google.com/+JakobJenkov?rel=author) [![img](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABqUlEQVRIx71WwUrDQBANEqQnP6AUSZo0JDnkByLSU/HkB0g/o0jJVUrx5MGvkHxDzuKxZ/HgoeQsOXiQom9kVjbJZhON7cKDbDI7M/vezG4MQzMcxxnbtp1YlpUBObBj0HNG38jG+O0YY8BBys4+W0A2Ka3p5BxZzbGg6OC4ioLWtjm//oPjEsiHLvNezqUg5Z0w5zVa4jg2XdcdYsEM81vgtStdJU1Y0JphdZdBEJgIdtUxUPpTippquYfDJZKZknMRCLs6wbeHtur6LmGu8y7bzmG78DzvWNLtrkWLxOAmUhog01PKHs8rYMvvNzK/LTvJDO5KpYHM/2QyGSCjNdO5FUGYriZNckPXrcQ/VZDv+6ZEy5zXbARdLLxSB20ACc9wciYFWXMCC5qHYXjUsIudliLgA3gC3oB3EYToYk1yUV3cJ0qKGkUGzZdcyiMO8iLoQrAbtpnyfKYUWVemURQNpGp5ZFouuPvPhU4s9lBZprpGg8GKgtBOmC56n7DDkWhGmtOxomw03VHRE2nrYdcDRe0C2utxfZAL5yBXZkWT/Vz68viP35Yv1q4mS+AFuV8AAAAASUVORK5CYII=)](http://jenkov.com/rss.xml) |
| ---- | ------------------------------------------------------------ |
|      |                                                              |

*JMH* is short for *Java Microbenchmark Harness*. JMH is a toolkit that helps you implement Java microbenchmarks correctly. JMH is developed by the same people who implement the Java virtual machine, so these guys know what they are doing. This JMH tutorial will teach you how to implement and run Java microbenchmarks with JMH.



## Why Are Java Microbenchmarks Hard?

Writing benchmarks that correctly measure the performance of a small part of a larger application is hard. There are many optimizations that the JVM or underlying hardware may apply to your component when the benchmark executes that component in isolation. These optimizations may not be possible to apply when the component is running as part of a larger application. Badly implemented microbenchmarks may thus make you believe that your component's performance is better than it will be in reality.

Writing a correct Java microbenchmark typically entails preventung the optimizations the JVM and hardware may apply during microbenchmark execution which could not have been applied in a real production system. That is what JMH - the Java Microbenchmark Harness - is helping you do.



## Getting Started With JMH

The easiest way to get started with JMH is to generate a new JMH project using the JMH Maven archetype. The JMH Maven archetype will generate a new Java project with a single, example benchmark Java class, and a Maven `pom.xml` file. The Maven `pom.xml` file contains the correct dependencies to compile and build your JMH microbenchmark suite.

Here is the Maven command line needed to generate a JMH project template:

```
 mvn archetype:generate
          -DinteractiveMode=false
          -DarchetypeGroupId=org.openjdk.jmh
          -DarchetypeArtifactId=jmh-java-benchmark-archetype
          -DgroupId=com.jenkov
          -DartifactId=first-benchmark
          -Dversion=1.0
```

This is one long command. There should be no line breaks in the command. I just added them to make the command easier to read.

This command line will create a new directory named `first-benchmark` (the `artifactId` specified in the Maven command). Inside this directory will be generated a new Maven source directory structure (`src/main/java`). Inside the `java` source root directory will be generated a single Java packaged named `com.jenkov` (actually a package named `com` with a subpackage named `jenkov`). Inside the `com.jenkov`package will be a JMH benchmark Java class named `MyBenchmark`.



## Your First JMH Benchmark

It is time to write your first JMH benchmark class, or at least see how it is done.

The generated `MyBenchmark` class is a JMH class template which you can use to implement your JMH benchmarks. You can either implement your benchmarks directly in the generated `MyBenchmark` class, or create a new class in the same Java package. To make it easy for you to write your first JMH benchmark I will just use the generated class in this example.

Here is first how the generated `MyBenchmark` class looks:

```
package com.jenkov;

import org.openjdk.jmh.annotations.Benchmark;

public class MyBenchmark {

    @Benchmark
    public void testMethod() {
        // This is a demo/sample template for building your JMH benchmarks. Edit as needed.
        // Put your benchmark code here.
    }

}
```

You can put the code you want to measure inside the `testMethod()` method body. Here is an example:

```
package com.jenkov;

import org.openjdk.jmh.annotations.Benchmark;

public class MyBenchmark {

    @Benchmark
    public void testMethod() {
        // This is a demo/sample template for building your JMH benchmarks. Edit as needed.
        // Put your benchmark code here.

        int a = 1;
        int b = 2;
        int sum = a + b;
    }

}
```

Note: This particular example is a bad benchmark implementation, as the JVM can see that `sum` is never used, and may thus eliminate the sum calculation. Well in fact the whole method body could be removed by JVM dead code elimination. For now, just imagine that the `testMethod()` body actually contained a good benchmark implementation. I will get back how to implement better benchmarks with JMH later in this tutorial.



## Building Your JMH Benchmark

You can now compile and build a benchmark JAR file from your JMH benchmark project using this Maven command:

```
mvn clean install
```

This Maven command must be executed from inside the generated benchmark project directory (in this example the `first-benchmark` directory).

When this command is executed a JAR file will be created inside the `first-benchmark/target` directory. The JAR file will be named `benchmarks.jar`



## The benchmarks.jar File

When you build your JMH benchmarks, Maven will always generate a JAR file named `benchmarks.jar` in the `target` directory (Maven's standard output directory).

The `benchmarks.jar` file contains everything needed to run your benchmarks. It contains your compiled benchmark classes as well as all JMH classes needed to run the benchmark.

If your benchmarks has any external dependencies (JAR files from other projects needed to run your benchmarks), declare these dependencies inside the Maven `pom.xml`, and they will be included in the `benchmarks.jar` too.

Since `benchmarks.jar` is fully self contained, you can copy that JAR file to another computer to run your JMH benchmarks on that computer.



## Running Your JMH Benchmarks

Once you have built your JMH benchmark code you can run the benchmark using this Java command:

```
java -jar target/benchmarks.jar
```

This will start JMH on your benchmark classes. JMH will scan through your code and find all benchmarks and run them. JMH will print out the results to the command line.

Running the benchmarks will take some time. JMH makes several warm ups, iterations etc. to make sure the results are not completely random. The more runs you have, the better average performance and high / low performance information you get.

You should let the computer alone while it runs the benchmarks, and you should close all other applications (if possible). If your computer is running other applications, these applications may take time from the CPU and give incorrect (lower) performance numbers.



## JMH Benchmark Modes

JMH can run your benchmarks in different modes. The benchmark mode tells JMH what you want to measure. JMH offer these benchmark modes:

| Throughput       | Measures the number of operations per second, meaning the number of times per second your benchmark method could be executed. |
| ---------------- | ------------------------------------------------------------ |
| Average Time     | Measures the average time it takes for the benchmark method to execute (a single execution). |
| Sample Time      | Measures how long time it takes for the benchmark method to execute, including max, min time etc. |
| Single Shot Time | Measures how long time a single benchmark method execution takes to run. This is good to test how it performs under a cold start (no JVM warm up). |
| All              | Measures all of the above.                                   |

The default benchmark mode is Throughput.

You specify what benchmark mode your benchmark should use with the JMH annotation `BenchmarkMode`. You put the `BenchmarkMode` annotation on top of your benchmark method. Here is a JMH `BenchmarkMode`example:

```
package com.jenkov;

import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.annotations.BenchmarkMode;
import org.openjdk.jmh.annotations.Mode;

public class MyBenchmark {

    @Benchmark @BenchmarkMode(Mode.Throughput)
    public void testMethod() {
        // This is a demo/sample template for building your JMH benchmarks. Edit as needed.
        // Put your benchmark code here.

        int a = 1;
        int b = 2;
        int sum = a + b;
    }

}
```

Notice the `@BenchmarkMode(Mode.Throughput)` annotation above the `testMethod()` method. That annotation specifies the benchmark mode. The `Mode` class contains constants for each possible benchmark mode.



## Benchmark Time Units

JMH enables you to specify what time units you want the benchmark results printed in. The time unit will be used for all benchmark modes your benchmark is executed in.

You specify the benchmark time unit using the JMH annotation `@OutputTimeUnit`. The `@OutputTimeUnit`annotation takes a `java.util.concurrent.TimeUnit` as parameter to specify the actual time unit to use. Here is a JMH `@OutputTimeUnit` annotation example:

```
package com.jenkov;

import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.annotations.BenchmarkMode;
import org.openjdk.jmh.annotations.Mode;
import org.openjdk.jmh.annotations.OutputTimeUnit;

import java.util.concurrent.TimeUnit;

public class MyBenchmark {

    @Benchmark @BenchmarkMode(Mode.Throughput) @OutputTimeUnit(TimeUnit.MINUTES)
    public void testMethod() {
        // This is a demo/sample template for building your JMH benchmarks. Edit as needed.
        // Put your benchmark code here.

        int a = 1;
        int b = 2;
        int sum = a + b;
    }

}
```

In this example the time unit specified is minutes. This means that you want the output shown using the time unit minutes (e.g. operations per minute).

The `TimeUnit` class contains the following time unit constants:

- NANOSECONDS
- MICROSECONDS
- MILLISECONDS
- SECONDS
- MINUTES
- HOURS
- DAYS



## Benchmark State

Sometimes you way want to initialize some variables that your benchmark code needs, but which you do not want to be part of the code your benchmark measures. Such variables are called "state" variables. State variables are declared in special state classes, and an instance of that state class can then be provided as parameter to the benchmark method. This may sound a bit complicated, so here is a JMH benchmark state example:

```
package com.jenkov;

import org.openjdk.jmh.annotations.*;

import java.util.concurrent.TimeUnit;


public class MyBenchmark {

    @State(Scope.Thread)
    public static class MyState {
        public int a = 1;
        public int b = 2;
        public int sum ;
    }


    @Benchmark @BenchmarkMode(Mode.Throughput) @OutputTimeUnit(TimeUnit.MINUTES)
    public void testMethod(MyState state) {
        state.sum = state.a + state.b;
    }

}
```

In this example I have added a nested static class named `MyState`. The `MyState` class is annotated with the JMH `@State` annotation. This signals to JMH that this is a state class. Notice that the `testMethod()`benchmark method now takes an instance of `MyState` as parameter.

Notice also that the `testMethod()` body has now been changed to use the `MyState` object when performing its sum calculation.



### State Scope

A state object can be reused across multiple calls to your benchmark method. JMH provides different "scopes" that the state object can be reused in. There state scope is specified in the parameter of the `@State` annotation. In the example above the scope chosen was `Scope.Thread`

The `Scope` class contains the following scope constants:

| Thread    | Each thread running the benchmark will create its own instance of the state object. |
| --------- | ------------------------------------------------------------ |
| Group     | Each thread group running the benchmark will create its own instance of the state object. |
| Benchmark | All threads running the benchmark share the same state object. |



### State Class Requirements

A JMH state class must obey the following rules:

- The class must be declared `public`
- If the class is a nested class, it must be declared `static` (e.g. `public static class ...`)
- The class must have a public no-arg constructor (no parameters to the constructor).

When these rules are obeyed you can annotate the class with the `@State` annotation to make JMH recognize it as a state class.



### State Object @Setup and @TearDown

You can annotate methods in your state class with the `@Setup` and `@TearDown` annotations. The `@Setup`annotation tell JMH that this method should be called to setup the state object before it is passed to the benchmark method. The `@TearDown` annotation tells JMH that this method should be called to clean up ("tear down") the state object after the benchmark has been executed.

The setup and tear down execution time is not included in the benchmark runtime measurements.

Here is a JMH state object example that shows the use of the `@Setup` and `@TearDown` annotations:

```
package com.jenkov;

import org.openjdk.jmh.annotations.*;

import java.util.concurrent.TimeUnit;


public class MyBenchmark {

    @State(Scope.Thread)
    public static class MyState {

        @Setup(Level.Trial)
        public void doSetup() {
            sum = 0;
            System.out.println("Do Setup");
        }

        @TearDown(Level.Trial)
        public void doTearDown() {
            System.out.println("Do TearDown");
        }

        public int a = 1;
        public int b = 2;
        public int sum ;
    }

    @Benchmark @BenchmarkMode(Mode.Throughput) @OutputTimeUnit(TimeUnit.MINUTES)
    public void testMethod(MyState state) {
        state.sum = state.a + state.b;
    }
}
```

Notice the two new methods in the `MyState` class named `doSetup()` and `doTearDown()`. These methods are annotated with the `@Setup` and `@TearDown` annotations. This example only show two methods, but you could have more methods annotated with `@Setup` and `@TearDown`.

Notice also that the annotations take a parameter. There are three different values this parameter can take. The value you set instruct JMH about when the method should be called. The possible values are:

| Level.Trial      | The method is called once for each time for each full run of the benchmark. A full run means a full "fork" including all warmup and benchmark iterations. |
| ---------------- | ------------------------------------------------------------ |
| Level.Iteration  | The method is called once for each iteration of the benchmark. |
| Level.Invocation | The method is called once for each call to the benchmark method. |

If you have any doubts about when a setup or tear down method is called, try inserting a `System.out.println()` statement in the method. Then you will see. Then you can change the `@Setup` and `@TearDown()` parameter values until your setup and tear down methods are called at the right time.



## Writing Good Benchmarks

Now that you have seen how to use JMH to write benchmarks, it is time to discuss how to write *good benchmarks*. As mentioned in the beginning of this JMH tutorial there are a couple of pitfalls that you can easily fall into when implementing benchmarks. I will discuss some of these pitfalls in the following sections.

One common pitfall is that the JVM may apply optimizations to your components when executed inside the benchmark which could not have been applied if the component was executed inside your real application. Such optimizations will make your code look faster than it will be in reality. I will discuss some of these optimizations later.



## Loop Optimizations

It is tempting to put your benchmark code inside a loop in your benchmark methods, in order to repeat it more times per call to the benchmark method (to reduce the overhead of the benchmark method call). However, the JVM is very good at optimizing loops, so you may end up with a different result than what you expected. In general you should avoid loops in your benchmark methods, unless they are part of the code you want to measure (and not *around* the code you want to measure).



## Dead Code Elimination

One of the JVM optimizations to avoid when implementing performance benchmarks is dead code elimination. If the JVM detects that the result of some computation is never used, the JVM may consider this computation *dead code* and eliminate it. Look at this benchmark example:

```
package com.jenkov;

import org.openjdk.jmh.annotations.Benchmark;

public class MyBenchmark {

    @Benchmark
    public void testMethod() {
        int a = 1;
        int b = 2;
        int sum = a + b;
    }

}
```

The JVM can detect that the calculation of `a + b` which is assigned to `sum` is never used. Therefore the JVM can remove the calculation of `a + b` altogether. It is considered dead code. The JVM can then detect that the `sum` variable is never used, and that subsequently `a` and `b` are never used. They too can be eliminated.

In the end, there is no code left in the benchmark. The results from running this benchmark are thus highly misleading. The benchmarks do not actually measure the time of adding two variables and assigning the value to a third variable. The benchmarks measure nothing at all.



### Avoiding Dead Code Elimination

To avoid dead code elimination you must make sure that the code you want to measure does not look like dead code to the JVM. There are two ways to do that.

- Return the result of your code from the benchmark method.
- Pass the calculated value into a "black hole" provided by JMH.

I will show you examples of both methods in the following sections.



### Return Value From Benchmark Method

Returning a computed value from the JMH benchmark method could look like this:

```
package com.jenkov;

import org.openjdk.jmh.annotations.Benchmark;

public class MyBenchmark {

    @Benchmark
    public int testMethod() {
        int a = 1;
        int b = 2;
        int sum = a + b;

        return sum;
    }

}
```

Notice how the `testMethod()` method now returns the `sum` variable. This way the JVM cannot just eliminate the addition, because the return value might be used by the caller. JMH will take of tricking the JVM into believing that the return value is actually used.

If your benchmark method is calculating multiple values that might end up being eliminated as dead code, you can either combine the two values into a single, and return that value (e.g. an object with both values in).



### Passing Value to a Black Hole

An alternative to returning a combined value is to pass the calculated values (or returned / generated objects or whatever the result of your benchmark is) into a JMH *black hole*. Here is how passing values into a black hole looks:

```
package com.jenkov;

import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.infra.Blackhole;

public class MyBenchmark {

    @Benchmark
   public void testMethod(Blackhole blackhole) {
        int a = 1;
        int b = 2;
        int sum = a + b;
        blackhole.consume(sum);
    }
}
```

Notice how the `testMethod()` benchmark method now takes a `Blackhole` object as parameter. This will be provided to the test method by JMH when called.

Notice also how the calculated sum in the `sum` variable is now passed to the `consume()` method of the `Blackhole` instance. This will fool the JVM into thinking that the `sum` variable is actually being used.

If your benchmark method produces multiple results you can pass each of these results to a black hole, meaning calling `consume()` on the `Blackhole` instance for each value.



## Constant Folding

Constant folding is another common JVM optimization. A calculation which is based on constants will often result in the exact same result, regardless of how many times the calculation is performed. The JVM may detect that, and replace the calculation with the result of the calculation.

As an example, look at this benchmark:

```
package com.jenkov;

import org.openjdk.jmh.annotations.Benchmark;

public class MyBenchmark {

    @Benchmark
    public int testMethod() {
        int a = 1;
        int b = 2;
        int sum = a + b;

        return sum;
    }

}
```

The JVM may detect that the value of `sum` is based on the two constant values 1 and 2 in `a` and `b`. It may thus replace the above code with this:

```
package com.jenkov;

import org.openjdk.jmh.annotations.Benchmark;

public class MyBenchmark {

    @Benchmark
    public int testMethod() {
        int sum = 3;

        return sum;
    }

}
```

Or even just `return 3;` directly. The JVM could even continue and never call the `testMethod()` because it knows it always returns 3, and just inline the constant 3 wherever the `testMethod()` was to be called.



### Avoiding Constant Folding

To avoid constant folding you must not hardcode constants into your benchmark methods. Instead, the input to your calculations should come from a state object. This makes it harder for the JVM to see that the calculations are based on constant values. Here is an example:

```
package com.jenkov;

import org.openjdk.jmh.annotations.*;

public class MyBenchmark {

    @State(Scope.Thread)
    public static class MyState {
        public int a = 1;
        public int b = 2;
    }


    @Benchmark 
    public int testMethod(MyState state) {
        int sum = state.a + state.b;
        return sum;
    }
}
```

Remember, if your benchmark method calculates multiple values you can pass them through a black hole instead of returning them, to also avoid the dead code elimination optimization. For instance:

```
    @Benchmark
    public void testMethod(MyState state, Blackhole blackhole) {
        int sum1 = state.a + state.b;
        int sum2 = state.a + state.a + state.b + state.b;

        blackhole.consume(sum1);
        blackhole.consume(sum2);
    }
```

Next: [Java Ring Buffer](http://tutorials.jenkov.com/java-performance/ring-buffer.html)