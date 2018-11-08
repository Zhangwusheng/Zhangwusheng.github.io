https://www.quora.com/HBase-follows-which-features-of-CAP-theorem



https://stackoverflow.com/questions/14950728/why-hbase-is-a-better-choice-than-cassandra-with-hadoop

   

一致性，CAP原理



预分区之后如果达到了文件大小是不是还是会分区

不同的CF可以有不同的Region数目？



​      77         down vote            accepted   

I don't think either is better than the others, it's not just one or  the other. These are very different systems, each with their strengths  and weaknesses, so it really depends on your use cases. They can  definitely be used in complement of one another in the same  infrastructure.

To explain the difference better I'd like to borrow a picture from [Cassandra: the Definitive Guide](http://rads.stackoverflow.com/amzn/click/1449390412), where they go over the CAP theorem. What they say is basically for any distributed system, you have to find a balance between **consistency**, **availability** and **partition tolerance**, and you can only realistically satisfy 2 of these properties. From that you can see that:

- Cassandra satisfies the **Availability** and **Partition Tolerance** properties.
- HBase satisfied the **Consistency** and **Partition Tolerance** properties.

![CAP](https://i.stack.imgur.com/53GeC.png)

When it comes to Hadoop, HBase is built on top of HDFS, which makes  it pretty convenient to use if you already have a Hadoop stack. It is  also supported by Cloudera, which is a standard enterprise distribution  for Hadoop.

But Cassandra also has more integration with Hadoop, namely Datastax  Brisk which is gaining popularity. You can also now natively stream data  from the output of a Hadoop job into a Cassandra cluster using some  Cassandra-provided output format (`BulkOutputFormat` for example), we are no longer to the point where Cassandra was just a standalone project.

In my experience, I've found that Cassandra is awesome for random reads, and not so much for scans

To put a little color to the picture, I've been using both at my job  in the same infrastructure, and HBase has a very different purpose than  Cassandra. I've used Cassandra mostly for real-time very fast lookups,  while I've used HBase more for heavy ETL batch jobs with lower latency  requirements.

This is a question that would truly be worthy of a blog post, so instead of going on and on I'd like to point you to [an article](http://bigdatanoob.blogspot.com/2012/11/hbase-vs-cassandra.html)  which sums up a lot of the keys differences between the 2 systems.  Bottom line is, there is no superior solution IMHO, and you should  really think about your use cases to see which system is better suited.

[share](https://stackoverflow.com/a/14951403)[improve this answer](https://stackoverflow.com/posts/14951403/edit)



http://yangshangchuan.iteye.com/blog/2002544





The short summary of the article is that CAP isn’t “C, A, or P, choose
two,” but rather “When P happens, choose A or C.”

Partitions, like death and taxes, are unavoidable – think of machine
death as just a partition of that machine out into the networking
equivalent of the afterlife. So it’s up to the system designer to
decide if, when that happens, we give up availability or give up
consistency.

In HBase’s case we choose consistency, so we have to give up some availability. 这个理解CAP，太到位了
--------------------- 
作者：JamesFen 
来源：CSDN 
原文：https://blog.csdn.net/jameshadoop/article/details/46608711 
版权声明：本文为博主原创文章，转载请附上博文链接！



