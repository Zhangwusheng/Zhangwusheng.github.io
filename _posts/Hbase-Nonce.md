---
layout:     post
title:     HBase的Nonce实现分析
subtitle:  HBase的Nonce实现分析
date:       2018-09-20
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - HBase
    - Nonce
---

# HBase的Nonce实现分析

一、问题背景

        当客户端发送RPC请求给服务端时，基于各种原因，服务器的响应很可能会超时。如果客户端只是在那等待，针对数据的操作，很可能出现服务器端已处理完毕，但是无法通知客户端，此时，客户端只能重新发起请求，可是又可能造成服务端重复处理请求。该如何解决该问题呢？

        二、解决方案

        实际上，客户端发送RPC请求给服务器后，如果响应超时，那么客户端会重复发送请求，直到达到参数配置的重试次数上限。而且，客户端第一次发送和以后重发请求时，会附带相同的nonce，服务端只要根据nonce进行判断，就能得知是否为同一请求，并根据之前请求处理的结果，决定是等待、拒绝还是直接处理。

        三、HBase如何实现的

        在HRegionServer中，有一个ServerNonceManager类型的成员变量nonceManager，由它负责管理该RegionServer上的nonce。其定义如下：

        

final ServerNonceManager nonceManager;

        ServerNonceManager中有一个十分重要的方法，用于当一个操作在服务端执行后未及时反馈响应给客户端，客户端重新发起携带相同nonceGroup和nonce的同一操作的请求时，服务端根据nonceGroup和nonce做相应的判断。定义如下：

/**
   * Starts the operation if operation with such nonce has not already succeeded. If the
   * operation is in progress, waits for it to end and checks whether it has succeeded.
   * 
   * 如果操作未执行成功，重新开始一个操作。如果该操作在进行过程中，等待它完成并判断它是否成功。
   * @param group Nonce group.
   * @param nonce Nonce.
   * @param stoppable Stoppable that terminates waiting (if any) when the server is stopped.
   * @return true if the operation has not already succeeded and can proceed; false otherwise.
        */
          public boolean startOperation(long group, long nonce, Stoppable stoppable)
      throws InterruptedException {
    // 如果传入的nonce为0，则返回true，表明操作可以进行
    if (nonce == HConstants.NO_NONCE) return true;
    
    // 构造NonceKey实例nk
    NonceKey nk = new NonceKey(group, nonce);
    // 构造OperationContext实例ctx，初始状态为WAIT
    OperationContext ctx = new OperationContext();
    while (true) {
      // 将NonceKey到OperationContext的映射，添加到ConcurrentHashMap类型的nonces中去
      OperationContext oldResult = nonces.putIfAbsent(nk, ctx);
      // 如果之前没有，则说明该操作可以直接执行
      if (oldResult == null) return true;
     
      // Collision with some operation - should be extremely rare.
      // 如果之前存在该操作，则取出该操作nonce对应的OperationContext
      synchronized (oldResult) {
    	// 获得该nonce对应的OperationContext状态
        int oldState = oldResult.getState();
        LOG.debug("Conflict detected by nonce: " + nk + ", " + oldResult);
        // 如果之前的状态不是WAIT
        if (oldState != OperationContext.WAIT) {
          // 如果之前的状态是PROCEED，说明之前的操作执行完成且以失败告终，此处返回true，表示操作可以再次执行
          return oldState == OperationContext.PROCEED; // operation ended
        }
        
        // 等待一段时间后继续循环
        oldResult.setHasWait();
        oldResult.wait(this.conflictWaitIterationMs); // operation is still active... wait and loop
        
        // 判断RegionServer的状态
        if (stoppable.isStopped()) {
          throw new InterruptedException("Server stopped");
        }
      }
    }
  }
        在RSRpcServices的append()方法中，有如下代码：
if (r == null) {
      long nonce = startNonceOperation(m, nonceGroup);
      boolean success = false;
      try {
        r = region.append(append, nonceGroup, nonce);
        success = true;
      } finally {
        endNonceOperation(m, nonceGroup, success);
      }
      if (region.getCoprocessorHost() != null) {
        region.getCoprocessorHost().postAppend(append, r);
      }
    }
        其中，startNonceOperation()方法源码如下：
/**
   * Starts the nonce operation for a mutation, if needed.
   * 
   * 如果需要的话，为mutation开启一个nonce操作
   * 
   * @param mutation Mutation.
   * @param nonceGroup Nonce group from the request.
   * @returns Nonce used (can be NO_NONCE).
        */
          private long startNonceOperation(final MutationProto mutation, long nonceGroup)
      throws IOException, OperationConflictException {
    
    // 如果RegionServer上的nonceManager为null，或者该mutation不存在nonce，那么直接返回HConstants.NO_NONCE，即0
    if (regionServer.nonceManager == null || !mutation.hasNonce()) return HConstants.NO_NONCE;
    // 标志位，是否可以运行
    boolean canProceed = false;
    try {
      // 调用RegionServer上nonceManager的startOperation()方法，确定是否可以执行该操作
      canProceed = regionServer.nonceManager.startOperation(
        nonceGroup, mutation.getNonce(), regionServer);
    } catch (InterruptedException ex) {
      throw new InterruptedIOException("Nonce start operation interrupted");
    }
    
    if (!canProceed) {// 如果不能运行，抛出OperationConflictException异常，即操作冲突异常
      // TODO: instead, we could convert append/increment to get w/mvcc
      String message = "The operation with nonce {" + nonceGroup + ", " + mutation.getNonce()
        + "} on row [" + Bytes.toString(mutation.getRow().toByteArray())
        + "] may have already completed";
      throw new OperationConflictException(message);
    }
    
    // 最后，返回mutation的nonce
    return mutation.getNonce();
  }

        它会调用RegionServer上nonceManager的startOperation()方法，确定是否可以执行该操作。

---------------------
作者：辰辰爸的技术博客 
来源：CSDN 
原文：https://blog.csdn.net/lipeng_bigdata/article/details/50464441 
版权声明：本文为博主原创文章，转载请附上博文链接！