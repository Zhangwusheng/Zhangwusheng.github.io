---
layout:     post
title:     Ambari安装HDP3.0.0
subtitle:   用Ambari2.7安装HDP3.0.0
date:       2018-09-22
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - Ambari
    - Hadoop
    - HDP
typora-copy-images-to: ..\img
typora-root-url: ..
---



# 0.参考文章：

Ambari官方文档

https://docs.hortonworks.com/HDPDocuments/Ambari-2.7.0.0/bk_ambari-installation/content/setting_up_a_local_repository_with_temporary_internet_access.html

网上的一篇博客

https://www.cnblogs.com/zhang-ke/p/8944240.html

# 1.下载离线安装包

- [ ] 下载页面：

- ambari2.7.0.0下载页面:
  https://docs.hortonworks.com/HDPDocuments/Ambari-2.7.0.0/bk_ambari-installation/content/ambari_repositories.html

- hdp-3.0.0下载页面:
  https://docs.hortonworks.com/HDPDocuments/Ambari-2.7.0.0/bk_ambari-installation/content/hdp_30_repositories.html

- hdp-3.1.0下载页面:

  https://docs.hortonworks.com/HDPDocuments/Ambari-2.7.3.0/bk_ambari-installation/content/hdp_31_repositories.html

- [ ] ambari-2.7.0.0


- wget -c 'http://public-repo-1.hortonworks.com/ambari/centos7/2.x/updates/2.7.0.0/ambari-2.7.0.0-centos7.tar.gz'

- wget -c 'http://public-repo-1.hortonworks.com/HDP/centos7/3.x/updates/3.0.0.0/HDP-3.0.0.0-centos7-rpm.tar.gz'
- wget -c 'http://public-repo-1.hortonworks.com/HDP-UTILS-1.1.0.22/repos/centos7/HDP-UTILS-1.1.0.22-centos7.tar.gz'
- wget -c 'http://public-repo-1.hortonworks.com/HDP-GPL/centos7/3.x/updates/3.0.0.0/HDP-GPL-3.0.0.0-centos7-gpl.tar.gz'

- [ ] ambari-2.7.3.0


- http://public-repo-1.hortonworks.com/ambari/centos7/2.x/updates/2.7.3.0/ambari-2.7.3.0-centos7.tar.gz


- http://public-repo-1.hortonworks.com/HDP/centos7/3.x/updates/3.1.0.0/HDP-3.1.0.0-centos7-rpm.tar.gz


- http://public-repo-1.hortonworks.com/HDP-UTILS-1.1.0.22/repos/centos7/HDP-UTILS-1.1.0.22-centos7.tar.gz


- http://public-repo-1.hortonworks.com/HDP-GPL/centos7/3.x/updates/3.1.0.0/HDP-GPL-3.1.0.0-centos7-gpl.tar.gz


- [ ] rinetd下载（如果需要网络转发的话）

- wget http://www.boutell.com/rinetd/http/rinetd.tar.gz



- [ ] UBUNTU:

wget -c 'http://public-repo-1.hortonworks.com/HDP/ubuntu18/3.x/updates/3.1.0.0/HDP-3.1.0.0-ubuntu18-deb.tar.gz'


wget -c 'http://public-repo-1.hortonworks.com/ambari/ubuntu18/2.x/updates/2.7.3.0/ambari-2.7.3.0-ubuntu18.tar.gz'


wget -c 'http://public-repo-1.hortonworks.com/HDP-UTILS-1.1.0.22/repos/ubuntu18/HDP-UTILS-1.1.0.22-ubuntu18.tar.gz'


wget -c 'http://public-repo-1.hortonworks.com/HDP-GPL/ubuntu18/3.x/updates/3.1.0.0/HDP-GPL-3.1.0.0-ubuntu18-gpl.tar.gz'

- [ ]

# 2.环境准备

**注意一定要上来先停掉防火墙，否则很容易出现莫名其妙的问题！！**

脚本所在目录：/var/www/html/scripts/third

软件所在目录：/var/www/html/soft

主机：192.168.254.40

端口： 8181

### 2.0检查CPU信息

```bash
ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/scripts/get-cpu-info.sh   dest=/home/zhangwusheng/scripts  owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  shell  -b -a "bash  /home/zhangwusheng/scripts/get-cpu-info.sh"
```



### 2.0首先增加必要的用户

```bash
groupadd cdnlog
useradd cdnlog -g cdnlog
useradd cdnlogop -g cdnlog

useradd kylin -g cdnlog
usermod -G hadoop kylin
echo 'cdnlogop   ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers

su - cdnlogop

ssh-keygen -t rsa
cd ~/.ssh
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDLli5xWfX86hIrUchgnl6hyrmDkpAw73LvcOicmyaASfSks+GYv+IORshuJhcrr635xR1FqLOwnXqgQy6R2D7JixZI9cTfwPhKN/bpKpQRfrDTqYN4rHgxIZ42gXMsEm9w/gBS9/8po9PYbIK37RmHr12xaYR5KUB7BMF8IvCOSG6SMs2u5HHydJVxl0JJUaNB5wTKx0/BSjOvTGDg9uD/PoCk6anRA0jWKqJUtYvX5Z+D/XomTDB2MNnE8Qkn0EXAGmVEzj/1KVmKn4ATdK6MDgHKsRIoYQSZK+S4n4kjUPpROFgWZuuvb3jNTVvrKR+Ee1sxs09PzEMugLjpin+53tz6e/F42SaXWsUNK0CPQboSSiOCht1n0YJHKRLKoZhFWkECQ+GxrrmVv4C3+xxiHB0rkgE84d8oU6ksFPeuIP1frB5MZoHma60QmsYt8J7qsXam/CgkYOgWB8DG9MaDWCpdyFNrUE/DR+YrEUHNZAMvSbTWqPX26ASupm4n9Yc= cdnlogop@sct-gz-guiyang1-loganalysis-01.in.ctcdn.cn' > ~/.ssh/authorized_keys
chmod 644  ~/.ssh/authorized_keys


userdel cdnlogop
rm -rf /home/cdnlogop/
sed -i '/cdnlogop/d'  /etc/sudoers

113.125.219.24
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" port port="9091" protocol="tcp" accept'

firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="113.125.219.24" port port="8181" protocol="tcp" accept'
firewall-cmd --reload
```



### 2.0首先设置免密登录！

- ssh设置


```bash
#mkdir /root/.ssh;chmod 600 /root/.ssh
#允许ROOT ssh
vi /etc/ssh/sshd_config

#PermitRootLogin no
PermitRootLogin yes

#然后重启sshd
systemctl restart sshd

#修改hosts.allow:
vi /etc/hosts.allow

#加入自己的IP
sshd:36.111.140.40:allow

ssh-keygen -t rsa
#不能ssh-copy-id的时候手工编辑这个文件，把pub文件拷贝过来
vi /root/.ssh/authorized_keys
#一定要修改权限
chmod 644 /root/.ssh/authorized_keys
```

- 设置host的查找顺序（确保）

  ```bash
  cat /etc/host.conf
  order hosts,bind
  multi on
  ```

### 2.1变量设置

```bash
vi /etc/ansible/hosts
#增加新的一批主机
[thirdnew]
192.168.254.118  ansible_ssh_user=root ansible_ssh_port=9000

export THISBATCH=thirdnew

ansible ${THISBATCH} -m shell -a 'mkdir -p /home/zhangwusheng/soft'
ansible ${THISBATCH} -m shell -a 'mkdir -p /home/zhangwusheng/scripts/third'
```

### 2.2关闭防火墙

```
#每台机器执行
systemctl disable firewalld
systemctl stop firewalld
```

### 2.3挂载磁盘

```bash
#格式化磁盘
#最开始文件系统是ext4，后面调整成了xfs,
#盘名字要自己根据机器的实际情况修改，有的是sda已经分区，有的是sdm已经分区，每一批机器的命令不一样
ansible ${THISBATCH} -m shell -a 'mkfs.xfs /dev/sdb'
ansible ${THISBATCH} -m shell -a 'mkfs.xfs /dev/sdc'
ansible ${THISBATCH} -m shell -a 'mkfs.xfs /dev/sdd'
ansible ${THISBATCH} -m shell -a 'mkfs.xfs /dev/sde'
ansible ${THISBATCH} -m shell -a 'mkfs.xfs /dev/sdf'
ansible ${THISBATCH} -m shell -a 'mkfs.xfs /dev/sdg'
ansible ${THISBATCH} -m shell -a 'mkfs.xfs /dev/sdh'
ansible ${THISBATCH} -m shell -a 'mkfs.xfs /dev/sdi'
ansible ${THISBATCH} -m shell -a 'mkfs.xfs /dev/sdj'

#建立目录
ansible ${THISBATCH} -m shell -a 'mkdir /data1 /data2 /data3 /data4 /data5 /data6 /data7 /data8 /data9 /data10 /ssd1 /ssd2'
;
#挂盘
#ssd，注意一定要检查脚本，把那个数字改一下，有的是960，有的是959
ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/scripts/third/ssd.sh -O /home/zhangwusheng/scripts/third/ssd.sh'
ansible ${THISBATCH} -m shell -a 'bash /home/zhangwusheng/scripts/third/ssd.sh'
#sata，注意一定要检查脚本，把那个数字改一下，有的是6001，有的是6000.9
ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/scripts/third/sata.sh -O /home/zhangwusheng/scripts/third/sata.sh'
ansible ${THISBATCH} -m shell -a 'bash /home/zhangwusheng/scripts/third/sata.sh'
#检查挂载是否成功
ansible ${THISBATCH} -m shell -a 'df -h'

#挂载fstab
ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/scripts/third/fstab.py -O /home/zhangwusheng/scripts/third/fstab.py'
ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/scripts/third/fstab.sh -O /home/zhangwusheng/scripts/third/fstab.sh'
#检查fstab
ansible ${THISBATCH} -m shell -a 'bash /home/zhangwusheng/scripts/third/fstab.sh'
ansible  ${THISBATCH}  -m shell -a 'python /home/zhangwusheng/scripts/third/fstab.py --action=check'
```

### 2.4安装JDK

```bash
export THISBATCH=thirdnew
#安装java
ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/soft/jdk-8u211-linux-x64.tar.gz -O /home/zhangwusheng/soft/jdk-8u211-linux-x64.tar.gz'

ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/soft/jce_policy-8.zip -O /home/zhangwusheng/soft/jce_policy-8.zip'

#===================java-env.sh
tar zxf /home/zhangwusheng/soft/jdk-8u211-linux-x64.tar.gz -C /usr/local/

rm -f /usr/local/jdk
ln -fs /usr/local/jdk1.8.0_211 /usr/local/jdk

unzip -o -j -q /home/zhangwusheng/soft/jce_policy-8.zip -d /usr/local/jdk/jre/lib/security/

echo 'export SPARK_HOME=/usr/hdp/3.1.0.0-78/spark2' > /etc/profile.d/spark.sh
echo 'export PATH=$PATH:$SPARK_HOME/bin' >> /etc/profile.d/spark.sh
echo 'export JAVA_HOME=/usr/local/jdk' > /etc/profile.d/java.sh
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile.d/java.sh
#====================================


#安装jdk
ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/scripts/third/java-env.sh -O /home/zhangwusheng/scripts/third/java-env.sh'
ansible ${THISBATCH} -m shell -a 'bash /home/zhangwusheng/scripts/third/java-env.sh'

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "mkdir -p /home/zhangwusheng/soft"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/jdk-8u211-linux-x64.tar.gz   dest=/home/zhangwusheng/soft  owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/jce_policy-8.zip   dest=/home/zhangwusheng/soft  owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/scripts/java-env.sh   dest=/home/zhangwusheng/scripts  owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  file  -b -a "path=/home/zhangwusheng/scripts state=directory owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "bash /home/zhangwusheng/scripts/java-env.sh"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "java -version"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "unzip -o -j -q /home/zhangwusheng/soft/jce_policy-8.zip -d /usr/local/jdk/jre/lib/security/"


显示java参数

java -XX:+UnlockDiagnosticVMOptions -XX:+PrintFlagsFinal -version|grep -i meta


jmap -F -dump:format=b,file=kylin.bin 221663

```

### 内蒙kafka优化步骤

```bash

1.运行 iostat -x 1 10 找出哪块盘利用率很高 查看 %util 字段


2. 运行 iotop -oP 找出io占用高的进程
        iotop -botq -p 8382 查看指定进程的io信息
		
3.运行  pidstat -d 1 查看进程的io相关信息



第一步：调整系统参数

对 182.42.78.61、182.42.78.99进行调整 
sysctl -a|grep dirty

vm.dirty_background_ratio 是内存可以填充脏数据的百分比。这些脏数据稍后会写入磁盘，pdflush/flush/kdmflush这些后台进程会稍后清理脏数据。比如，我有32G内存，那么有3.2G的脏数据可以待着内存里，超过3.2G的话就会有后台进程来清理。
vm.dirty_ratio是可以用脏数据填充的绝对最大系统内存量，当系统到达此点时，必须将所有脏数据提交到磁盘，同时所有新的I/O块都会被阻塞，直到脏数据被写入磁盘。这通常是长I/O卡顿的原因，但这也是保证内存中不会存在过量脏数据的保护机制。
https://blog.csdn.net/weixin_44410537/article/details/98449706

/proc/vmstat, /proc/meminfo, iostat, vmstat 以及/proc/sys/vm

150网段为：
vm.dirty_background_bytes = 0
vm.dirty_background_ratio = 5
vm.dirty_bytes = 0
vm.dirty_expire_centisecs = 3000
vm.dirty_ratio = 70
vm.dirty_writeback_centisecs = 500

182网段为：
vm.dirty_background_bytes = 0
vm.dirty_background_ratio = 10  ----->   5
vm.dirty_bytes = 0
vm.dirty_expire_centisecs = 3000
vm.dirty_ratio = 20             -----> 70
vm.dirty_writeback_centisecs = 500


cat /sys/kernel/mm/transparent_hugepage/enabled

echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag

vm.dirty_ratio = 5
vm.dirty_background_ratio = 70 
做成服务：
vim /etc/rc.d/rc.local
增加下列内容：

if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
echo never > /sys/kernel/mm/transparent_hugepage/enabled
fi
if test -f /sys/kernel/mm/transparent_hugepage/defrag; then
echo never > /sys/kernel/mm/transparent_hugepage/defrag
fi


第二步：
删除topic

2.1 首先检查数据

#du -sh /data*/kafka-logs/tencent_ctYun-[0-9]*

du -sh /data*/kafka-logs/CdnPerfTest-[0-9]*
du -sh /data*/kafka-logs/CdnPerfTest-LZ4-[0-9]*
du -sh /data*/kafka-logs/CdnPerfTest2-[0-9]*
du -sh /data*/kafka-logs/ctYun_test-[0-9]*
du -sh /data*/kafka-logs/haohanRedo-[0-9]*
du -sh /data*/kafka-logs/cdn-log-analysis-realtime-pref-[0-9]*
du -sh /data*/kafka-logs/revert_ctYun_0608-[0-9]*
du -sh /data*/kafka-logs/revert_ctYun_20210608-[0-9]*
du -sh /data*/kafka-logs/ctYun_20210311-[0-9]*
du -sh /data*/kafka-logs/cdn-log-analysis-realtime-Ali-[0-9]*
du -sh /data*/kafka-logs/cdn-log-analysis-realtime-baidu-[0-9]*
du -sh /data*/kafka-logs/cdn-log-analysis-realtime-yunfan-[0-9]*
du -sh /data*/kafka-logs/cdn-log-analysis-realtime-jingdong-[0-9]*
du -sh /data*/kafka-logs/cdn-log-analysis-realtime-tencent-[0-9]*
du -sh /data*/kafka-logs/cdn-log-analysis-realtime-[0-9]*

#
150.223.254.23上进行zk的操作


usr/hdp/current/zookeeper-client/bin/zkCli.sh -server cdnlog040.ctyun.net:12181/cdnlog-first

ls /brokers/topics/CdnPerfTest
ls /brokers/topics/CdnPerfTest-LZ4
ls /brokers/topics/CdnPerfTest2
ls /brokers/topics/ctYun_test
ls /brokers/topics/haohanRedo
ls /brokers/topics/cdn-log-analysis-realtime-pref
ls /brokers/topics/revert_ctYun_0608
ls /brokers/topics/revert_ctYun_20210608
ls /brokers/topics/ctYun_20210311
ls /brokers/topics/cdn-log-analysis-realtime-Ali
ls /brokers/topics/cdn-log-analysis-realtime-baidu
ls /brokers/topics/cdn-log-analysis-realtime-yunfan
ls /brokers/topics/cdn-log-analysis-realtime-jingdong
ls /brokers/topics/cdn-log-analysis-realtime-tencent
ls /brokers/topics/cdn-log-analysis-realtime



删除前一共topic数：
Showing 1 to 161 of 161 entries

本次共删除15个topic，应该剩余146个topic


rmr /brokers/topics/CdnPerfTest
rmr /brokers/topics/CdnPerfTest-LZ4
rmr /brokers/topics/CdnPerfTest2
rmr /brokers/topics/ctYun_test
rmr /brokers/topics/haohanRedo
rmr /brokers/topics/cdn-log-analysis-realtime-pref
rmr /brokers/topics/revert_ctYun_0608
rmr /brokers/topics/revert_ctYun_20210608
rmr /brokers/topics/ctYun_20210311
rmr /brokers/topics/cdn-log-analysis-realtime-Ali
rmr /brokers/topics/cdn-log-analysis-realtime-baidu
rmr /brokers/topics/cdn-log-analysis-realtime-yunfan
rmr /brokers/topics/cdn-log-analysis-realtime-jingdong
rmr /brokers/topics/cdn-log-analysis-realtime-tencent
rmr /brokers/topics/cdn-log-analysis-realtime



rm -rf /data*/kafka-logs/CdnPerfTest-[0-9]*
rm -rf /data*/kafka-logs/CdnPerfTest-LZ4-[0-9]*
rm -rf /data*/kafka-logs/CdnPerfTest2-[0-9]*
rm -rf /data*/kafka-logs/ctYun_test-[0-9]*
rm -rf /data*/kafka-logs/haohanRedo-[0-9]*
rm -rf /data*/kafka-logs/cdn-log-analysis-realtime-pref-[0-9]*
rm -rf /data*/kafka-logs/revert_ctYun_0608-[0-9]*
rm -rf /data*/kafka-logs/revert_ctYun_20210608-[0-9]*
rm -rf /data*/kafka-logs/ctYun_20210311-[0-9]*
rm -rf /data*/kafka-logs/cdn-log-analysis-realtime-Ali-[0-9]*
rm -rf /data*/kafka-logs/cdn-log-analysis-realtime-baidu-[0-9]*
rm -rf /data*/kafka-logs/cdn-log-analysis-realtime-yunfan-[0-9]*
rm -rf /data*/kafka-logs/cdn-log-analysis-realtime-jingdong-[0-9]*
rm -rf /data*/kafka-logs/cdn-log-analysis-realtime-tencent-[0-9]*
rm -rf /data*/kafka-logs/cdn-log-analysis-realtime-[0-9]*


ls -al /data*/kafka-logs/CdnPerfTest-[0-9]*
ls -al /data*/kafka-logs/CdnPerfTest-[0-9]*
ls -al /data*/kafka-logs/CdnPerfTest-LZ4-[0-9]*
ls -al /data*/kafka-logs/CdnPerfTest2-[0-9]*
ls -al /data*/kafka-logs/ctYun_test-[0-9]*
ls -al /data*/kafka-logs/haohanRedo-[0-9]*
ls -al /data*/kafka-logs/cdn-log-analysis-realtime-pref-[0-9]*
ls -al /data*/kafka-logs/revert_ctYun_0608-[0-9]*
ls -al /data*/kafka-logs/revert_ctYun_20210608-[0-9]*
ls -al /data*/kafka-logs/ctYun_20210311-[0-9]*
ls -al /data*/kafka-logs/cdn-log-analysis-realtime-Ali-[0-9]*
ls -al /data*/kafka-logs/cdn-log-analysis-realtime-baidu-[0-9]*
ls -al /data*/kafka-logs/cdn-log-analysis-realtime-yunfan-[0-9]*
ls -al /data*/kafka-logs/cdn-log-analysis-realtime-jingdong-[0-9]*
ls -al /data*/kafka-logs/cdn-log-analysis-realtime-tencent-[0-9]*
ls -al /data*/kafka-logs/cdn-log-analysis-realtime-[0-9]*


03已重启
04已重启
13,14，23，24已重启


CPU SOFt STUCK
调整机器参数

sysctl -a |grep kernel.watchdog_thresh
sudo sysctl -w kernel.watchdog_thresh=30


#检查磁盘分布情况

cd cd /home/zhangwusheng/usr/bin/kafka-io
TOPIC=ctYun
du -sh /data*/kafka-logs/ctYun-*|sort -k2,2 > $TOPIC.$HOSTNAME

ansible -i /home/zhangwusheng/etc/ansible/neimeng.hosts kafka -m shell  -a "mkdir -p /home/zhangwusheng/usr/bin/kafka-io"
ansible -i /home/zhangwusheng/etc/ansible/neimeng.hosts kafka  -m copy -b -a "src=/home/zhangwusheng/usr/bin/kafka-io/get_topic_disk_dist.sh  dest=/home/zhangwusheng/usr/bin/kafka-io "

ansible -i /home/zhangwusheng/etc/ansible/neimeng.hosts kafka -m shell  -a "bash /home/zhangwusheng/usr/bin/kafka-io/get_topic_disk_dist.sh migu_haohanYun" --forks=1
```

TOPIC=zws_dir_test
 du -sh /data*/kafka-logs/${TOPIC}-[0-9]*|sort -k2,2|awk '{print $2;}'|awk -F'/' '{print $2;}'|sort|uniq -c|awk 'BEGIN{for(i=1;i<=10;i++){a["data"i]=0;}}{a[$2]=$1;}END{for(i=1;i<=10;i++){print a["data"i];}}'

1. 增加jmx采集，做曲线（指标待讨论，暂定
2. 监控每台机器平均时间之内IO达到40%以上告警，直接重启机器（预案）
3. 准备磁盘相关的命令（需群策群力，看看哪些命令有效），
   3.1. 运行 iostat -x 1 10 找出哪块盘利用率很高 查看 %util 字段
   3.2. 运行 iotop -oP 找出io占用高的进程
      iotop -botq -p 8382 查看指定进程的io信息
   3.3. 运行  pidstat -d 1 查看进程的io相关信息
4. 调整kafka分区磁盘分布（目前不知道怎么调整目录，需要研究） 
5. 重启kafka集群，删除部分topic（已做）  
6. 现有baiduYun扩分区或者合入ctYun，防止个别分区变慢，再读冷数据。（后者多一次读写）
   7.对 182.42.78.61、182.42.78.99进行调整 dirty参数,(已调整，观察效果，其他182网段机器未做）
    7.1 cat /sys/kernel/mm/transparent_hugepage/enabled
      echo never > /sys/kernel/mm/transparent_hugepage/enabled
      echo never > /sys/kernel/mm/transparent_hugepage/defrag
    7.2 vm.dirty_ratio = 5
      vm.dirty_background_ratio = 70 

重点：
找出哪些进程IO高，以及高的原因

在机器 sct-nmg-huhehaote3-loganalysis-75.in.ctcdn.cn 部署arthas监控脚本。


#预生产环境验证kafka目录迁移

KAFKA_ZK=dev-nmg-huhehaote2-loganalysis-06.in.ctcdn.cn:12181,dev-nmg-huhehaote2-loganalysis-03.in.ctcdn.cn:12181,dev-nmg-huhehaote2-loganalysis-09.in.ctcdn.cn:12181/cdnlog-first
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper  ${KAFKA_ZK}



/usr/hdp/current/kafka-broker/bin/kafka-reassign-partitions.sh  --zookeeper ${KAFKA_ZK} --topics-to-move-json-file ./topics-to-move.json --broker-list 1001,1002,1003,1004,1005,1006,1007,1008 --generate


#创建Topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${KAFKA_ZK}  --topic zws_dir_test    --partitions 50 --replication-factor 3

#查看创建的Topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --describe --zookeeper ${KAFKA_ZK}   --topic zws_dir_test

#Topic授权，注意这里最好使用--producer，不要使用--operation Write
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --add --allow-principal User:producer --topic zwstestnew2  --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --list  --topic zwstestnew2

#修改好kafka_client_jaas_conf ，注意使用 --security-protocol，而不是网上的producer-property，那样不行
/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667  --topic zwstestnew2 --security-protocol=SASL_PLAINTEXT --producer-property sasl.mechanism=PLAIN

#修改好consumer的kafka_client_jaas_conf，然后修改好consumer.properties
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667  --topic zwstestnew2 --security-protocol=SASL_PLAINTEXT --from-beginning --consumer.config ./consumer.properties --new-consumer

#想要读取，必须经过授权！
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1  --add --allow-principal User:consumer --topic zwstestnew2  --consumer --group zws-test-grp1


#/bin/bash

#profile_one_minute_spark.sh

app_count=`ps -ef|grep profile_one_minute_spark|grep  -v grep |wc -l 2>/dev/null`
echo $app_count
if [ $app_count -gt 2 ]
then
	echo "total $app_count instance of profile_one_minute_spark running"
	exit 0
fi

cd /home/cdnlog
mkdir -p /home/cdnlog/spark-56005
java -jar ./arthas-boot.jar -c'profiler start;stop' 56005 
sleep 4m
java -jar arthas-boot.jar -c'profiler stop;stop' 56005 > /home/cdnlog/56005.log
filename=`grep  'profiler output file' /home/cdnlog/56005.log|awk -F':' '{print $2;}'`
cp ${filename} /home/cdnlog/spark-56005


ansible -i /home/zhangwusheng/etc/ansible/neimeng.hosts kafka  -m copy -b -a "src=/home/zhangwusheng/usr/bin/profile_one_minute_spark.sh dest=/home/zhangwusheng/usr/bin "

主机：
sct-nmg-huhehaote3-loganalysis-73.in.ctcdn.cn 定时生成svg


### 2.5设置ulimit

```bash


export THISBATCH=thirdnew
ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/scripts/third/ulimit.sh -O /home/zhangwusheng/scripts/third/ulimit.sh'
ansible ${THISBATCH} -m shell -a 'bash /home/zhangwusheng/scripts/third/ulimit.sh'
ansible ${THISBATCH} -m shell -a ' cat /etc/security/limits.conf'
################
#有的时候root不能su 其他用户，需要修改这里
vi /etc/security/limits.d/20-nproc.conf
#*          soft    nproc     4096
*          soft    nproc     65536
root       soft    nproc     unlimited
默认的4096不行

#for es
ansible ${THISBATCH} -m shell -a 'sysctl -w vm.max_map_count=262144;sysctl -p'
ansible ${THISBATCH} -m shell -a 'sysctl -p'


#==================ulimit.sh
cat /etc/security/limits.conf|grep -v nofile|grep -v nproc|grep -v 'soft core' > ${TEMPFILE}
echo '* soft nofile 65536' >> ${TEMPFILE}
echo '* hard nofile 65536' >> ${TEMPFILE}
echo '* soft nproc 131072' >> ${TEMPFILE}
echo '* hard nproc 131072' >> ${TEMPFILE}
echo '* soft core unlimited' >> ${TEMPFILE}

mv /etc/security/limits.conf /etc/security/limits.conf.`date +%s`
mv -f ${TEMPFILE} /etc/security/limits.conf
#======================
ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/scripts/ulimit.sh   dest=/home/zhangwusheng/scripts  owner=zhangwusheng group=zhangwusheng"



#查看bond状态
ifconfig #ifconfig命令可以查看设备的bond信息，bond口和两个成员口MAC地址相同，成员口的地址失效，两块网卡共用bond0设备的一个IP地址
cat /proc/net/bonding/bond0.
cat /sys/class/net/bond0/bonding/mode.

```
### 2.6设置通用环境变量

```bash
#设置swappiness
#设置语言
#禁止ipv6
#设置core文件位置
export THISBATCH=thirdnew
ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/scripts/third/misc-env.sh -O /home/zhangwusheng/scripts/third/misc-env.sh'

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/scripts/misc-env.sh   dest=/home/zhangwusheng/scripts  owner=zhangwusheng group=zhangwusheng"

ansible ${THISBATCH} -m shell -a 'bash /home/zhangwusheng/scripts/third/misc-env.sh'

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  shell  -b -a "bash /home/zhangwusheng/scripts/misc-env.sh"

#+=============================
#lang
echo 'LANG=en_US.UTF-8' > /etc/locale.conf

#swappiness
echo '1' > /proc/sys/vm/swappiness
#sed -i 's/vm.swappiness=10/vm.swappiness=1/g' /etc/sysctl.conf
sed -i '/vm.swappiness/d' /etc/sysctl.conf
echo 'vm.swappiness=1' >> /etc/sysctl.conf


#core file
mkdir -p /data2/core_files
echo '/data2/core_files/core-%e-%p-%t' > /proc/sys/kernel/core_pattern

#disable ipv6
echo 1> /proc/sys/net/ipv6/conf/all/disable_ipv6
echo 1> /proc/sys/net/ipv6/conf/default/disable_ipv6

sed -i '/disable_ipv6/d' /etc/sysctl.conf
echo 'net.ipv6.conf.all.disable_ipv6=1' >> /etc/sysctl.conf
#cat /etc/sysctl.conf
sysctl  -p
#=============================================

查询网络丢包
mtr -n --report 182.42.78.61

```

>  *core_pattern的参数说明*
>
> ​         *%p - inse*rt pid into filename 添加pid*
> ​          %u - insert current uid into filename 添加当前uid*
> ​          *%g - insert current gid into filename 添加当前gid*
> ​          *%s - insert signal that caused the coredump into the filename 添加导致产生core的信号*
> ​          *%t - insert UNIX time that the coredump occurred into filename 添加core文件生成的unix时间*
> ​          *%h - insert hostname where the coredump happened into filename 添加主机名*
> ​          %e - insert coredumping executable name into filename 添加命令名*

### 2.7修改hostname

```bash
#这个每个批次机器都设置好了，要改的也不一样，这个脚本并不是通用的，每次要根据实际情况修改
export THISBATCH=thirdnew
ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/scripts/third/hostname-1.sh -O /home/zhangwusheng/scripts/third/hostname-1.sh'
ansible ${THISBATCH} -m shell -a 'bash /home/zhangwusheng/scripts/third/hostname-1.sh'
```



### 2.8设置hosts

```bash
export THISBATCH=XX
#获取所有的hostname
ansible ${THISBATCH} -m shell -a 'hostname'
#发布,HOSTS文件需要全网发布
ansible cdnlog -m shell -a 'mkdir -p /home/zhangwusheng/scripts/third'
#下发host文件
ansible cdnlog -m shell -a 'wget http://192.168.254.40:8181/scripts/third/hosts -O /home/zhangwusheng/scripts/third/hosts'
#下发host脚本
ansible cdnlog -m shell -a 'wget http://192.168.254.40:8181/scripts/third/hosts.sh -O /home/zhangwusheng/scripts/third/hosts.sh'
#执行host脚本
ansible cdnlog -m shell -a 'bash /home/zhangwusheng/scripts/third/hosts.sh'
#检查hosts文件
ansible cdnlog -m shell -a 'cat /etc/hosts'


function generate_hosts_wlan_guizhou()
{
	local wlan=` ip addr|grep 113.125|awk '{print $2;}'|awk -F'/' '{print $1;}'`
	echo "$wlan     $HOSTNAME"
}

function generate_hosts_wlan_guizhou()
{
	local wlan=` ip addr|grep 192.168|awk '{print $2;}'|awk -F'/' '{print $1;}'`
	echo "$wlan     $HOSTNAME"
}

function generate_hosts_wlan_neimeng()
{
	local wlan=`ip addr|grep -e'150.223' -e'182.42.'|awk '{print $2;}'|awk -F'/' '{print $1;}'`
	echo "$wlan     $HOSTNAME"
}

generate_hosts_wlan_neimeng

#内蒙
ansible cdnlog -m  copy  -b -a "src=/var/www/html/scripts/third/generate-hosts.sh   dest=/home/zhangwusheng/scripts/third  owner=root group=root"
ansible cdnlog -m  shell  -b -a "bash /home/zhangwusheng/scripts/third/generate-hosts.sh"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/scripts/generate-hosts.sh   dest=/home/zhangwusheng/scripts  owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  shell  -b -a "bash /home/zhangwusheng/scripts/generate-hosts.sh"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/scripts/hosts   dest=/home/zhangwusheng/scripts  owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  shell  -b -a "cp /etc"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m copy -b -a "src=/home/zhangwusheng/scripts/hosts  dest=/etc/ backup=yes"
```



-   ntp服务

```bash
#跳板机做ntpserver
yum -y install ntp

#如果能连接外网首先同步跳板机的时间
ntpdate 0.centos.pool.ntp.org

#其实这里不改也行
vi /etc/ntp.conf
restrict 192.168.0.193 mask 255.255.255.0
restrict 192.168.0.110 mask 255.255.255.0
restrict 192.168.0.201 mask 255.255.255.0
#不能连接外网时使用本机墙上时钟
server  127.127.1.0     # local clock
fudge   127.127.1.0 stratum 2

systemctl start ntpd.service
systemctl enable ntpd.service

#36.111.140.40的配置：
restrict default kod nomodify notrap nopeer noquery
restrict -6 default kod nomodify notrap nopeer noquery
restrict 127.0.0.1
restrict -6 ::1
server 36.111.136.110
server  127.127.1.0     # local clock
driftfile /var/lib/ntp/drift
keys /etc/ntp/keys
```

可以不设置。

```bash
#在其他三台节点上执行，以跳板机的为准
crontab -e
0-59/10 * * * * /usr/sbin/ntpdate t3m1 #这里的主机自己随便选，可以选择ambariserver所在的主机
```

上面这一步为必须设置的步骤。

-    临时关闭selinux

```bash
#临时关闭：
[root@localhost ~]# getenforce
Enforcing
[root@localhost ~]# setenforce 0
[root@localhost ~]# getenforce
Permissive

#永久关闭：
[root@localhost ~]# vim /etc/sysconfig/selinux
SELINUX=enforcing 改为 SELINUX=disabled

```

### 2.9增加用户


```bash
export THISBATCH=thirdnew
#下发host脚本
ansible ${THISBATCH} -m shell -a 'wget http://192.168.254.40:8181/scripts/third/useradd.sh -O /home/zhangwusheng/scripts/third/useradd.sh'
#执行host脚本
ansible ${THISBATCH} -m shell -a 'bash /home/zhangwusheng/scripts/third/useradd.sh'

#安装集群完毕后再安装！
需要把kylin -G到hadoop组


#分开执行

/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey tsdb/${HOSTNAME}@CTYUN.NET"

/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "xst -k /etc/security/keytabs/tsdb.keytab tsdb/${HOSTNAME}@CTYUN.NET"

klist -k /etc/security/keytabs/tsdb.keytab

######
chmod a+r /etc/security/keytabs/tsdb.keytab
```

### 2.10 开通防火墙

```bash
export THISBATCH=tsdb
ansible cdnlog -m shell -a 'wget http://192.168.254.40:8181/scripts/third/firewall-cluster-visit-tsdb.sh -O /home/zhangwusheng/scripts/third/firewall-cluster-visit-tsdb.sh'

ansible cdnlog -m shell -a 'bash /home/zhangwusheng/scripts/third/firewall-cluster-visit-tsdb.sh'


ansible tsdb -m shell -a 'wget http://192.168.254.40:8181/scripts/third/firewall-tsdb-visit-cluster.sh -O /home/zhangwusheng/scripts/third/firewall-tsdb-visit-cluster.sh'
ansible tsdb -m shell -a 'bash /home/zhangwusheng/scripts/third/firewall-tsdb-visit-cluster.sh'
ansible tsdb -m shell -a 'firewall-cmd --list-all'



firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="125.88.39.167" port port="6667" protocol="tcp" accept'
firewall-cmd --reload

firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" port port="9091" protocol="tcp" accept'

firewall-cmd --permanent --remove-rich-rule 'rule family="ipv4" port port="9091" protocol="tcp" accept'


firewall-cmd --reload
firewall-cmd --list-all


```

### 2.11 验证端口连通性

```bash
nc -zw 2  {{ item }} 5044


for ip in `cat /home/zhangwusheng/etc/ansible/vivo.kafka.local`
do
   nc -zw 2 ${ip} 5044
   if [ $? -ne 0 ]
   then
      echo ${ip} 5044 failed
   else
      echo ${ip} 5044 success
   fi

done

```







# 3.配置YUM离线源

***Amber-Server服务器执行，自己选择一台机器作为AmbariServer***

- 安装httpd并且修改端口

```bash
sudo firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=36.111.140.26 accept'
sudo firewall-cmd --permanent --remove-rich-rule 'rule family=ipv4 source address=36.111.140.26 accept'


#安装httpd
yum -y install httpd
#修改默认端口
sed -i 's/Listen 80/Listen 18181/g' /etc/httpd/conf/httpd.conf
#启动服务
systemctl restart httpd
#检查启动情况：
netstat -anp|grep 18181
```

-   解压安装软件

```bash
mkdir -p /var/www/html/ambari
cd  ${HDP_SOFT}

tar zxvf ambari-2.7.0.0-centos7.tar.gz -C /var/www/html/ambari
tar zxvf HDP-3.0.0.0-centos7-rpm.tar.gz  -C /var/www/html/ambari
tar zxvf HDP-UTILS-1.1.0.22-centos7.tar.gz -C  /var/www/html/ambari
tar zxvf HDP-GPL-3.0.0.0-centos7-gpl.tar.gz -C /var/www/html/ambari


tar zxvf ambari-2.7.3.0-centos7.tar.gz -C /var/www/html/ambari
tar zxvf HDP-3.1.0.0-centos7-rpm.tar.gz  -C /var/www/html/ambari
tar zxvf HDP-UTILS-1.1.0.22-centos7.tar.gz -C  /var/www/html/ambari
tar zxvf HDP-GPL-3.1.0.0-centos7-gpl.tar.gz -C /var/www/html/ambari

sudo tar zxvf ambari-2.7.3.0-ubuntu18.tar.gz -C /var/www/html/ambari
sudo  tar zxvf HDP-3.1.0.0-ubuntu18-deb.tar.gz -C /var/www/html/ambari
sudo  tar zxvf HDP-UTILS-1.1.0.22-ubuntu18.tar.gz -C /var/www/html/ambari
sudo  tar zxvf HDP-GPL-3.1.0.0-ubuntu18-gpl.tar.gz -C /var/www/html/ambari
```

- 配置离线源

```bash
#baseurl改成自己的ambariserver在的机器
cat > /etc/yum.repos.d/ambari.repo<<EOF
[ambari-2.7.0.0]
name=HDP Version - ambari-2.7.0.0
baseurl=http://192.168.0.47/ambari/ambari/centos7/2.7.0.0-897/
gpgcheck=0
EOF


cat > /etc/yum.repos.d/ambari.repo<<EOF
[ambari-2.7.3.0]
name=HDP Version - ambari-2.7.3.0
baseurl=http://172.31.0.14:18181/ambari/ambari/centos7/2.7.3.0-139/
gpgcheck=0
EOF

#检查是否正确
yum repolist
#yum clean all
#yum makecache

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/scripts/generate-ambari-repo.sh   dest=/home/zhangwusheng/scripts  owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  file  -b -a "path=/home/zhangwusheng/scripts state=directory owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "bash /home/zhangwusheng/scripts/generate-ambari-repo.sh"


#出问题的话可以这样子：
rm -rf /var/lib/rpm/__db*
```
- 安装AmbariServer

```bash
yum install -y ambari-server
#修改ambari端口
echo 'client.api.port=18080' >> /etc/ambari-server/conf/ambari.properties
#或者
grep -v 'client.api.port' /etc/ambari-server/conf/ambari.properties > /etc/ambari-server/conf/ambari.properties2
echo 'client.api.port=18080' >> /etc/ambari-server/conf/ambari.properties2
mv -f /etc/ambari-server/conf/ambari.properties2 /etc/ambari-server/conf/ambari.properties


sudo firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=192.168.189.0/25 accept'
```



安装ambari-agent

```bash
ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  file  -b -a "path=/home/zhangwusheng/scripts state=directory owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "yum -y install ambari-agent"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "java -version"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/scripts/install-ambari-agent.sh   dest=/home/zhangwusheng/scripts  owner=zhangwusheng group=zhangwusheng"

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "sed -i 's/hostname=localhost/hostname=sct-gz-guiyang1-loganalysis-17.in.ctcdn.cn/g' /etc/ambari-agent/conf/ambari-agent.ini "

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "ambari-agent start "

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "ambari-agent status"

#解决多版本保护问题
ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a " yum -y install gcc --setopt=protected_multilib=false"
```



- Ubuntu

```bash
cd /etc/apt/sources.list.d

deb   http://127.0.0.1:8181/ambari/ambari/ubuntu18/2.7.3.0-139/ Ambari main
deb   http://127.0.0.1:8181/ambari/HDP/ubuntu18/3.1.0.0-78/ HDP main
deb   http://127.0.0.1:8181/ambari/HDP-GPL/ubuntu18/3.1.0.0-78/ HDP-GPL main
deb   http://127.0.0.1:8181/ambari/HDP-UTILS/ubuntu18/1.1.0.22/ HDP-UTILS main


sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv B9733A7A07513CAD
apt-cache showpkg ambari-server
apt-cache showpkg ambari-agent
apt-cache showpkg ambari-metrics-assembly

#daquan
https://blog.csdn.net/mwz1tn/article/details/87446216

```



# 4.安装mysql（跳过）

```bash
5.6版本：

my.cnf
basedir =/usr/local/mysql
datadir =/usr/local/mysql/data
log-err = /usr/local/mysql/data/error.log

/usr/local/mysql/scripts/mysql_install_db --verbose --user=root --defaults-file=/usr/local/mysql/my.cnf --datadir=/usr/local/mysql/data --basedir=/usr/local/mysql --pid-file=/usr/local/mysql/data/mysql.pid --tmpdir=/tmp


/usr/local/mysql/bin/mysqld_safe --defaults-file=/usr/local/mysql/my.cnf --socket=/tmp/mysql.sock --user=root &

use mysql;
update user set password=password("root") where user="CdnLogRoot!$&";
FLUSH PRIVILEGES;

```



```
yum install -y mariadb-server
yum install -y mariadb
systemctl start mariadb 
systemctl enable mariadb //设置开机自启

mysql_secure_installation
/**root:root!@#$%^*/

# vim /etc/my.cnf
在[mysqld]标签下添加如下内容：
default-storage-engine = innodb
innodb_file_per_table
max_connections = 4096
collation-server = utf8_general_ci
character-set-server = utf8

# vim /etc/my.cnf.d/client.cnf
在[client]标签下添加如下内容：
default-character-set=utf8


systemctl restart mariadb


mysql -uroot -p
root!@#$%^
执行musql语句：

CREATE DATABASE ambari;
use ambari;
drop user  'ambari';
CREATE USER 'ambari'@'%' IDENTIFIED BY 'bigdata';
GRANT ALL PRIVILEGES ON *.* TO 'ambari'@'%';
FLUSH PRIVILEGES;

CREATE USER 'ambari'@'localhost' IDENTIFIED BY 'ambari';
GRANT ALL PRIVILEGES ON *.* TO 'ambari'@'localhost';

CREATE USER 'ambari'@'t3m1' IDENTIFIED BY 'ambari';
GRANT ALL PRIVILEGES ON *.* TO 'ambari'@'t3m1';
FLUSH PRIVILEGES;

source /var/lib/ambari-server/resources/Ambari-DDL-MySQL-CREATE.sql
show tables;
use mysql;
select Host,User,Password from user where user='ambari';

CREATE DATABASE hive;
use hive;
CREATE USER 'hive'@'%' IDENTIFIED BY 'hive';
GRANT ALL PRIVILEGES ON *.* TO 'hive'@'%';
CREATE USER 'hive'@'localhost' IDENTIFIED BY 'hive';
GRANT ALL PRIVILEGES ON *.* TO 'hive'@'localhost';
CREATE USER 'hive'@'t3m1' IDENTIFIED BY 'hive';
GRANT ALL PRIVILEGES ON *.* TO 'hive'@'t3m1';
FLUSH PRIVILEGES;


CREATE DATABASE oozie;
use oozie;
CREATE USER 'oozie'@'%' IDENTIFIED BY 'oozie';
GRANT ALL PRIVILEGES ON *.* TO 'oozie'@'%';
CREATE USER 'oozie'@'localhost' IDENTIFIED BY 'oozie';
GRANT ALL PRIVILEGES ON *.* TO 'oozie'@'localhost';
CREATE USER 'oozie'@'t3m1' IDENTIFIED BY 'oozie';
GRANT ALL PRIVILEGES ON *.* TO 'oozie'@'t3m1';
FLUSH PRIVILEGES;


CREATE DATABASE ranger;
use ranger;
CREATE USER 'rangeradmin'@'%' IDENTIFIED BY 'rangeradmin';
GRANT ALL PRIVILEGES ON *.* TO 'rangeradmin'@'%' WITH GRANT OPTION;
CREATE USER 'rangeradmin'@'localhost' IDENTIFIED BY 'rangeradmin' ;
GRANT ALL PRIVILEGES ON *.* TO 'rangeradmin'@'localhost' WITH GRANT OPTION;
CREATE USER 'rangeradmin'@'t3m1' IDENTIFIED BY 'rangeradmin';
GRANT ALL PRIVILEGES ON *.* TO 'rangeradmin'@'t3m1' WITH GRANT OPTION;
FLUSH PRIVILEGES;

CREATE DATABASE rangerkms;
use rangerkms;
CREATE USER 'rangerkms'@'%' IDENTIFIED BY 'rangerkms';
GRANT ALL PRIVILEGES ON *.* TO 'rangerkms'@'%' WITH GRANT OPTION;
CREATE USER 'rangerkms'@'localhost' IDENTIFIED BY 'rangerkms';
GRANT ALL PRIVILEGES ON *.* TO 'rangerkms'@'localhost';
CREATE USER 'rangerkms'@'t3m1' IDENTIFIED BY 'rangerkms';
GRANT ALL PRIVILEGES ON *.* TO 'rangerkms'@'t3m1';

CREATE USER 'rangerkms'@'t3s3.ecloud.com' IDENTIFIED BY 'rangerkms';
GRANT ALL PRIVILEGES ON *.* TO 'rangerkms'@'t3s3.ecloud.com' WITH GRANT OPTION;
FLUSH PRIVILEGES;

select Host,User,Password from user where user='rangerkms';

CREATE DATABASE druid;
use druid;
CREATE USER 'druid'@'%' IDENTIFIED BY 'druid';
GRANT ALL PRIVILEGES ON *.* TO 'druid'@'%' WITH GRANT OPTION;
CREATE USER 'druid'@'localhost' IDENTIFIED BY 'druid' ;
GRANT ALL PRIVILEGES ON *.* TO 'druid'@'localhost' WITH GRANT OPTION;
CREATE USER 'druid'@'t3m1' IDENTIFIED BY 'druid';
GRANT ALL PRIVILEGES ON *.* TO 'druid'@'t3m1' WITH GRANT OPTION;
FLUSH PRIVILEGES;


##################### 设置MySQLJar包
cp /data/zhangwusheng/mysql-connector-java-8.0.12/mysql-connector-java-8.0.12.jar  /usr/share/java/mysql-connector-java.jar

cp /usr/share/java/mysql-connector-java.jar /var/lib/ambari-server/resources/mysql-jdbc-driver.jar

vi /etc/ambari-server/conf/ambari.properties
增加：
server.jdbc.driver.path=/usr/share/java/mysql-connector-java.jar

```



# 5.设置ambari-server并启动

```bash
# 设置ambari-server，在这一步修改jdk为自己的jdk
# ambari-server setup

贵州ambari：pg密码： lR5FLlMqpHjwfnfS

Using python  /usr/bin/python
Setup ambari-server
Checking SELinux...
SELinux status is 'enabled'
SELinux mode is 'permissive'
WARNING: SELinux is set to 'permissive' mode and temporarily disabled.
OK to continue [y/n] (y)?
Customize user account for ambari-server daemon [y/n] (n)? y
Enter user account for ambari-server daemon (root):ambari
Adjusting ambari-server permissions and ownership...
Checking firewall status...
Checking JDK...
[1] Oracle JDK 1.8 + Java Cryptography Extension (JCE) Policy Files 8
[2] Custom JDK
==============================================================================
Enter choice (1): 2
WARNING: JDK must be installed on all hosts and JAVA_HOME must be valid on all hosts.
WARNING: JCE Policy files are required for configuring Kerberos security. If you plan to use Kerberos,please make sure JCE Unlimited Strength Jurisdiction Policy Files are valid on all hosts.
Path to JAVA_HOME: /usr/local/jdk
Validating JDK on Ambari Server...done.
Check JDK version for Ambari Server...
JDK version found: 8
Minimum JDK version is 8 for Ambari. Skipping to setup different JDK for Ambari Server.
Checking GPL software agreement...
GPL License for LZO: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
Enable Ambari Server to download and install GPL Licensed LZO packages [y/n] (n)? y
Completing setup...
Configuring database...
Enter advanced database configuration [y/n] (n)? y
Configuring database...
==============================================================================
Choose one of the following options:
[1] - PostgreSQL (Embedded)
[2] - Oracle
[3] - MySQL / MariaDB
[4] - PostgreSQL
[5] - Microsoft SQL Server (Tech Preview)
[6] - SQL Anywhere
[7] - BDB
==============================================================================
Enter choice (1): 3
Hostname (localhost):
Port (3306):
Database name (ambari):
Username (ambari):
Enter Database Password (bigdata):
Re-enter password:
Configuring ambari database...
Configuring remote database connection properties...
WARNING: Before starting Ambari Server, you must run the following DDL against the database to create the schema: /var/lib/ambari-server/resources/Ambari-DDL-MySQL-CREATE.sql
Proceed with configuring remote database connection properties [y/n] (y)? y
Extracting system views...
ambari-admin-2.7.0.0.897.jar
....
Ambari repo file contains latest json url http://public-repo-1.hortonworks.com/HDP/hdp_urlinfo.json, updating stacks repoinfos with it...
Adjusting ambari-server permissions and ownership...
Ambari Server 'setup' completed successfully.

# 设置ambari-server使用mysql，跳过，使用自带的postgresql
ambari-server setup --jdbc-db=mysql --jdbc-driver=/usr/share/java/mysql-connector-java.jar

#
# ambari-server start

Using python  /usr/bin/python
Starting ambari-server
Ambari Server running with administrator privileges.
Organizing resource files at /var/lib/ambari-server/resources...
Ambari database consistency check started...
Server PID at: /var/run/ambari-server/ambari-server.pid
Server out at: /var/log/ambari-server/ambari-server.out
Server log at: /var/log/ambari-server/ambari-server.log
Waiting for server start.........................
Server started listening on 8080

DB configs consistency check: no errors and warnings were found.
Ambari Server 'start' completed successfully.
```



# 6.配置Hive使用Postgresql

## 6.1  配置PG数据库

- 修改配置

  vi /var/lib/pgsql/data/pg_hba.conf

  /etc/postgresql/10/main/pg_hba.conf

  host    all   hive   10.142.235.1/24         md5

- 重启服务

  systemctl restart postgresql

- 增加权限

  su postgres

  psql

    #贵阳 k0mQJUyVV9eXNR77

  create user hive with password 'k0mQJUyVV9eXNR77';

  ​	create database hive owner hive;
  ​	grant all privileges on database hive to hive;





  ​	create user root with password 'hive';

  ​	grant all privileges on database hive to root;

  ​	create user kylin with password 'hive';

  ​	grant all privileges on database hive to kylin ;







  ​	create user hive with password 'hive';

  ​	create database hive owner hive;
  ​	grant all privileges on database hive to hive;

  ​	create user root with password 'hive';

  ​	grant all privileges on database hive to root;

  ​	create user kylin with password 'hive';

  ​	grant all privileges on database hive to kylin ;

  ​	\q

- 设置postgresql jar包路径

  ​	ambari-server setup --jdbc-db=postgres --jdbc-driver=/usr/lib/ambari-server/postgresql-42.2.2.jar

  > 备注：jdbc:postgresql://hbase177.ecloud.com:5432/hive
  >
  > ​	org.postgresql.Driver

- 修改最大连接数

/var/lib/pgsql/data/postgresql.conf修改最大连接数：

max_connections = 200

- 处理组件重复安装问题：


select * from hostcomponentdesiredstate  where component_name like '%LOGSTASH%';

delete from hostcomponentdesiredstate where id=8451

## 6.2 PG主从复制

```bash
#################################################
#安装软件
rpm -qa|grep postgre
rpm -ql postgresql-server-9.2.24-1.el7_5.x86_64

yum -y install postgresql-server
/usr/bin/postgresql-setup initdb

su - postgres
psql
#查看数据库
\l
#use db
\c hive
#查看表
select * from pg_tables where tablename='zws_test';

#################################################
#master主机：

su - postgres
psql
create user cdnrepl with login replication password 'cdnrepl';

create role cdnrepl with login replication password 'cdnrepl';

mkdir /var/lib/pgsql/archieve/

#修改配置文件，允许从机连接pg

vi /var/lib/pgsql/data/pg_hba.conf
host    replication     cdnrepl         192.168.2.41/25         md5
host    replication     cdnrepl         36.111.140.41/25         md5
host    all     postgres         192.168.2.41/25         trust
host    all     postgres         36.111.140.41/25         trust

vi /var/lib/pgsql/data/postgresql.conf
max_wal_senders =4
wal_level = hot_standby #different version :lower:hot_standby,upper version:replica
wal_receiver_status_interval = 2s
hot_standby_feedback = on
wal_keep_segments = 32          # in logfile segments, 16MB each; 0 disables
replication_timeout = 60s       # in milliseconds; 0 disables
log_connections = on
archive_mode = on #
archive_command = 'cp %p /var/lib/pgsql/archieve/%f'

#注意，这里是*监听所有的IP
listen_addresses="*"

#重启数据库
systemctl restart postgresql


#主库上生成测试数据
create table zws_test(id int);
insert into zws_test select 1;
insert into zws_test select 2;
insert into zws_test select 3;
insert into zws_test select 4;

#########################################
#从库上备份数据 36

#测试连接主数据库
psql -h 192.168.2.40 -U hive -W -d hive
su - postgres
mkdir /var/lib/pgsql/data
chmod 700 /var/lib/pgsql/data

#备份数据
pg_basebackup -D /var/lib/pgsql/data  -Fp -Xs -v -P -h 192.168.2.43 -U cdnrepl -p 5432
pg_basebackup -D /var/lib/pgsql/data  -Fp -Xs -v -P -h 192.168.189.40 -U cdnrepl -p 5432

cp /usr/share/pgsql/recovery.conf.sample /var/lib/pgsql/data/recovery.conf
#修改内容
standby_mode = on
primary_conninfo = 'host=192.168.2.43 port=5432 user=cdnrepl password=cdnrepl'
trigger_file = '/var/lib/pgsql/data/trigger.kenyon'
recovery_target_timeline = 'latest'

#修改：
1.vi /var/lib/pgsql/data/postgresql.conf
hot_standby = on

#重启数据库
systemctl restart postgresql

#master主机查看
select * from pg_stat_replication;
#==============================================
#主备切换
#停掉master主机的
systemctl stop postgresql

#备机
su - postgres
pg_ctl promote
```



```bash
#常用命令
 pg_controldata /var/lib/pgsql/data/

```

## 6.3 常用Psql命令

```bash
#show databases
\l
#use ambari
\c ambari
#show tables;
SELECT * FROM information_schema.tables where table_schema='ambari';

#
select *from ambari.hosts where host_name='ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net';
```



## 6.4 删除过期binlog数据

```bash
cd  /var/lib/pgsql/archieve
# +2 2 day before，-2 in two days
find . -type f -mtime +3 -exec rm -f {} \;

```





# 7.安装配置部署HDP集群

- 第一步：


打开ambariserver    http://localhost:8080/#/login

初始密码为：admin/admin

本地仓库地址：

http://192.168.0.47/ambari/HDP/centos7/3.0.0.0-1634

http://192.168.0.47/ambari/HDP-GPL/centos7/3.0.0.0-1634

http://192.168.0.47/ambari/HDP-UTILS/centos7/1.1.0.22



http://192.168.1.36:18181/ambari/HDP/centos7/3.1.0.0-78/

http://192.168.1.36:18181/ambari/HDP-GPL/centos7/3.1.0.0-78/

http://192.168.1.36:18181/ambari/HDP-UTILS/centos7/1.1.0.22/

> 说明：
>
> 3.1安装有的时候有问题，这个文件生成的baseurl是空的，需要手工修改：
>
> https://community.hortonworks.com/articles/231020/ambari-273-ambari-writes-empty-baseurl-values-writ.html
>
> cd /usr/lib/ambari-server/web/javascripts
>
> cp app.js app.js_backup
>
> vi app.js
>
>   onNetworkIssuesExist: function () {
>     if (this.get('networkIssuesExist')) {
>       this.get('content.stacks').forEach(function (stack) {
>           stack.setProperties({
>             usePublicRepo: false,
>             useLocalRepo: true
>           });
>           stack.cleanReposBaseUrls();
>       });
>     }
>   }.observes('networkIssuesExist'),
>
> 修改为：
>
>   onNetworkIssuesExist: function () {
>     if (this.get('networkIssuesExist')) {
>       this.get('content.stacks').forEach(function (stack) {
>         if(stack.get('useLocalRepo') != true){
>           stack.setProperties({
>             usePublicRepo: false,
>             useLocalRepo: true
>           });
>           stack.cleanReposBaseUrls();
>         }
>       });
>     }
>   }.observes('networkIssuesExist'),
>
> 修改完毕后，
>
> ambari-server  stop
>
> ambari-server  reset
>
> ambari-server  start
>
> 如果不能reset，则需要手工修改数据库数据，参见上面链接







cat /etc/hosts|awk '{print $2;}'

- 第二步：


![1537716187931](/img/ambari-1537716187931.png)



- 第三步：


![1537716424901](/img/ambari-1537716424901.png)



- 第四步：




![1537717128168](/img/ambari-4-1537717128168.png)

-
  第五步：选择服务




![1537717293865](/img/ambari-5-1537717293865.png)



- 第六步：


有用户名的，都是和用户名相同，没有用户名的，都是rangeradmin；rangerkms的密码也是rangeradmin

![1537718408865](/img/ambari-6-1537718408865.png)

![1537718436412](/img/ambari-6-2-1537718436412.png)





第七步：



配置druid：

![1537719552101](/img/ambari-7-druid-1537719552101.png)

配置Hive：

![1537719591630](/img/ambari-7-hive-1537719591630.png)

配置oozie：

![1537719633344](/img/ambari-7-oozie-1537719633344.png)



配置Ranger：

![1537719734149](/img/ambari-7-ranger-1537719734149.png)

配置ranger-kms：



![1537719790658](/img/ambari-7-ranger-kms-1537719790658.png)



第八步：

配置目录，都在默认的目录前面加了/data



第九步：系统用户

![1537720710165](/img/ambari-9-account-1537720710165.png)

![1537720747653](/img/ambari-9-account-2-1537720747653.png)

最后修改：

atlas.admin.password 修改为：atlasadmin123

Ranger Admin user's password for Ambari ：rangeradmin123

Ranger Admin user's password ：rangeradmin123

Ranger KMS keyadmin user's password ：rangeradmin123

Ranger Tagsync user's password ：rangeradmin123

Ranger Usersync user's password ：rangeradmin123



***记得修改所有组件的日志目录！***

***HDFS设置storage policy***

***机器设置RACK***

# 8.Rack配置

https://community.hortonworks.com/articles/43164/rack-awareness-series-2.html



# 9.修改Ambari密码

改成复杂一点的

# 10.Kerberos安装

> ## HDP3.0 Ambari的几个坑:
>
> 1.yarn dns默认端口 hadoop自己是5353,安装的时候变成了53,导致启动yarndns的机器在运行kadmin时出问题
> 2.kerberos 一定要使用域名,不能使用IP
> 3.kerberos一定要他管理krb5.conf,不能清除那个选项,使用自己的配置文件

## 1.安装所需软件

在KDC服务器安装

```bash
#安装软件
yum -y install krb5-server krb5-devel krb5-workstation
#检查版本
rpm -qa|grep krb5
krb5-config --version

ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m shell -b -a "yum -y install krb5-server krb5-devel krb5-workstation"


```
> kerberos有版本要求 -37  -8  -18都可以，但是以前就遇到过-19 的不行（汪聘）

每台机器安装jce

```bash
https://www.oracle.com/technetwork/java/javase/downloads/jce-all-download-5170447.html
C:\work\Source\
unzip -o -j -q /data1/jce_policy-8.zip -d $JAVA_HOME/jre/lib/security/

for ip in `echo 2 10 28 29 37 38 `
do
scp -P 9000 /home/zhangwusheng/soft/jce_policy-8.zip 192.168.254.${ip}:/usr/local/jdk
done

for ip in `echo 2 10 28 29 37 38 `
do
ssh -p 9000 192.168.254.${ip} "unzip -o -j -q /usr/local/jdk/jce_policy-8.zip -d /usr/local/jdk/jre/lib/security/"
done


unzip -o -j -q /home/zhangwusheng/jce_policy-8.zip -d /usr/local/jdk/jre/lib/security/
```

## 2.配置KDC

```bash
# cat /var/kerberos/krb5kdc/kdc.conf

[kdcdefaults]
 kdc_ports = 88
 kdc_tcp_ports = 88

[realms]
 CTYUN.NET = {
  #master_key_type = aes256-cts
  acl_file = /var/kerberos/krb5kdc/kadm5.acl
  dict_file = /usr/share/dict/words
  admin_keytab = /var/kerberos/krb5kdc/kadm5.keytab
  supported_enctypes = aes256-cts:normal aes128-cts:normal des3-hmac-sha1:normal arcfour-hmac:normal camellia256-cts:normal camellia128-cts:normal des-hmac-sha1:normal des-cbc-md5:normal des-cbc-crc:normal

  #这里要加上，否则不能renew
  max_life = 25h 0m 0s
  max_renewable_life = 3650d 0h 0m 0s
 }

 -------------------------------------------------------------------------------
 问题处理：
#关键；如果忘记了max_renewable_life，那么应该确保这个用户是存在的krbtgt
kadmin.local -q "modprinc -maxrenewlife 7days krbtgt/CTYUN.NET"

ssh -p 9000 192.168.254.12 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey kylin/cdnlog012.ctyun.net"'


ssh -p 9000 192.168.254.3 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/kylin.keytab kylin/cdnlog003.ctyun.net"'

#这些命令可以使得用户可以renew
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable kylin/cdnlog040.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable kylin/cdnlog031.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable kylin/cdnlog032.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable kylin/cdnlog041.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable kylin/cdnlog042.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net

modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog002.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog010.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net

 see https://www.jianshu.com/p/54cd2a659698

 #批量修改renew
 /usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "listprincs" > ker.all.txt
 #请认真检查！！
 #去除kadmin,krbtgt,kchangpw，kiprop重要账号！！
 cat ker.all.txt |awk '{print "modprinc -maxlife 25h -maxrenewlife 3650days +allow_renewable "$1;}' > ker.mod.txt

 getprinc HTTP/cdnlog006.ctyun.net@CTYUN.NET
 # maxrenewlife经测试，取min(取值，7)

```

## 3.修改kadm5.acl配置文件

```bash
#修改自己的域的管理员
# cat /var/kerberos/krb5kdc/kadm5.acl
#change here
*/admin@CTYUN.NET     *
```

## 4.修改/etc/krb5.conf文件

> 备注：如果不修改这个文件，启动kdc服务时，会报如下错误：
>
> krb5kdc: Configuration file does not specify default realm - while attempting to retrieve default realm
>
> 疑问：我的理解是这个文件是客户端用的，怎么kdcserver也会用到这个文件呢？仅仅是为了获取默认域？
>
> 这个默认域确实客户端和server端都需要用到

```bash
includedir /etc/krb5.conf.d/

[logging]
 default = FILE:/var/log/krb5libs.log
 kdc = FILE:/var/log/krb5kdc.log
 admin_server = FILE:/var/log/kadmind.log

[libdefaults]
 dns_lookup_realm = false
 ticket_lifetime = 24h
 renew_lifetime = 7d
 forwardable = true
 rdns = false
 pkinit_anchors = /etc/pki/tls/certs/ca-bundle.crt
 #这里需要修改
 default_realm = ECLOUD.COM
 default_ccache_name = KEYRING:persistent:%{uid}

[realms]
#这里需要修改
 ECLOUD.COM = {
  kdc = hbase36.ecloud.com
  admin_server = hbase36.ecloud.com
 }

[domain_realm]
#这里需要修改
 .ecloud.com = ECLOUD.COM
 cloud.com = ECLOUD.COM



#贵阳
#File modified by ipa-client-install

includedir /etc/krb5.conf.d/
includedir /var/lib/sss/pubconf/krb5.include.d/

#added section by zws 2020-11-21
[logging]
 default = FILE:/var/log/krb5libs.log
 kdc = FILE:/var/log/krb5kdc.log
 admin_server = FILE:/var/log/kadmind.log


[libdefaults]
  default_realm = IN.CTCDN.CN
  #dns_lookup_realm = true
  dns_lookup_realm = false
  dns_lookup_kdc = false
  rdns = false
  #dns_canonicalize_hostname = false
  ticket_lifetime = 24h
  renew_lifetime = 7d
  forwardable = true
  udp_preference_limit = 0
  default_ccache_name =/tmp/krb5cc_%{uid}
  #default_ccache_name = KEYRING:persistent:%{uid}
  pkinit_anchors = /etc/pki/tls/certs/ca-bundle.crt

[realms]
  IN.CTCDN.CN = {
#    pkinit_anchors = FILE:/var/lib/ipa-client/pki/kdc-ca-bundle.pem
#    pkinit_pool = FILE:/var/lib/ipa-client/pki/ca-bundle.pem
  kdc = sct-gz-guiyang1-loganalysis-17.in.ctcdn.cn
  admin_server = sct-gz-guiyang1-loganalysis-17.in.ctcdn.cn
  }


[domain_realm]
  .in.ctcdn.cn = IN.CTCDN.CN
  in.ctcdn.cn = IN.CTCDN.CN
  #sct-gz-guiyang1-loganalysis-17.in.ctcdn.cn = IN.CTCDN.CN
```



## 5.创建KDC数据库

```bash
kdb5_util create  -s -r CTYUN.NET
密码:cdnlog@kdc!@#

kdb5_util create  -s -r IN.CTCDN.CN
```

## 6.启动KDC

```bash
systemctl restart krb5kdc
systemctl restart kadmin
systemctl enable krb5kdc.service
systemctl enable kadmin.service
```

## 7.创建远程管理员

```bash
kadmin.local:  addprinc root/admin
密码：cdnlog@kdc!@#

#或者一个命令行
/usr/sbin/kadmin.local -q "addprinc root/admin"
#备注 admin/admin不用添加，直接使用kadmin.local即可

```

> https://www.jianshu.com/p/4200c260c152?utm_campaign=maleskine&utm_content=note&utm_medium=seo_notes&utm_source=recommendation
>
> 网上看到的关于admin/admin与root/admin的区别
>
> 管理帐号包含两种kadmin.local和kadmin帐号，其中kadmin.local是kdc服务器上的本地管理帐号，一定要在kdc服务器才能登录，还有kadmin管理帐号会在部署了各个节点上的krb5配置后会作为各个节点的的管理帐号
>
> 其中admin/admin为kdc服务上kadmin.local的管理帐号，同时还需要创建一个root/admin的各个客户端的管理帐号(密码都设置为clife.data)

## 8.重启服务

```bash
systemctl restart kadmin.service
systemctl restart krb5kdc.service

#备注：添加了root账号之后，一定要重启两个服务，否则下面的验证不能通过，会报第三个错误
验证一下:
kadmin
如果能连通，就说明配置正确，连不通，说明配置有问题，可能存在的两个问题
1.Yarn的DNS配置了53端口，这个要改掉、
2./etc/resolv.conf检查一下，云主机把114和115去掉
3.报错：kadmin: Communication failure with server while initializing kadmin interface
重启kadmind
```

## 9.Ambari安装Kerberos

## 10.Kerberos启动主从



主KDC上：



#addprinc  -randkey  host/hbase36.ecloud.com

#addprinc  -randkey druid-cdnlog@CTYUNCDN.NET
rm -f /etc/security/keytabs/druid.headless.keytab
#xst -k /etc/security/keytabs/druid.headless.keytab  druid-cdnlog@CTYUNCDN.NET
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "xst  -k /etc/security/keytabs/druid.headless.keytab  druid-cdnlog@CTYUNCDN.NET"
chmod a+r /etc/security/keytabs/druid.headless.keytab
#ktadd host/hbase36.ecloud.com

首先在40master上添加如下两个账号;

addprinc kadmin/cdnlog036.ctyun.net

addprinc kadmin/cdnlog039.ctyun.net

addprinc kiprop/cdnlog036.ctyun.net

addprinc kiprop/cdnlog039.ctyun.net

cdnlog@kdc!@#

master上：

```bash
mkdir -p /var/kerberos/backup
cd /var/kerberos/backup
datestr=`date +%Y%m%d`
rm -f /var/kerberos/krb5kdc/backup.dump.${datestr}
kdb5_util dump /var/kerberos/krb5kdc/backup.dump.${datestr}
rm -f /var/kerberos/krb5kdc.${datestr}.tar.gz
tar zcvf /var/kerberos/krb5kdc.${datestr}.tar.gz /var/kerberos/krb5kdc/*

for ip in `seq 45 50`
do
 echo "------------${ip}"
 scp -P 9000 /var/kerberos/krb5kdc.${datestr}.tar.gz 192.168.254.${ip}:/var/kerberos
done

for ip in `echo 36 39 35 41 42` `seq 30 32` `seq 25 27` `seq 21 22` `seq 15 18` `seq 12 12` `seq 5 9`
do
 echo "------------${ip}"
 scp -P 9000 /var/kerberos/krb5kdc.${datestr}.tar.gz 192.168.254.${ip}:/var/kerberos
done

```

slave上：

做到第五步之后（创建了数据库之后）：

kdb5_util load /var/kerberos/krb5kdc/backup.dump.20190805

最后一次备份是20200202，备份到了36和39上面



```bash
cd /var/kerberos/backup
vi backup.sh

#backup-kerberos.sh
BACKUP_DIR=/var/kerberos/backup
mkdir -p ${BACKUP_DIR}
cd ${BACKUP_DIR}
datestr=`date +%Y%m%d%H%M`
#rm -f /var/kerberos/krb5kdc/backup.dump.${datestr}
kdb5_util dump /var/kerberos/krb5kdc/backup.dump.${datestr}
#rm -f /var/kerberos/krb5kdc.${datestr}.tar.gz
tar zcvf ${BACKUP_DIR}/krb5kdc.${datestr}.tar.gz /var/kerberos/krb5kdc/*

scp -P 9000 ${BACKUP_DIR}/krb5kdc.${datestr}.tar.gz 192.168.254.36:/var/kerberos
scp -P 9000 ${BACKUP_DIR}/krb5kdc.${datestr}.tar.gz 192.168.254.39:/var/kerberos


#设置crontab
50 */2 * * * /bin/bash /var/kerberos/backup/backup.sh
```

备份到其他主机：



```bash
ansible master -m shell -a "mkdir -p /home/zhangwusheng/data/kdc"

ansible master -m shell -a "wget http://192.168.254.40:8181/data/krb5kdc.202004241650.tar.gz -O /home/zhangwusheng/data/kdc/krb5kdc.202004241650.tar.gz "
```



## 11.KDC保活

vi /usr/lib/systemd/system/krb5kdc.service

[Service]
Restart=on-abnormal



## 12.安装/移除组件

使用如下用户名和密码：

root/admin
cdnlog@kdc!@#



```bash



-----------------------------------------
# kadmin.local -q "addprinc admin/admin@CDNLOG"
kadmin.local -q "addprinc admin/admin@CTYUNCDN.NET"
cdnlog@kdc!@#


kadmin.local -q "addprinc kadmin/192.168.1.66@CDNLOG"

Authenticating as principal root/admin@CDNLOG with password.
WARNING: no policy specified for admin/admin@CDNLOG; defaulting to no policy
Enter password for principal "admin/admin@CDNLOG":
Re-enter password for principal "admin/admin@CDNLOG":
Principal "admin/admin@CDNLOG" created.

# kadmin.local -q "xst -norandkey admin/admin@CDNLOG"
kadmin.local -q "xst -norandkey admin/admin@CTYUNCDN.NET"
cdnlog@kdc!@#

Authenticating as principal root/admin@CDNLOG with password.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type aes256-cts-hmac-sha1-96 added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type aes128-cts-hmac-sha1-96 added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type des3-cbc-sha1 added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type arcfour-hmac added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type camellia256-cts-cmac added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type camellia128-cts-cmac added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type des-hmac-sha1 added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type des-cbc-md5 added to keytab FILE:/etc/krb5.keytab.




kadmin.local
Authenticating as principal root/admin@CDNLOG with password.
kadmin.local:  listprincs
K/M@CDNLOG
admin/admin@CDNLOG
kadmin/admin@CDNLOG
kadmin/changepw@CDNLOG
kadmin/hbase73.ecloud.com@CDNLOG
kiprop/hbase73.ecloud.com@CDNLOG
krbtgt/CDNLOG@CDNLOG

kadmin.local:  addprinc root/admin
cdnlog@kdc!@#

WARNING: no policy specified for root/admin@CDNLOG; defaulting to no policy
Enter password for principal "root/admin@CDNLOG":
Re-enter password for principal "root/admin@CDNLOG":
Principal "root/admin@CDNLOG" created.
kadmin.local:
```





- krb5.conf

由Ambari管理！修改realm即可

```bash
[root@hbase171 yum.repos.d]#  cat /etc/krb5.conf
# Configuration snippets may be placed in this directory as well
includedir /etc/krb5.conf.d/

[logging]
 default = FILE:/var/log/krb5libs.log
 kdc = FILE:/var/log/krb5kdc.log
 admin_server = FILE:/var/log/kadmind.log

[libdefaults]
 dns_lookup_realm = false
 ticket_lifetime = 24h
 renew_lifetime = 7d
 forwardable = true
 rdns = false
 #change here
 default_realm = ECLOUD.COM
 default_ccache_name = KEYRING:persistent:%{uid}

[realms]
#change here
 ECLOUD.COM = {
  kdc = hbase171.ecloud.com
  admin_server = hbase171.ecloud.com
 }

[domain_realm]
#change here
.ecloud.com = ECLOUD.COM
ecloud.com = ECLOUD.COM



[root@hbase171 3.1.0.0-78]# kadmin.local
Authenticating as principal root/admin@ECLOUD.COM with password.
kadmin.local:  addprinc admin/admin@ECLOUD.COM
WARNING: no policy specified for admin/admin@ECLOUD.com; defaulting to no policy
Enter password for principal "admin/admin@ECLOUD.com": kerberos
Re-enter password for principal "admin/admin@ECLOUD.com": kerberos
Principal "admin/admin@ECLOUD.com" created.
kadmin.local:  exit



kadmin.local -r ECLOUD.COM -p admin/admin

scp /etc/krb5.conf 192.168.1.106:/etc
scp /etc/krb5.conf 192.168.1.48:/etc



[root@hbase106 ~]#  systemctl enadble kadmin.service
```

krb5-config --version



![1557912194106](/img/ambari-install-kerberos.png)



















```
kdb5_util(1M)
名称
kdb5_util - Kerberos Database maintenance utility
用法概要
/usr/sbin/kdb5_util [-d dbname] [-k mkeytype] [-kv mkeyVNO] [-m ]
     [-M mkeyname] [-P password] [-r realm] [-sf stashfilename]
     [-x db_args]... cmd
描述
The kdb5_util utility enables you to create, dump, load, and destroy the Kerberos V5 database. You can also use kdb5_util to create a stash file containing the Kerberos database master key.

选项
The following options are supported:

–d dbname
Specify the database name. .db is appended to whatever name is specified. You can specify an absolute path. If you do not specify the –d option, the default database name is /var/krb5/principal.

–k mkeytype
Specify the master key type. Valid values are des3-cbc-sha1, des-cbc-crc, des-cbc-md5, des-cbc-raw, arcfour-hmac-md5, arcfour-hmac-md5-exp, aes128-cts-hmac-sha1-96 , and aes256-cts-hmac-sha1-96.

–m
Enter the master key manually.

–M mkeyname
Specify the master key name.

–P password
Use the specified password instead of the stash file.

–r realm
Use realm as the default database realm.

–sf stashfile_name
Specifies the stash file of the master database password.

–x db_args
Pass database-specific arguments to kadmin. Supported arguments are for LDAP and the Berkeley-db2 plug-in. These arguments are:

binddn=binddn
LDAP simple bind DN for authorization on the directory server. Overrides the ldap_kadmind_dn parameter setting in krb5.conf(4).

bindpwd=bindpwd
Bind password.

dbname=name
For the Berkeley-db2 plug-in, specifies a name for the Kerberos database.

nconns=num
Maximum number of server connections.

port=num
Directory server connection port.

操作数
The following operands are supported:

cmd
Specifies whether to create, destroy, dump, or load the database, or to create a stash file.

You can specify the following commands:

create –s
Creates the database specified by the –d option. You will be prompted for the database master password. If you specify –s, a stash file is created as specified by the –f option. If you did not specify –f, the default stash file name is /var/krb5/.k5.realm. If you use the –f, –k, or –M options when you create a database, then you must use the same options when modifying or destroying the database.

destroy
Destroys the database specified by the –d option.

stash
Creates a stash file. If –f was not specified, the default stash file name is /var/krb5/.k5.realm. You will be prompted for the master database password. This command is useful when you want to generate the stash file from the password.

dump [–old] [–b6] [–b7] [–ov] [–r13] [–verbose] [–mkey_convert] [–new_mkey_file mkey_file] [–rev] [–recurse] [filename [principals...]]
Dumps the current Kerberos and KADM5 database into an ASCII file. By default, the database is dumped in current format, “kdb5_util load_dumpversion 6”. If filename is not specified or is the string “-”, the dump is sent to standard output. Options are as follows:

–old
Causes the dump to be in the Kerberos 5 Beta 5 and earlier dump format (“kdb5_edit load_dump version 2.0”).

–b6
Causes the dump to be in the Kerberos 5 Beta 6 format (“kdb5_edit load_dump version 3.0”).

–b7
Causes the dump to be in the Kerberos 5 Beta 7 format (“kdb5_util load_dump version 4”). This was the dump format produced on releases prior to 1.2.2.

–ov
Causes the dump to be in ovsec_adm_export format.

–r13
Causes the dump to be in the Kerberos 5 1.3 format (“kdb5_util load_dump version 5”). This was the dump format produced on releases prior to 1.8.

–verbose
Causes the name of each principal and policy to be displayed as it is dumped.

–mkey_convert
Prompts for a new master key. This new master key will be used to re-encrypt the key data in the dumpfile. The key data in the database will not be changed.

–new_mkey_file mkey_file
The filename of a stash file. The master key in this stash file will be used to re-encrypt the key data in the dumpfile. The key data in the database will not be changed.

–rev
Dumps in reverse order. This might recover principals that do not dump normally, in cases where database corruption has occured.

–recurse
Causes the dump to walk the database recursively (btree only). This might recover principals that do not dump normally, in cases where database corruption has occurred. In cases of such corruption, this option will probably retrieve more principals than will the –rev option.

load [–old] [–b6] [–b7] [–ov] [–r13] [–hash] [–verbose] [–update] filename dbname [ admin_dbname]
Loads a database dump from filename into dbname. Unless the –old or –b6 option is specified, the format of the dump file is detected automatically and handled appropriately. Unless the –update option is specified, load creates a new database containing only the principals in the dump file, overwriting the contents of any existing database. The –old option requires the database to be in the Kerberos 5 Beta 5 or earlier format (“kdb5_edit load_dump version 2.0”).

–b6
Requires the database to be in the Kerberos 5 Beta 6 format (“kdb5_edit load_dump version 3.0”).

–b7
Requires the database to be in the Kerberos 5 Beta 7 format (“kdb5_util load_dump version 4”).

–ov
Requires the database to be in ovsec_adm_import format. Must be used with the –update option.

–hash
Requires the database to be stored as a hash. If this option is not specified, the database will be stored as a btree. This option is not recommended, as databases stored in hash format are known to corrupt data and lose principals.

–r13
Causes the dump to be in the Kerberos 5 1.3 format (“kdb5_util load_dump version 5”). This was the dump format produced on releases prior to 1.8.

–verbose
Causes the name of each principal and policy to be displayed as it is dumped.

–update
Records from the dump file are added to or updated in the existing database. Otherwise, a new database is created containing only what is in the dump file and the old one is destroyed upon successful completion.

filename
Required argument that specifies a path to a file containing database dump.

dbname
Required argument that overrides the value specified on the command line or overrides the default.

admin_dbname
Optional argument that is derived from dbname if not specified.

add_mkey [–e etype] [–s]
Adds a new master key to the K/M (master key) principal. Existing master keys will remain. The –e etype option allows specification of the enctype of the new master key. The –s option stashes the new master key in a local stash file which will be created if it does not already exist.

use_mkey mkeyVNO [time]
Sets the activation time of the master key specified by mkeyVNO. Once a master key is active (that is, its activation time has been reached) it will then be used to encrypt principal keys either when the principal keys change, are newly created, or when the update_princ_encryption command is run. If the time argument is provided, that will be the activation time; otherwise the current time is used by default. The format of the optional time argument is that specified in the Time Formats section of the kadmin(1M) man page.

list_mkeys
List all master keys from most recent to earliest in K/M principal. The output will show the KVNO, enctype and salt for each mkey, similar to kadmin getprinc output. An asterisk (*) following an mkey denotes the currently active master key.

purge_mkeys [–f] [–n] [–v]
Delete master keys from the K/M principal that are not used to protect any principals. This command can be used to remove old master keys from a K/M principal once all principal keys are protected by a newer master key.

–f
Does not prompt user.

–n
Does a dry run, shows master keys that would be purged, but does not actually purge any keys.

–v
Verbose output.

update_princ_encryption [–f] [–n] [–v] [princ-pattern]
Update all principal records (or only those matching the princ-pattern glob pattern) to re-encrypt the key data using the active database master key, if they are encrypted using older versions, and give a count at the end of the number of principals updated. If the –f option is not given, ask for confirmation before starting to make changes. The –v option causes each principal processed (each one matching the pattern) to be listed, and an indication given as to whether it needed updating or not. The –n option causes the actions not to be taken, only the normal or verbose status messages displayed; this implies –f, since no database changes will be performed and thus there is little reason to seek confirmation.

示例
示例 1 Creating File that Contains Information about Two Principals
The following example creates a file named slavedata that contains the information about two principals, jdb@ACME.COM and pak@ACME.COM.


# /usr/krb5/bin/kdb5_util dump -verbose slavedata
jdb@ACME.COM pak@ACME.COM

文件
/var/krb5/principal
Kerberos principal database.

/var/krb5/principal.kadm5
Kerberos administrative database. Contains policy information.

/var/krb5/principal.kadm5.lock
Lock file for the Kerberos administrative database. This file works backwards from most other lock files (that is, kadmin exits with an error if this file does not exist).

/var/krb5/principal.ulog
The update log file for incremental propagation.

属性
See attributes(5) for descriptions of the following attributes:

ATTRIBUTE TYPE
ATTRIBUTE VALUE
Availability
system/security/kerberos-5
Interface Stability
Committed
另请参见
kpasswd(1), gkadmin(1M), kadmin(1M), kadmind(1M), kdb5_ldap_util(1M), kproplog(1M), kadm5.acl(4), kdc.conf(4), attributes(5), kerberos(5)

附注
The global –f is made obsolete with the –sf argument for specifying a non-default stash file location. The global –f argument might be removed in a future release of the Solaris operating system. Use caution in specifying –f as it has different semantics in subcommands as distinguished from its use as a global argument.
```

## 13.KDC共存问题

cat /var/lib/sss/pubconf/kdcinfo.CTYUNCDN.NET
36.111.140.104



/etc/sssd/sssd.conf

增加sssd.conf

krb5_use_kdcinfo = false

systemctl restart sssd



备注：

在启用kerberos的时候可能Test Client不通过，这时候要全部机器都设置这个选相关，这样就可以通过了。亲测



## 14.spark kerberos7天的问题

https://docs.cloudera.com/documentation/enterprise/5-3-x/topics/cm_sg_yarn_long_jobs.html



https://www.pianshen.com/article/7395176073/





```bash
spark加上
--principal <value> \
  --keytab <value> \

  ./bin/spark-submit \
  --class <main-class> \
  --master <master-url> \
  --deploy-mode <deploy-mode> \
  --conf <key>=<value> \
  --principal <value> \
  --keytab <value> \
  <application-jar> \
  [application-arguments]
```

Yarn配置：

```
<property>
<name>yarn.resourcemanager.proxy-user-privileges.enabled</name>
<value>true</value>
</property>
```

HDFS配置

```
<property>
<name>hadoop.proxyuser.yarn.hosts</name>
<value>*</value>
</property>

<property>
<name>hadoop.proxyuser.yarn.groups</name>
<value>*</value>
</property>
```

# 11.启用Hadoop和Spark Basic认证

废弃，参见Windows下Kerberos小节

yarn/hdfs/spark在启用了kerberos后，webui访问比较麻烦，需要windows下安装kerberos客户端，所以改成basic访问，用户输入用户名和密码。



yarn:CdnYarnMd5!$&  3a033cd5793abaa4fe8975f19cc93096

yarn:3a033cd5793abaa4fe8975f19cc93096

| HDFS                                                         |                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| hadoop.http.authentication.type                              | com.ctg.hadoop.security.authentication.server.BasicAuthenticationHandler |
| hadoop.http.authentication.basic.userCredential              | yarn:4ae173c92b702cd54eea8ccb04f64036                        |
| SPARK2（目前是简单密码，需要改成和上面一样，加上md5）        |                                                              |
| Advanced spark2-env                                          | {% if security_enabled %}里面的kerberos参数注释掉            |
| Custom spark2-defaults                                       |                                                              |
| spark.ui.filters                                             | com.ctg.security.spark.SparkBasicAuthFilter                  |
| spark.com.ctg.security.spark.SparkBasicAuthFilter.param.username | spark                                                        |
| spark.com.ctg.security.spark.SparkBasicAuthFilter.param.password | spark123456                                                  |

备注：Hadoop自己提供了这个类：

org.apache.hadoop.security.authentication.server.MultiSchemeAuthenticationHandler



## 15.kerberos互信

```bash
https://community.cloudera.com/t5/Community-Articles/Kerberos-cross-realm-trust-for-distcp/ta-p/245590

https://docs.cloudera.com/documentation/enterprise/5-12-x/topics/cdh_admin_distcp_data_cluster_migrate.html#concept_fx2_t1q_3x



 hadoop distcp hftp://cdh57-namenode:50070/ hdfs://CDH59-nameservice/

 #上海访问武汉：


 1192  hadoop jar /usr/hdp/3.1.0.0-78/hadoop-mapreduce/hadoop-mapreduce-examples-3.1.1.3.1.0.0-78.jar wordcount /tmp/11.txt /tmp/wc-3
 1193  hdfs dfs -ls /tmp/wc-3
 1194  hdfs dfs -cat /tmp/wc-3/part*
 1195  hadoop distcp hdfs://none-hb-wuhan-cdnlog-106-ecloud.com:8020/tmp/11.txt hdfs://none-hb-wuhan-cdnlog-106-ecloud.com:8020/tmp/
 1196  hadoop distcp hdfs://none-hb-wuhan-cdnlog-106-ecloud.com:8020/tmp/11.txt hdfs://none-hb-wuhan-cdnlog-106-ecloud.com:8020/tmp/distcp-1
 1197  hadoop distcp hdfs://none-hb-wuhan-cdnlog-106-ecloud.com:8020/tmp/11.txt hdfs://none-hb-wuhan-cdnlog-106-ecloud.com:8020/tmp/distcp-1
 1198  hadoop distcp hdfs://none-hb-wuhan-cdnlog-106-ecloud.com:8020/tmp/11.txt hdfs://none-hb-wuhan-cdnlog-106-ecloud.com:8020/tmp/distcp-1

 https://docs.cloudera.com/documentation/enterprise/latest/topics/cdh_admin_distcp_data_cluster_migrate.html#concept_fx2_t1q_3x

 http://confluence.ctyuncdn.cn/pages/viewpage.action?pageId=26751129
```






jmap -F -dump:format=b,file=peon.bin 224403




# 12.Kylin安装

问题排查：
grep   'Duration:' /data2/apache-kylin-2.6.1-bin-hadoop3/logs/kylin.log.*|sort -n -k2,2 > /home/zhangwusheng/kylin.slow.log.`hostname`


 tail -n 20 /home/zhangwusheng/kylin.slow.log.`hostname` |awk -F':' '{printf("echo ========\ngrep -b4 \"%s:%s\" %s\n",$2,$3,$1);}' > /home/zhangwusheng/t1.sh ;bash /home/zhangwusheng/t1.sh|more

## 1.增加kylin用户

```bash
groupadd cdnlog
useradd kylin -g cdnlog
usermod -G hadoop kylin
echo 'kylin   ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers

useradd cdnlog -g cdnlog

/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey kylin/cdnlog002.ctyun.net@CTYUN.NET"
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey kylin/cdnlog010.ctyun.net@CTYUN.NET"
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey kylin/cdnlog028.ctyun.net@CTYUN.NET"
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey kylin/cdnlog029.ctyun.net@CTYUN.NET"
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey kylin/cdnlog037.ctyun.net@CTYUN.NET"
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey kylin/cdnlog038.ctyun.net@CTYUN.NET"
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey kylin/cdnlog017.ctyun.net@CTYUN.NET"
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey kylin/cdnlog047.ctyun.net@CTYUN.NET"


/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "listprincs"

for ip in `cat cdn_hosts_all.txt`
do
  echo ${ip}
  ssh -p 9000 ${ip} "klist -k /etc/security/keytabs/kylin.keytab"
done


modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog002.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog010.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net
modprinc -maxlife 1days -maxrenewlife 7days +allow_renewable cdnlog/cdnlog040.ctyun.net

/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey kylin/cdnlog047.ctyun.net@CTYUN.NET"

/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "xst -k /etc/security/keytabs/kylin.keytab kylin/cdnlog002.ctyun.net"

/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "xst -k /etc/security/keytabs/kylin.keytab kylin/cdnlog047.ctyun.net"
klist -k /etc/security/keytabs/kylin.keytab


for ip in `cat cdn_hosts_nonkylin.txt`
do
  echo "ssh -p 9000 ${ip} \"rm -f /etc/security/keytabs/kylin.keytab\""
done> kylin.keytab.sh


for ip in `cat cdn_hosts_nonkylin.txt`
do
  aa=`echo ${ip}|awk -F'.' '{printf("%03d",$4)}'`
  echo "ssh -p 9000 ${ip} /usr/bin/kadmin -p root/admin -w 'passwd' -q \"xst -k /etc/security/keytabs/kylin.keytab kylin/cdnlog${aa}.ctyun.net\""
done>> kylin.keytab.sh

sed -i 's/passwd/cdnlog@kdc!@#/g' kylin.keytab.sh


klist -k /etc/security/keytabs/kylin.keytab
mv  /etc/security/keytabs/kylin.keytab /etc/security/keytabs/kylin.keytab.20200103
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "xst -k /etc/security/keytabs/kylin.keytab kylin/cdnlog031.ctyun.net"

klist -k /etc/security/keytabs/kylin.keytab
mv  /etc/security/keytabs/kylin.keytab /etc/security/keytabs/kylin.keytab.20200103
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "xst -k /etc/security/keytabs/kylin.keytab kylin/cdnlog032.ctyun.net"
klist -k /etc/security/keytabs/kylin.keytab

klist -k /etc/security/keytabs/kylin.keytab
mv  /etc/security/keytabs/kylin.keytab /etc/security/keytabs/kylin.keytab.20200103
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "xst -k /etc/security/keytabs/kylin.keytab kylin/cdnlog041.ctyun.net"
klist -k /etc/security/keytabs/kylin.keytab

klist -k /etc/security/keytabs/kylin.keytab
mv  /etc/security/keytabs/kylin.keytab /etc/security/keytabs/kylin.keytab.20200103
/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "xst -k /etc/security/keytabs/kylin.keytab kylin/cdnlog042.ctyun.net"
klist -k /etc/security/keytabs/kylin.keytab

#批量增加机器

```



## 2.设置环境变量

```bash
##Standalone版本
export KYLIN_HOME=/data2/apache-kylin-2.6.1-bin-hadoop3
export HADOOP_HOME=/usr/hdp/3.0.0.0-1634/hadoop
export SPARK_HOME=/data1/spark-2.3.2-bin-hadoop2.7
export PATH=$PATH:$SPARK_HOME/bin

##HDP版本
echo 'export SPARK_HOME=/usr/hdp/3.0.0.0-1634/spark2' > /etc/profile.d/spark.sh
echo 'export PATH=$PATH:$SPARK_HOME/bin' >> /etc/profile.d/spark.sh
mv /usr/hdp/3.0.0.0-1634/spark2/bin/beeline /usr/hdp/3.0.0.0-1634/spark2/bin/spark-beeline
source /etc/profile.d/spark.sh


#北京CDN
echo 'export SPARK_HOME=/usr/hdp/3.1.0.0-78/spark2' > /etc/profile.d/spark.sh
echo 'export PATH=$PATH:$SPARK_HOME/bin' >> /etc/profile.d/spark.sh
source /etc/profile.d/spark.sh



```

## 3.修改Hive脚本(非kerberos)

```bash
vi /usr/hdp/current/hive-client/bin/hive.distro

  if [ SERVICE == "cli" -o SERVICE == "beeline" ]
  then
      $TORUN -p hive -n kylin "@"
  else
      $TORUN "@"
  fi

```

## 4.修复Tomcat

```bash
cd /data1/apache-kylin-2.6.1-bin-hadoop3/tomcat/webapps
mkdir kylin
unzip  ../kylin.war

上传 F:\Soft\HDP\Kylin
commons-configuration-1.6-zws-added.jar

```

## 5.修改并运行check-env.sh

```bash
#首先在hdfs上创建kylin目录(root用户)
kinit  -kt /etc/security/keytabs/hdfs.headless.keytab hdfs-cdnlog
hdfs dfs -mkdir /kylin
hdfs dfs -chown -R kylin:cdnlog /kylin
hdfs dfs -mkdir /user/kylin
hdfs dfs -chown -R kylin:cdnlog /user/kylin
kdestroy

#check-port-availability.sh增加sudo
kylin_port_in_use=`sudo netstat -tlpn | grep "\b${kylin_port}\b"`

vi find-hive-dependency.sh
#加上""否则会报错:too many arguments
if [ -z "$hive_env" ]

#北京CDN生产：
kinit  -kt /etc/security/keytabs/hdfs.headless.keytab hdfs-cdnlog
hdfs dfs -mkdir /kylin
hdfs dfs -chown -R kylin:hadoop /kylin
hdfs dfs -mkdir /user/kylin
hdfs dfs -chown -R kylin:hadoop /user/kylin
kdestroy

#check-port-availability.sh增加sudo
kylin_port_in_use=`sudo netstat -tlpn | grep "\b${kylin_port}\b"`

vi find-hive-dependency.sh
#加上""否则会报错:too many arguments
if [ -z "$hive_env" ]
```

## 6.Kerberos增加kylin princ(root)

```bash
kadmin:
输入密码：cdnlog@kdc!@#

运行命令：
addprinc kylin/hbase36.ecloud.com@ECLOUD.COM
xst -k /etc/security/keytabs/kylin.keytab  kylin/hbase36.ecloud.com@ECLOUD.COM
quit

systemctl restart krb5kdc
systemctl restart kadmin

cp /etc/krb5.keytab /etc/security/keytabs/kylin.keytab
chown kylin:hadoop  /etc/security/keytabs/kylin.keytab
#验证是否能够成功
kinit -kt  /etc/security/keytabs/kylin.keytab  kylin

#北京
addprinc kylin/cdnlog040.ctyun.net@CTYUN.NET
xst -k /etc/security/keytabs/kylin.keytab  kylin/cdnlog040.ctyun.net@CTYUN.NET

systemctl restart krb5kdc
systemctl restart kadmin
chown kylin:hadoop  /etc/security/keytabs/kylin.keytab
kinit -kt  /etc/security/keytabs/kylin.keytab  kylin/cdnlog040.ctyun.net
klist
```

## 7.建立Kylin专用hive库

```bash
#先建立目录,然后kylin库指定到这个目录
kinit  -kt /etc/security/keytabs/hdfs.headless.keytab hdfs-cdnlog
sudo -u hdfs hdfs dfs -mkdir  /warehouse/tablespace/external/hive/kylin.db
sudo -u hdfs hdfs dfs -chown -R kylin:hadoop  /warehouse/tablespace/external/hive/kylin.db
kdestroy

kinit -kt  /etc/security/keytabs/kylin.keytab  kylin
#hive建kylin库,修改为kylin用户的

beeline:
CREATE DATABASE IF NOT EXISTS kylin LOCATION "hdfs://cdnlog/warehouse/tablespace/external/hive/kylin.db"

#修改kylin配置
#修改hive库默认为kylin
#kylin.source.hive.database-for-flat-table=default
kylin.source.hive.database-for-flat-table=kylin

#北京
kinit  -kt /etc/security/keytabs/hdfs.headless.keytab hdfs-cdnlog
sudo -u hdfs hdfs dfs -mkdir  /warehouse/tablespace/external/hive/kylin.db
sudo -u hdfs hdfs dfs -chown -R kylin:hadoop  /warehouse/tablespace/external/hive/kylin.db
kdestroy

klist -k /etc/security/keytabs/hive.service.keytab
kinit -kt /etc/security/keytabs/hive.service.keytab hive/cdnlog040.ctyun.net

hive
CREATE DATABASE IF NOT EXISTS kylin LOCATION "hdfs://cdnlog/warehouse/tablespace/external/hive/kylin.db"
#修改hive库默认为kylin
#kylin.source.hive.database-for-flat-table=default
kylin.source.hive.database-for-flat-table=kylin
kylin.storage.hbase.namespace=kylin
```

## 8.修改Kylin运行hive

```bash
vi kylin.properties
kylin.source.hive.beeline-shell=/usr/bin/beeline
#注意这里一定是hive,不能是kylin
kylin.source.hive.beeline-params=kylin.source.hive.beeline-params=-u"jdbc:hive2://hbase36.ecloud.com:10000;principal=hive/hbase36.ecloud.com@ECLOUD.COM"
kylin.web.timezone=GMT+8

vi find-hive-dependency.sh
#这里去掉那些参数
hive_env=`${beeline_shell}  -e"set;" 2>&1 | grep --text 'env:CLASSPATH' `

```

## 9.Kylin的Hbase配置

```bash

kylin.storage.hbase.namespace=kylin
kylin.storage.hbase.compression-codec=snappy
kylin.metadata.url=kylin:kylin_metadata@hbase
#
klist -k /etc/security/keytabs/hbase.service.keytab
kinit -kt /etc/security/keytabs/hbase.service.keytab  hbase/hbase36.ecloud.com
hbase shell:
create_namespace "kylin"
grant 'kylin','RWXCA','@kylin'
quit



```



启动kylin

```bash
#启动kylin
su - kylin

kinit -kt  /etc/security/keytabs/kylin.keytab  kylin/cdnlog040.ctyun.net
ln -fs /data2/apache-kylin-2.6.1-bin-hadoop3 /usr/local/kylin

#删除两个树形，这个不能运行时修改
kylin_hive_conf.xml
dfs.replication
mapreduce.job.split.metainfo.maxsize

firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=36.111.140.26 port port=7070 protocol=tcp accept'

firewall-cmd --reload
firewall-cmd --list-all
```



## 10.数据清理以及注意点

1.建立聚合组

2.搭建集群版kylin

kylin.server.mode=all

kylin.server.cluster-servers=cdnlog041.ctyun.net:7070,cdnlog042.ctyun.net:7070,cdnlog031.ctyun.net:7070,cdnlog032.ctyun.net:7070

kylin.job.scheduler.default=2
kylin.job.lock=org.apache.kylin.storage.hbase.util.ZookeeperJobLock

3.定期清理存储

41 1 * * *  /bin/kinit -kt /etc/security/keytabs/kylin.keytab kylin/cdnlog041.ctyun.net
41 13 * * *  /bin/kinit -kt /etc/security/keytabs/kylin.keytab kylin/cdnlog041.ctyun.net
0 1 * * * /data2/apache-kylin-2.6.1-bin-hadoop3/storageClean.sh >> /data2/apache-kylin-2.6.1-bin-hadoop3/storageClean.log
55 12 * * * /bin/python /data2/apache-kylin-2.6.1-bin-hadoop3/bin/KylinExpireJob.py

4.定期清理metadata

```bash
#定时
57 2 */3 * * /bin/bash  /data2/apache-kylin-2.6.1-bin-hadoop3/bin/ctg-clean-kylinmeta.sh  >> /data2/apache-kylin-2.6.1-bin-hadoop3/clean-kylinmeta.log

#删除数据脚本
cat /data2/apache-kylin-2.6.1-bin-hadoop3/bin/ctg-clean-kylinmeta.sh

cd /data2/apache-kylin-2.6.1-bin-hadoop3
./bin/metastore.sh backup
./bin/metastore.sh clean --delete true --jobThreshold 30

last_date=`date -d'65 days ago' +meta_%Y_%m`
cd /data2/apache-kylin-2.6.1-bin-hadoop3/meta_backups
rm -rf /data2/apache-kylin-2.6.1-bin-hadoop3/meta_backups/${last_date}*
```



## 11.最终配置

```java

kylin.metadata.url=kylin:kylin_cdnlog@hbase
kylin.server.mode=all
kylin.server.cluster-servers=cdnlog041.ctyun.net:7070,cdnlog042.ctyun.net:7070,cdnlog031.ctyun.net:7070,cdnlog032.ctyun.net:7070
kylin.web.timezone=GMT+8
kylin.source.hive.database-for-flat-table=kylin
kylin.storage.hbase.table-name-prefix=CDNLOG_
kylin.storage.hbase.namespace=cdnlog_kylin
kylin.storage.hbase.compression-codec=snappy


kylin.engine.spark-conf.spark.master=yarn
kylin.engine.spark-conf.spark.eventLog.enabled=true
kylin.engine.spark-conf.spark.eventLog.dir=hdfs\:///spark2-history
kylin.engine.spark-conf.spark.history.fs.logDirectory=hdfs\:///spark2-history


kylin.job.scheduler.default=2
kylin.job.lock=org.apache.kylin.storage.hbase.util.ZookeeperJobLock




```



## 12.配置CUBE

第一步：

![1567480558119](/img/1567480558119.png)

第二步：

![1567480609411](/img/1567480609411.png)

第三步：

![1567480632513](/img/1567480632513.png)

第四步：

![1567480656216](/img/1567480656216.png)



第五步：



![1567480689716](/img/1567480689716.png)

![1567480719631](/img/1567480719631.png)



![1567480735267](/img/1567480735267.png)

![1567480749449](/img/1567480749449.png)

第六步：




![1567480528560](/img/1567480528560.png)

## 13.Kylin集群版搭建

## 14.修改用户名和密码：

加密密码：BCrypt   KYLIN@123!

```
org.apache.kylin.rest.security.PasswordPlaceholderConfigurer
工程：kylin-server-base

Usage: ${KYLIN_HOME}/bin/kylin.sh org.apache.kylin.rest.security.PasswordPlaceholderConfigurer <EncryptMethod> <your_password>"
```

vi  /data1/apache-kylin-2.6.1-bin-hadoop3/tomcat/webapps/kylin/WEB-INF/classes/kylinSecurity.xml



CDNADMIN/KYLIN@123!

CDNMODELER/MODELER!@123#$%

CDNANALYST/ANALYST@1234@#&

ADMIN/KYLIN@123!

MODELER/MODELER!@123#$%

ANALYST/ANALYST@1234@#&

## 15.Kylin优化建议

- 将必要维度放在开头

- 然后是在过滤 ( where 条件)中起到很大作用的维度

- 如果多个列都会被用于过滤，将高基数的维度（如 user_id）放在低基数的维度（如 age）的前面，这也是基于过滤作用的考虑

- ```bash
  kylin.storage.hbase.min-region-count  5
  kylin.source.hive.redistribute-flat-table  false
  kylin.engine.spark-conf.spark.executor.cores  2
  kylin.engine.spark-conf.spark.yarn.queue kylin
  kylin.engine.spark-conf.spark.executor.instances 40
  kylin.engine.spark-conf.spark.executor.memory 20G
  kylin.storage.hbase.region-cut-gb  3
  kylin.engine.spark.min-partition 20
  kylin.engine.spark-conf.spark.memory.storageFraction 0.3
  kylin.storage.hbase.max-region-count 50
  kylin.engine.spark-conf.spark.executor.extraJavaOptions "-verbose:gc -XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:+PrintGCDateStamps  -XX:+PrintTenuringDistribution"
  ```



## 16.Kylin慢查询 

grep 'Duration:' /data2/apache-kylin-2.6.1-bin-hadoop3/logs/kylin.log |awk '{if($2>2){printf("%s\n",$0);}}'|sort -n -k2,2


grep 'Duration:' /data2/apache-kylin-2.6.1-bin-hadoop3/logs/kylin.log |tail -n 100

grep 'Duration:' /data2/apache-kylin-2.6.1-bin-hadoop3/logs/kylin.log.5 |awk '{if($2>2){printf("%s\n",$0);}}'|sort -n -k2,2|wc -l
grep 'Duration:' /data2/apache-kylin-2.6.1-bin-hadoop3/logs/kylin.log.4 |awk '{if($2>2){printf("%s\n",$0);}}'|sort -n -k2,2|wc -l
grep 'Duration:' /data2/apache-kylin-2.6.1-bin-hadoop3/logs/kylin.log.3 |awk '{if($2>2){printf("%s\n",$0);}}'|sort -n -k2,2|wc -l
grep 'Duration:' /data2/apache-kylin-2.6.1-bin-hadoop3/logs/kylin.log.2 |awk '{if($2>2){printf("%s\n",$0);}}'|sort -n -k2,2|wc -l
grep 'Duration:' /data2/apache-kylin-2.6.1-bin-hadoop3/logs/kylin.log.1 |awk '{if($2>2){printf("%s\n",$0);}}'|sort -n -k2,2|wc -l


tail -n 20 /home/zhangwusheng/kylin.slow.log.31 |awk -F':' '{printf("echo ========\ngrep -b4 \"%s:%s\" %s\n",$2,$3,$1);}' > /home/zhangwusheng/t1.sh ;bash /home/zhangwusheng/t1.sh|more


tail -n 40 /home/zhangwusheng/kylin.slow.log.32 |awk -F':' '{printf("echo ========\ngrep -b4 \"%s:%s\" %s\n",$2,$3,$1);}' > /home/zhangwusheng/t1.sh ;bash /home/zhangwusheng/t1.sh|more


tail -n 20 /home/zhangwusheng/kylin.slow.log.31 |awk -F':' '{printf("echo ========\ngrep -b4 \"%s:%s\" %s\n",$2,$3,$1);}' > /home/zhangwusheng/t1.sh ;bash /home/zhangwusheng/t1.sh|more

tail -n 20 /home/zhangwusheng/kylin.slow.log.31 |awk -F':' '{printf("echo ========\ngrep -b4 \"%s:%s\" %s\n",$2,$3,$1);}' > /home/zhangwusheng/t1.sh ;bash /home/zhangwusheng/t1.sh|more



# 13.集群参数优化

1.参照现有集群

2.spark增加：

spark.driver.extraJavaOptions   -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/data2/core_files/spark-driver-%p.hprof

spark.executor.extraJavaOptions  -XX:+UseNUMA  -XX:OnOutOfMemoryError="rm -f /data2/core_files/spark-%p.hprof ;/usr/local/jdk/bin/jmap -dump:live,format=b,file=/data2/core_files/spark-%p.hprof;kill -9 %p "



3.Hbase优化



 hbase.client.scanner.timeout.period 增加到2分钟
hbase.client.scanner.caching  改成了1000条





# 14.设置集群队列

TODO

# 15.集群打安全补丁

***ambari 2.7.3已经不需要打补丁了***。

```bash
#系统安全

echo 'net.ipv4.tcp_sack = 0' >> /etc/sysctl.conf;sysctl -p

#看这里==============================================
ls /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-*-2.6.7*jar

for ip in `echo 27 28 40 41 42 43 44 45`
do
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar  /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-databind-2.6.7.1.jar.BAK
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-core-2.6.7.jar.BAK
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-annotations-2.6.7.jar.BAK
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-jaxb-annotations-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-module-jaxb-annotations-2.6.7.jar.BAK
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-scala_2.11-2.6.7.1.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-module-scala_2.11-2.6.7.1.jar.BAK
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-dataformat-cbor-2.6.7.jar.BAK
done


#手工上传jackson-dataformat-cbor-2.9.5.jar到目录/usr/hdp/3.0.0.0-1634/spark2/jars

cd /usr/hdp/3.0.0.0-1634/spark2/jars
for ip in `echo 27 28 41 42 43 44 45`
do
	scp /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.9.5.jar 192.168.2.${ip}:/usr/hdp/3.0.0.0-1634/spark2/jars/
done


for ip in `echo 27 28 40 41 42 43 44 45`
do
ssh 192.168.2.${ip} cp /usr/hdp/3.0.0.0-1634/hbase/lib/jackson-module-scala_2.11-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
ssh 192.168.2.${ip} cp /usr/hdp/3.0.0.0-1634/hadoop-yarn/lib/jackson-module-jaxb-annotations-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
ssh 192.168.2.${ip} cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-databind-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
ssh 192.168.2.${ip} cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-annotations-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
ssh 192.168.2.${ip} cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-core-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
done


ls /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-*-2.6.7*jar

#回退:

for ip in `echo 27 28 40 41 42 43 44 45`
do
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-databind-2.6.7.1.jar.BAK  /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-core-2.6.7.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.6.7.jar
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-annotations-2.6.7.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.6.7.jar
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-jaxb-annotations-2.6.7.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-module-jaxb-annotations-2.6.7.jar
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-scala_2.11-2.6.7.1.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-module-scala_2.11-2.6.7.1.jar
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.6.7.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-dataformat-cbor-2.6.7.jar


ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.9.5.jar
ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.9.5.jar
ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.9.5.jar
ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-jaxb-annotations-2.9.5.jar
ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-scala_2.11-2.9.5.jar
ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.9.5.jar

done

```



# 16.用户运行说明

kylin运行在kylin用户下

自己的mr运行在cdnlog用户下



# 17.kafka权限

***备注：Ambari对于kafka的支持就是一坨屎，很多配置必须手工确认！***

## 1.安装和配置

- 创建全新的Kafka环境

```
NEW_ZK_DIR="kafka-test-auth3"
/usr/hdp/current/zookeeper-client/bin/zkCli.sh -server ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181 create /${NEW_ZK_DIR} "data-of-${NEW_ZK_DIR}"
```



> 注意：
>
> kafka的安全不是使用的kerberos，一定要先kdestroy！否则会出现莫名其妙的问题！
>
> 比如kafka-console-consumer不能读取数据！

- 修改Kafka配置：

| 字段名                               | 字段值                                    |
| ------------------------------------ | ----------------------------------------- |
| zookeeper.connect                    | XXX:12181/kafka-auth-test-1  使用新的zk值 |
| listeners                            | SASL_PLAINTEXT://localhost:6667           |
| sasl.enabled.mechanisms              | PLAIN                                     |
| sasl.mechanism.inter.broker.protocol | PLAIN                                     |
| security.inter.broker.protocol       | SASL_PLAINTEXT                            |
| super.users                          | User:admin                                |

- kafka_jaas.conf

```bash
#如果没有启用kerberos，只要这一段就行了
KafkaServer {
org.apache.kafka.common.security.plain.PlainLoginModule required
username="admin"
password="admin-sec"
user_admin="admin-sec"
user_producer="prod-sec"
user_consumer="cons-sec";
};
#如果启用了kerberos，必须包含下面两段，这个是使用kerberos连接zk用的
Client {
com.sun.security.auth.module.Krb5LoginModule required
useKeyTab=true
keyTab="{{kafka_keytab_path}}"
storeKey=true
useTicketCache=false
serviceName="zookeeper"
principal="{{kafka_jaas_principal}}";
};

com.sun.security.jgss.krb5.initiate {
com.sun.security.auth.module.Krb5LoginModule required
renewTGT=false
doNotPrompt=true
useKeyTab=true
keyTab="{{kafka_keytab_path}}"
storeKey=true
useTicketCache=false
serviceName="{{kafka_bare_jaas_principal}}"
principal="{{kafka_jaas_principal}}";
};



--------------------------------------------------------------------------

 /**
        * Example of SASL/PLAIN Configuration
        *
        * KafkaServer {
        *   org.apache.kafka.common.security.plain.PlainLoginModule required
        *   username="admin"
        *   password="admin-secret"
        *   user_admin="admin-secret"
        *   user_alice="alice-secret";
        *   };
        *
        * Example of SASL/SCRAM
        *
        * KafkaServer {
        *   org.apache.kafka.common.security.scram.ScramLoginModule required
        *   username="admin"
        *   password="admin-secret"
        *   };
        *
        * Example of Enabling multiple SASL mechanisms in a broker:
        *
        *   KafkaServer {
        *
        *    com.sun.security.auth.module.Krb5LoginModule required
        *    useKeyTab=true
        *    storeKey=true
        *    keyTab="/etc/security/keytabs/kafka_server.keytab"
        *    principal="kafka/kafka1.hostname.com@EXAMPLE.COM";
        *
        *    org.apache.kafka.common.security.plain.PlainLoginModule required
        *    username="admin"
        *    password="admin-secret"
        *    user_admin="admin-secret"
        *    user_alice="alice-secret";
        *
        *    org.apache.kafka.common.security.scram.ScramLoginModule required
        *    username="scram-admin"
        *    password="scram-admin-secret";
        *    };
        *
        **/

        {% if kerberos_security_enabled %}

      KafkaServer {
            org.apache.kafka.common.security.plain.PlainLoginModule required
            username="admin"
            password="CtYiofnwk@269Mn"
            user_admin="CtYiofnwk@269Mn"
            user_huaweiYun="C#huaTwei2Y4Gun"
            user_cache_access="TcacGhe2@acCcess"
            user_youpuYun="GYunCTyou10@p#u"
            user_haohanYun="GCTha12o#hyun"
            user_baishanYun="CbaTishGan3@Y#un"
            user_cdnlog="QwtB+SRLaiZOXysjcapN"
            user_jicheng="kzptJziTtex6qo7Y"
            user_axetask="Es68Kuh6elJugj1c"
            user_ossNginx="yY0I3Mq#xZC@yHOH"
            user_elkmetricsdocker="2Hlk0jVrmRGZIPTl"
            user_DebugTopic="ThisisTheDebugUser147@201907";
        };

        KafkaClient {
        com.sun.security.auth.module.Krb5LoginModule required
        useTicketCache=true
        renewTicket=true
        serviceName="{{kafka_bare_jaas_principal}}";
        };
        Client {
        com.sun.security.auth.module.Krb5LoginModule required
        useKeyTab=true
        keyTab="{{kafka_keytab_path}}"
        storeKey=true
        useTicketCache=false
        serviceName="zookeeper"
        principal="{{kafka_jaas_principal}}";
        };
        com.sun.security.jgss.krb5.initiate {
        com.sun.security.auth.module.Krb5LoginModule required
        renewTGT=false
        doNotPrompt=true
        useKeyTab=true
        keyTab="{{kafka_keytab_path}}"
        storeKey=true
        useTicketCache=false
        serviceName="{{kafka_bare_jaas_principal}}"
        principal="{{kafka_jaas_principal}}";
        };

        {% endif %}
```

- kafka_client_jaas.conf  for producer

```bash
KafkaClient {
org.apache.kafka.common.security.plain.PlainLoginModule required
username="producer"
password="prod-sec" ;
};
```

- kafka_client_jaas_conf for consumer

```bash
KafkaClient {
org.apache.kafka.common.security.plain.PlainLoginModule required
username="consumer"
password="cons-sec";
};
```

- cat consumer.properties

```bash
secutiry.protocol=SASL_PLAINTEXT
sasl.mechanism=PLAIN
group.id=zws-test-grp1
```

- 创建新的Topic测试

```bash
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1


#创建Topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1  --topic zwstestnew2    --partitions 1 --replication-factor 1

#查看创建的Topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --describe --zookeeper ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1   --topic zwstestnew2

#Topic授权，注意这里最好使用--producer，不要使用--operation Write
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --add --allow-principal User:producer --topic zwstestnew2  --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --list  --topic zwstestnew2

#修改好kafka_client_jaas_conf ，注意使用 --security-protocol，而不是网上的producer-property，那样不行
/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667  --topic zwstestnew2 --security-protocol=SASL_PLAINTEXT --producer-property sasl.mechanism=PLAIN

#修改好consumer的kafka_client_jaas_conf，然后修改好consumer.properties
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667  --topic zwstestnew2 --security-protocol=SASL_PLAINTEXT --from-beginning --consumer.config ./consumer.properties --new-consumer

#想要读取，必须经过授权！
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1  --add --allow-principal User:consumer --topic zwstestnew2  --consumer --group zws-test-grp1
```



代码：

jvm启动参数

-Djava.security.auth.login.config=/usr/hdp/current/kafka-broker/conf/kafka_client_jaas.conf

 props.put("security.protocol", "SASL_PLAINTEXT");
        props.put("sasl.kerberos.service.name", "kafka");
        props.put("sasl.mechanism", "PLAIN");



#新增用户：



| 用户名       | 密码             | 说明   |
| ------------ | ---------------- | ------ |
| huaweiYun    | C#huaTwei2Y4Gun  | 华为云 |
| cache_access | TcacGhe2@acCcess | 自研   |
| youpuYun     | GYunCTyou10@p#u  | 有谱   |
| haohanYun    | GCTha12o#hyun    | 浩瀚   |
| baishanYun   | CbaTishGan3@Y#un | 白山   |
|              |                  |        |
|              |                  |        |
|              |                  |        |

KafkaServer {
org.apache.kafka.common.security.plain.PlainLoginModule required
username="admin"
password="CtYiofnwk@269Mn"
user_admin="CtYiofnwk@269Mn"
user_huaweiYun="C#huaTwei2Y4Gun"
user_cache_access="TcacGhe2@acCcess"
user_youpuYun="GYunCTyou10@p#u"
user_haohanYun="GCTha12o#hyun"
user_baishanYun="CbaTishGan3@Y#un";
};

```bash
华为云：

topicName=huaweiYun

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1  --topic ${topicName}    --partitions 40 --replication-factor 3

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --add --allow-principal User:${topicName} --topic ${topicName}   --producer

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1  --add --allow-principal User:${topicName} --topic ${topicName}   --consumer --group grp-${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --list  --topic ${topicName}

#自研
topicName=cache_access
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1  --topic ${topicName}    --partitions 20 --replication-factor 3

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --add --allow-principal User:${topicName} --topic ${topicName}   --producer

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1  --add --allow-principal User:${topicName} --topic ${topicName}   --consumer --group grp-${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --list  --topic ${topicName}

#友普
topicName=youpuYun
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1  --topic ${topicName}    --partitions 10 --replication-factor 3

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --add --allow-principal User:${topicName} --topic ${topicName}   --producer

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1  --add --allow-principal User:${topicName} --topic ${topicName}   --consumer --group grp-${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --list  --topic ${topicName}
#浩瀚云
topicName=haohanYun
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1  --topic ${topicName}    --partitions 10 --replication-factor 3

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --add --allow-principal User:${topicName} --topic ${topicName}   --producer

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1  --add --allow-principal User:${topicName} --topic ${topicName}   --consumer --group grp-${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --list  --topic ${topicName}

#白山云
topicName=baishanYun
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1  --topic ${topicName}    --partitions 10 --replication-factor 3

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --add --allow-principal User:${topicName} --topic ${topicName}   --producer

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1  --add --allow-principal User:${topicName} --topic ${topicName}   --consumer --group grp-${topicName}


/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:6667  --topic ctYun --producer-property security.protocol=SASL_PLAINTEXT --producer-property sasl.mechanism=PLAIN

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --list  --topic ctYun

#调试
topicName="ctYun_MidLevel"
userName="cache_access"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --alter --zookeeper ${ZK_CONN} --topic ctYun --partitions 21

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 1 --replication-factor 3
#授权可写
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic ${topicName}   --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}
#授权可读
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${userName} --topic ${topicName}   --consumer --group grp-${userName}

/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list cdnlog003.ctyun.net:5044  --topic DebugTopic --producer-property security.protocol=SASL_PLAINTEXT --producer-property sasl.mechanism=PLAIN

#修改好consumer的kafka_client_jaas_conf，然后修改好consumer.properties
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server cdnlog003.ctyun.net:5044  --topic DebugTopic --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-DebugTopic  --consumer.config ./consumer.properties


------------------------------------------------------------------开发

topicName=Kafka_Rest_Test2
userName="DebugTopic"
ZK_CONN="ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 1 --replication-factor 3

##修改分区数量
./kafka-topics.sh --alter --zookeeper ${ZK_CONN} --topic ctYun --partitions 30

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic ${topicName}   --producer


/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667   --topic ${topicName} --producer-property security.protocol=SASL_PLAINTEXT --producer-property sasl.mechanism=PLAIN

/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667    --topic ${topicName} --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-${topicName} --consumer.config /usr/hdp/3.1.0.0-78/kafka/consumer-kafka-rest.properties

cat consumer-test.properties
secutiry.protocol=SASL_PLAINTEXT
sasl.mechanism=PLAIN
group.id=logstash

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${userName} --topic ${topicName}   --consumer --group grp-${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:DebugTopic --topic ${topicName}   --consumer --group grp-${topicName}

```

- Kafka重新分配分区（测试中）:


```bash

/usr/hdp/current/kafka-broker/bin/kafka-reassign-partitions.sh  --zookeeper ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181/kafka-auth-test-1 --topics-to-move-json-file ./topics-to-move.json --broker-list 1001,1002,1003 --generate

topicName=KafkaRestTest2
userName="zwstestnew2"
ZK_CONN="ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1"



/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions ${PART_NUM} --replication-factor 3

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --describe --zookeeper ${ZK_CONN} --topic ${topicName}

#--bootstrap-server ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667
```

- Kafka网络日志配置（测试中）CLOSE_WAIT过高：

```bash
#added zws,log reomte ip address
log4j.appender.networkAcceptAppender=org.apache.log4j.DailyRollingFileAppender
log4j.appender.networkAcceptAppender.DatePattern='.'yyyy-MM-dd-HH
log4j.appender.networkAcceptAppender.File=${kafka.logs.dir}/network-accept.log
log4j.appender.networkAcceptAppender.layout=org.apache.log4j.PatternLayout
log4j.appender.networkAcceptAppender.layout.ConversionPattern=[%d{ISO8601}][%L] %p %m (%c)%n

log4j.logger.kafka.network.Acceptor=DEBUG,networkAcceptAppender
log4j.logger.kafka.network.AbstractServerThread=DEBUG,networkAcceptAppender
log4j.additivity.kafka.network.Acceptor=false
log4j.additivity.kafka.network.AbstractServerThread=false


#查看网络连接
for ip in `echo 3 4 13 14 23 24 33 34 43 44`; do echo "192.168.254.${ip}"; ssh -p 9000 192.168.254.${ip}  grep -v 192.168 /var/log/kafka/network-accept.log |awk '{print $7;}'|awk -F':' '{arrr[$1]++;}END{for (ip in arrr){print ip"->"arrr[ip]};}'|grep /49 ; done


#todo：
0:只使用ipv4，已经修改过了
1.修改操作系统参数
https://blog.csdn.net/hellozhxy/article/details/90030332
2.修改/etc/resolv.conf
3.已经修改了num.network.threads，从24改到了100

```



## 2.生产添加Topic

```bash
#添加阿里云
topicName="aliYun"
userName="aliYun"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
PART_NUM=10
#添加阿里云直播
topicName="aliYun_live"
userName="aliYun"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
PART_NUM=5
#压测
topicName="CdnPerfTest-LZ4"
userName="DebugTopic"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
PART_NUM=80
#浩瀚补数
topicName="haohanRedo"
userName="haohanRedo"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
PART_NUM=80
#自研父层日志2020-02-24
topicName="ctYun_MidLevel"
userName="cache_access"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
PART_NUM=5
#自研父层日志2020-02-24
topicName="ctYun_MidLevel_live"
userName="cache_access"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
PART_NUM=2
#浩瀚父层日志2020-02-24
topicName="haohanYun_MidLevel"
userName="haohanYun"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
PART_NUM=3
#浩瀚父层日志2020-02-24
topicName="haohanYun_MidLevel_live"
userName="haohanYun"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
PART_NUM=1



/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions ${PART_NUM} --replication-factor 3
#授权可写
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic ${topicName}   --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}
#授权可读
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${userName} --topic ${topicName}   --consumer --group grp-${userName}

/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list cdnlog003.ctyun.net:5044  --topic DebugTopic --producer-property security.protocol=SASL_PLAINTEXT --producer-property sasl.mechanism=PLAIN

#修改好consumer的kafka_client_jaas_conf，然后修改好consumer.properties
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server cdnlog003.ctyun.net:5044  --topic CdnPerfTest-LZ4 --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-DebugTopic  --consumer.config ./consumer.properties


topicName=KafkaRestTest2
userName="DebugTopic"
ZK_CONN="ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --alter --zookeeper ${ZK_CONN} --topic ctYun --partitions ${PART_NUM}


#压测Topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --alter --zookeeper ${ZK_CONN} --topic ${topicName} --partitions 80

#2020-03-05
1.存储/点播-容量---- oss-vod-capacity
2.点播-转码        ---- oss-vod-transcode
3.直播-流量        -----oss-live-flow
4.直播-转码       ------oss-live-transcode
5.直播-API调用 ------oss-live-api
6.直播-流数量 ------   oss-live-flowcount
topicName="haohanYun_MidLevel_live"
userName="haohanYun"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
PART_NUM=1


```

## 3.防火墙开通

- 范日明

```bash
firewall-cmd --reload
firewall-cmd --list-all

#125.88.39.158，125.88.39.159，125.88.39.167
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="125.88.39.158" port port="6667" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="125.88.39.159" port port="6667" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="125.88.39.167" port port="6667" protocol="tcp" accept'
firewall-cmd --reload
firewall-cmd --list-all



rule family="ipv4" port port="161" protocol="udp" accept
```

## 4.查看消费者组

```bash
export KAFKA_OPTS=" -Djava.security.auth.login.config=/home/zhangwusheng/zws_jaas.conf"

/usr/hdp/current/kafka-broker/bin/kafka-consumer-groups.sh --bootstrap-server ctl-nm-hhht-yxxya6-ceph-011.ctyuncdn.net:6667 --describe --group edge_computing_log --command-config /usr/hdp/current/kafka-broker/config/consumer.properties
```

## 5.删除Topic

```bash
userName="DebugTopic"
ZK_CONN="ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1"
/usr/hdp/current/kafka-broker/bin/kafka-topics  --delete --zookeeper ${ZK_CONN}  --topic Kafka_Rest_Test2



/usr/hdp/current/kafka-broker/bin/kafka-configs.sh  --zookeeper cdnlog036.ctyun.net:12181/cdnlog-first --entity-type topics  --entity-name ctYun --describe


/usr/hdp/current/kafka-broker/bin/kafka-configs.sh  --zookeeper cdnlog036.ctyun.net:12181/cdnlog-first --entity-type topics  --entity-name ctYun_agg_shanghai --describe

```

## 6.Topic级别配置修改

- 开发环境

```bash

#看看有没有单独的配置

#开发broker对应关系
1001 	ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net
1003 	ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net
1004 	ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net
1005 	ctl-nm-hhht-yxxya6-ceph-011.ctyuncdn.net
1006 	ctl-nm-hhht-yxxya6-ceph-012.ctyuncdn.net
1007 	ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net

/usr/hdp/current/kafka-broker/bin/kafka-configs.sh --zookeeper 192.168.2.27:12181/kafka-auth-test-1 --describe --entity-type topics --entity-name ctYun

#调整topic过期时间：
#开发环境
/usr/hdp/current/kafka-broker/bin/kafka-configs.sh --zookeeper 192.168.2.27:12181/kafka-auth-test-1  --entity-type topics --entity-name ctYun  --alter --add-config retention.ms=172800000


#调整topic参数（设置topic可以从不同步的副本选择leader！！慎用）：
/usr/hdp/current/kafka-broker/bin/kafka-configs.sh  --zookeeper cdnlog036.ctyun.net:12181/cdnlog-first --entity-type topics  --entity-name ambari_kafka_service_check  --alter --add-config unclean.leader.election.enable=true

# 查看分区分布情况
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --describe --zookeeper 192.168.2.27:12181/kafka-auth-test-1 --topic cdn-fee-flow-increment

#生成重新分区的数据
/usr/hdp/current/kafka-broker/bin/kafka-reassign-partitions.sh --zookeeper 192.168.2.27:12181/kafka-auth-test-1 --generate --topics-to-move-json-file /home/zhangwusheng/scripts/kafka-reassign.txt --broker-list 1001,1003,1004,1005,1006,1007

cat /home/zhangwusheng/scripts/kafka-reassign.txt
echo
{
     "topics":[
                {
                        "topic":"ctYun"
                }
        ],
     "version":1
}

Current partition replica assignment
{"version":1,"partitions":[{"topic":"ctYun-dev","partition":2,"replicas":[1007,1003,1005],"log_dirs":["any","any","any"]},{"topic":"ctYun-dev","partition":1,"replicas":[1006,1003,1005],"log_dirs":["any","any","any"]},{"topic":"ctYun-dev","partition":0,"replicas":[1005,1003,1006],"log_dirs":["any","any","any"]}]}

Proposed partition reassignment configuration
{"version":1,"partitions":[{"topic":"ctYun-dev","partition":0,"replicas":[1004,1003,1005],"log_dirs":["any","any","any"]},{"topic":"ctYun-dev","partition":2,"replicas":[1006,1003,1004],"log_dirs":["any","any","any"]},{"topic":"ctYun-dev","partition":1,"replicas":[1005,1003,1004],"log_dirs":["any","any","any"]}]}




```



生产环境

```bash

#生产broker对应关系
1001 	cdnlog003.ctyun.net
1002 	cdnlog004.ctyun.net
1012 	cdnlog043.ctyun.net
1013 	cdnlog044.ctyun.net
1014 	cdnlog023.ctyun.net
1015 	cdnlog014.ctyun.net
1016 	cdnlog033.ctyun.net
1017 	cdnlog024.ctyun.net
1018 	cdnlog034.ctyun.net
1019 	cdnlog013.ctyun.net

/usr/hdp/current/kafka-broker/bin/kafka-configs.sh --zookeeper cdnlog036.ctyun.net:12181/cdnlog-first --describe --entity-type topics --entity-name huaweiYun

/usr/hdp/current/kafka-broker/bin/kafka-configs.sh  --zookeeper cdnlog036.ctyun.net:12181/cdnlog-first --entity-type topics  --entity-name ctYun  --alter --add-config retention.ms=172800000

/usr/hdp/current/kafka-broker/bin/kafka-configs.sh  --zookeeper cdnlog036.ctyun.net:12181/cdnlog-first --entity-type topics  --entity-name elk-metrics --alter --delete-config retention.ms

cat > /home/zhangwusheng/scripts/kafka-reassign.txt<<EOF
{
     "topics":[
                {
                        "topic":"huaweiYun"
                }
        ],
     "version":1
}
EOF

/usr/hdp/current/kafka-broker/bin/kafka-reassign-partitions.sh --zookeeper cdnlog036.ctyun.net:12181/cdnlog-first --generate --topics-to-move-json-file /home/zhangwusheng/scripts/kafka-reassign.txt --broker-list 1001,1002,1012,1013,1014,1015,1016,1017,1018,1019


/usr/hdp/current/kafka-broker/bin/kafka-reassign-partitions.sh --zookeeper cdnlog036.ctyun.net:12181/cdnlog-first --bootstrap-server cdnlog003.ctyun.net:5044,cdnlog004.ctyun.net:5044 --execute --reassignment-json-file /home/zhangwusheng/scripts/kafka-reassign-youpuYun.json

/usr/hdp/current/kafka-broker/bin/kafka-reassign-partitions.sh --zookeeper cdnlog036.ctyun.net:12181/cdnlog-first  --verify --reassignment-json-file /home/zhangwusheng/scripts/kafka-reassign-youpuYun.json


#查看偏移量：
/usr/hdp/current/kafka-broker/bin/kafka-consumer-groups-acls.sh --command-config  /usr/hdp/current/kafka-broker/config/consumer_lizw.properties --bootstrap-server  cdnlog003.ctyun.net:5044 --group ctYun-realtime-bilibili --describe

#平衡leader：
bin/kafka-preferred-replica-election.sh --zookeeper zk_host:port/chroot

#不限group消费授权：
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=192.168.254.36:12181/cdnlog-first --add --allow-principal User:edge_computing --consumer --topic evm-billing-out-bandwidth     --group '*'


```

## 7.压测



```bash
/usr/hdp/current/kafka-broker/bin/kafka-producer-perf-test.sh  --topic rsyslog-dev-30   --throughput 500000 --num-records 10000000 --record-size 1000 --producer-props bootstrap.servers=SASL_PLAINTEXT://ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667  security.protocol=SASL_PLAINTEXT   sasl.mechanism=PLAIN


/usr/hdp/current/kafka-broker/bin/kafka-configs.sh --zookeeper 192.168.2.27:12181/kafka-auth-test-1  --entity-type topics --entity-name CapTest  --alter --add-config retention.ms=7200000

/usr/hdp/current/kafka-broker/bin/kafka-configs.sh --zookeeper 192.168.2.27:12181/kafka-auth-test-1  --entity-type topics --entity-name rsyslog-dev-30  --alter --add-config retention.ms=7200000

结论
1. 10个分区，1000字节，20W每秒，2000个字节，10W每秒
2. 30个分区，1000字节，40W每秒，2000个字节，20W每秒
3.
```



## 8.__consumer_offsets

```bash
https://support.huaweicloud.com/intl/en-us/trouble-mrs/mrs_03_0202.html
exclude.internal.topics = false

kafka-console-consumer.sh --topic __consumer_offsets --zookeeper 10.5.144.2:2181/kafka --formatter "kafka.coordinator.group.GroupMetadataManager\$OffsetsMessageFormatter" --consumer.config ../config/consumer.properties --from-beginning


GetOffsetShell kafka-run-class kafka.tools.GetOffsetShell  --broker-list $  kafka-console-consumer is a consumer command line that: read data from a Kafka topic and write it to standard output (console). Articles Related Example Command line Print key and value kafka-console-consumer.sh \ --bootstrap-server localhost:9092 \ --topic mytopic \ --from-beginning \ --formatter kafka.tools.DefaultMessageFormatter \ --property print.key=true \ --property print.value=true
```





# 18.KafkaManager

1.下载

https://github.com/yahoo/kafka-manager/releases

2.解压

cd  /c/Work/Source/kafka-manager-2.0.0.2

./sbt dist

生成配置包

3.配置application.conf的zk

kafka-manager.zkhosts="ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181/kafka-manager"

zk上需要建立/kafka-manager目录

4.启动

```
nohup /data2/kafka-manager-2.0.0.2/bin/kafka-manager -Dconfig.file=/data2/kafka-manager-2.0.0.2/conf/application.conf -Dhttp.port=19090  -Dapplication.home=/data2/kafka-manager/kafka-manager-2.0.0.2 &

生产系统：

nohup /data2/kafka-manager/kafka-manager-2.0.0.2/bin/kafka-manager -Dconfig.file=/data2/kafka-manager/kafka-manager-2.0.0.2/conf/application.conf -Dhttp.port=19090  -Dapplication.home=/data2/kafka-manager/kafka-manager-2.0.0.2 &


/usr/local/kafkamanager/bin/kafka-manager -Dconfig.file=/usr/local/kafkamanager/conf/application.conf -Dhttp.port=29090  -Dapplication.home=/usr/local/kafkamanager/


#抓取数据
cd /home/zhangwusheng/var/lib

curl 'http://sct-gz-guiyang1-loganalysis-09.in.ctcdn.cn:29090/clusters/hdfs-cdnlog_guizhou/topics/ctYun' -o guizhou_km.txt
dd=`date +%Y%m%d-%H%M`
grep -A 12 'Messages in /sec' guizhou_km.txt|grep badge|awk -F'>' '{print $2;}'|awk -F'<' '{print $1;}'  | awk -v dd=${dd} 'BEGIN { ORS = " " ;print dd; } { print }END{printf("\n");}' >> guizhou_km.stat.txt
echo '' >> guizhou_km.stat.txt 

one line 

curl 'http://sct-gz-guiyang1-loganalysis-09.in.ctcdn.cn:29090/clusters/hdfs-cdnlog_guizhou/topics/ctYun' |grep -A 12 'Messages in /sec' |grep badge|awk -F'>' '{print $2;}'|awk -F'<' '{print $1;}'  | awk -v dd="`date +%Y%m%d-%H%M`" 'BEGIN { ORS = " " ;print dd; } { print }END{printf("\n");}' >> guizhou_km.stat.txt
```

5.新增配置；

zookeeper hosts：

cdnlog041.ctyun.net:12181,cdnlog042.ctyun.net:12181/cdnlog-first

version: 2.0.0

Security Protocol: SASL_PLAINTEXT

SASL Mechanism :PLAIN

SASL JAAS Config:org.apache.kafka.common.security.plain.PlainLoginModule required  username="admin" password="CtYiofnwk@269Mn" ;



```
Security Protocol:SASL_PLAINTEXT
SASL Mechanism:PLAIN

JAAS:
KafkaClient { org.apache.kafka.common.security.plain.PlainLoginModule required  username="admin" password="admin-sec" ; };
```



## Kafka连接排查

```bash

netstat -anp|grep 5044|grep -v 192.168.254|awk '{print $5;}'|awk -F':' '{print $1;}'|sort |uniq -c|sort -n -k1,1 > /home/zhangwusheng/ip.kafka.20201208

#统计外网连接清单
netstat -anp|grep 5044|grep -v 192.168.254|awk '{print $5;}'|awk -F':' '{print $1;}'|sort |uniq -c|sort -n -k1,1 > /home/zhangwusheng/kafka.${HOSTNAME}.`date +%Y%m%d`.txt

#统计每个连接的总机器数
netstat -anp|grep 5044|grep -v 192.168.254|awk '{print $5;}'|awk -F':' '{print $1;}'|sort |uniq -c|sort -n -k1,1|awk '{a[$1]++;}END{for(i in a){printf("%d = %d\n",i,a[i]);}}'|sort -n -k1,1

```



#CMAK
下载cmak-3.0.0.5，安装jdk 11，sbt dist
#对zk版本有要求，低版本的要先建立

create /cmak-first ""
create /cmak-first/kafka-manager ""
create /cmak-first/kafka-manager/mutex ""
create /cmak-first/kafka-manager/mutex/leases ""
create /cmak-first/kafka-manager/mutex/locks ""

 cat consumer.properties
security.protocol=SASL_PLAINTEXT
sasl.mechanism=PLAIN

application.conf
修改zk的连接

https://github.com/yahoo/CMAK/issues/748
需要修改zk的依赖版本，因为他依赖的curator版本比较高，zk也比较高

增加kafka-jaas.conf
KafkaClient {
        org.apache.kafka.common.security.plain.PlainLoginModule required
        username="admin"
        password="admin-sec";
};

 /home/zhangwusheng/soft/cmak-3.0.0.5/bin/cmak
 最开始增加
export JAVA_HOME=/home/zhangwusheng/soft/cmak-3.0.0.5/jdk-11.0.11
export PATH=$JAVA_HOME/bin:$PATH


/home/zhangwusheng/soft/cmak-3.0.0.5/bin/cmak -Dconfig.file=/home/zhangwusheng/soft/cmak-3.0.0.5/conf/application.conf -Dhttp.port=39090 -Djava.security.auth.login.config=/home/zhangwusheng/soft/cmak-3.0.0.5/conf/kafka-jaas.conf -Dapplication.home=/home/zhangwusheng/soft/cmak-3.0.0.5
# 19.Kafaka配置

broker端：

| 参数名                          | 参数含义                                                     | 默认值 | 建议值               |
| ------------------------------- | ------------------------------------------------------------ | ------ | -------------------- |
| auto.create.topics.enable       | Enable auto creation of topic on the server                  | true   | false                |
| background.threads              | The number of threads to use for various background processing tasks | 10     |                      |
| delete.topic.enable             | Enables delete topic. Delete topic through the admin tool will have no effect if this config is turned off | true   | false                |
| log.dirs                        | The directories in which the log data is kept. If not set, the value in log.dir is used |        |                      |
| log.retention.hours             | The number of hours to keep a log file before deleting it (in hours), tertiary to log.retention.ms property | 168    |                      |
| num.io.threads                  | The number of threads that the server uses for processing requests, which may include disk I/O | 8      |                      |
| num.network.threads             | The number of threads that the server uses for receiving requests from the network and sending responses to the network | 3      |                      |
| num.replica.fetchers            | Number  of fetcher threads used to replicate messages from a source broker.  Increasing this value can increase the degree of I/O parallelism in the  follower broker. | 1      |                      |
| socket.receive.buffer.bytes     | The SO_RCVBUF buffer of the socket server sockets. If the value is -1, the OS default will be used. | 102400 |                      |
| socket.send.buffer.bytes        | The SO_SNDBUF buffer of the socket server sockets. If the value is -1, the OS default will be used. | 102400 |                      |
| zookeeper.connection.timeout.ms | The  max time that the client waits to establish a connection to zookeeper.  If not set, the value in zookeeper.session.timeout.ms is used |        |                      |
| zookeeper.session.timeout.ms    | Zookeeper session timeout                                    | 6000   | 适当调大一些         |
| zookeeper.connect               |                                                              |        | 配置单独的zk命名空间 |
| listeners                       |                                                              |        | 配置SASL             |
| Ambari Advanced kafka_jaas_conf |                                                              |        | 配置SASL             |
| super.users                     |                                                              |        | 配置正确的admin用户  |



- KafkaRack相关以及同时配置内外网：

advertised.listeners=SASL_PLAINTEXT://cdnlog013.ctyun.net:5044

listeners=SASL_PLAINTEXT://0.0.0.0:5044



- 首先生成rack脚本

cp /etc/hadoop/3.1.0.0-78/0/topology_script.py  /usr/hdp/current/kafka-broker/conf/kafka-topology_script.py

cp /etc/hadoop/3.1.0.0-78/0/topology_mappings.data  /usr/hdp/current/kafka-broker/conf/kafka_topology_mappings.data

- 其次，生成rack数据

编辑topology_mappings.data为自己想要的内容

```bash
[network_topology]
cdnlog042.ctyun.net=/rack-e15
192.168.254.42=/rack-e15
cdnlog041.ctyun.net=/rack-e15
192.168.254.41=/rack-e15
cdnlog005.ctyun.net=/rack-d01
192.168.254.5=/rack-d01
cdnlog003.ctyun.net=/rack-d01
192.168.254.3=/rack-d01
cdnlog004.ctyun.net=/rack-d01
192.168.254.4=/rack-d01
cdnlog009.ctyun.net=/rack-d01
192.168.254.9=/rack-d01
cdnlog007.ctyun.net=/rack-d01
192.168.254.7=/rack-d01
cdnlog008.ctyun.net=/rack-d01
192.168.254.8=/rack-d01
cdnlog006.ctyun.net=/rack-d01
192.168.254.6=/rack-d01
cdnlog017.ctyun.net=/rack-d02
192.168.254.17=/rack-d02
cdnlog015.ctyun.net=/rack-d02
192.168.254.15=/rack-d02
cdnlog013.ctyun.net=/rack-d02
192.168.254.13=/rack-d02
cdnlog016.ctyun.net=/rack-d02
192.168.254.16=/rack-d02
cdnlog012.ctyun.net=/rack-d02
192.168.254.12=/rack-d02
cdnlog018.ctyun.net=/rack-d02
192.168.254.18=/rack-d02
cdnlog014.ctyun.net=/rack-d02
192.168.254.14=/rack-d02
cdnlog026.ctyun.net=/rack-d20
192.168.254.26=/rack-d20
cdnlog021.ctyun.net=/rack-d20
192.168.254.21=/rack-d20
cdnlog023.ctyun.net=/rack-d20
192.168.254.23=/rack-d20
cdnlog024.ctyun.net=/rack-d20
192.168.254.24=/rack-d20
cdnlog025.ctyun.net=/rack-d20
192.168.254.25=/rack-d20
cdnlog022.ctyun.net=/rack-d20
192.168.254.22=/rack-d20
cdnlog027.ctyun.net=/rack-d20
192.168.254.27=/rack-d20
cdnlog034.ctyun.net=/rack-d21
192.168.254.34=/rack-d21
cdnlog031.ctyun.net=/rack-d21
192.168.254.31=/rack-d21
cdnlog030.ctyun.net=/rack-d21
192.168.254.30=/rack-d21
cdnlog032.ctyun.net=/rack-d21
192.168.254.32=/rack-d21
cdnlog035.ctyun.net=/rack-d21
192.168.254.35=/rack-d21
cdnlog033.ctyun.net=/rack-d21
192.168.254.33=/rack-d21
cdnlog046.ctyun.net=/rack-e16
192.168.254.46=/rack-e16
cdnlog045.ctyun.net=/rack-e15
192.168.254.45=/rack-e15
cdnlog047.ctyun.net=/rack-e16
192.168.254.47=/rack-e16
cdnlog049.ctyun.net=/rack-e16
192.168.254.49=/rack-e16
cdnlog050.ctyun.net=/rack-e16
192.168.254.50=/rack-e16
cdnlog048.ctyun.net=/rack-e16
192.168.254.48=/rack-e16
cdnlog043.ctyun.net=/rack-e15
192.168.254.43=/rack-e15
cdnlog044.ctyun.net=/rack-e15
```

- 第三，生成脚本,并且scp过去


ctg-kafka-rack.sh的内容为：

```bash
#!/bin/bash

CTG_KAFKA_HOST=`/bin/hostname`
MYDIR=`dirname $0`
CTG_KAFKA_RACK=`/bin/python ${MYDIR}/../config/kafka-topology_script.py ${CTG_KAFKA_HOST} 2>/dev/null |awk -F'/' '{print $2;}'`

if [ -z "${CTG_KAFKA_RACK}" ]
then
    CTG_KAFKA_RACK="CTG-DEFAULT"
fi
export KAFKA_RACK=${CTG_KAFKA_RACK}

DIRBASE=`dirname $0`
#MYDIR=$(cd $DIRBASE && pwd -P)
echo "MYDIR=${MYDIR}"
if [ -f ${MYDIR}/../config/server.properties ]
then
      grep 'broker.rack'  ${MYDIR}/../config/server.properties
      if [ $? == 0 ]
      then
             /bin/sed -i "s#broker\.rack=.*\$#broker\.rack=$KAFKA_RACK#g"     ${MYDIR}/../config/server.properties
      else
            echo "broker.rack=${KAFKA_RACK}" >>${MYDIR}/../config/server.properties
      fi

          grep 'advertised.listeners'  ${MYDIR}/../config/server.properties
          if [ $? == 0 ]
      then
                        #advertised.listeners=SASL_PLAINTEXT://0.0.0.0:5044
             /bin/sed -i "s#advertised\.listeners=\(.*\)://\(.*\):\(.*\)#advertised\.listeners=\\1://${CTG_KAFKA_HOST}:\\3#g"     ${MYDIR}/../config/server.properties
      else
            myport=`grep "listeners" ${MYDIR}/../config/server.properties |/bin/awk -F':' '{print $3;}'|sort -u`
            muprot=`grep listeners ${MYDIR}/../config/server.properties |/bin/awk -F'=' '{print $2;}'|/bin/awk -F':' '{print $1;}'|sort -u`
            echo "advertised.listeners=${muprot}://${CTG_KAFKA_HOST}:${myport}" >>${MYDIR}/../config/server.properties
      fi
fi
```

- 最后，修改脚本kafka-run-class.sh

vi kafka-run-class.sh

最后面开始执行程序时增加（在Launch mode这一行）：

```
#zws added
bash $base_dir/bin/ctg-kafka-rack.sh

# Launch mode
```

18.生产手记：

kafka: 5044  JMX：5090

# 20.KDC主从

todo：

1.定期备份kdc数据库

2.增加一台免密机器



参见10.10小节

# 21.卸载HDP

### 21.1卸载整个集群

如果只是重装，不要删除配置目录，只删除数据目录，然后ambari-server reset即可。

```bash
1. ambari-server reset

/usr/bin/yum list available --showduplicates

2. 查看日志里面安装了哪些包
   cat  /var/lib/ambari-agent/data/*|grep yum|grep install

3. 删除并且清理ambari的仓库
   cd /etc/yum.repos.d
   rm -f /etc/yum.repos.d/ambari* /etc/yum.repos.d/hdp.*
   yum makecache fast

4. 列出所有的已安装的包
   yum list installed|grep HDP|awk '{print "yum remove -y "$1;}'|sort -u
  yum list installed|grep hbase|awk '{print "yum remove -y "$1;}'|sort -u
   yum list installed |grep hadoop|awk '{print "yum remove -y "$1;}'|sort -u
   yum list installed |grep HDP
   yum list installed |grep ambari|awk '{print "yum remove -y "$1;}'|sort -u
   yum list installed |grep HDP|awk '{print "rpm -e "$1;}'|sort -u
5. 删除数据目录！
   rm -rf  XXXX

   rm -rf /data1/hadoop*
   rm -rf /data2/hadoop*
   kafka的要换个新的目录和zk的目录
6. yum clean all
7. rm -rf /var/cache/yum/*
rm -rf /var/lib/rpm/__db*

#删除配置目录，还是要删掉，不然安装不同的版本会有问题
 rm -rf /etc/hadoop /etc/hbase/

 #删除数据目录,防止软链出问题
 rm -rf /usr/hdp/*

 8. baseurl为空的问题

 https://community.cloudera.com/t5/Community-Articles/ambari-2-7-3-Ambari-writes-Empty-baseurl-values-written-to/ta-p/249314

 cd /usr/lib/ambari-server/web/javascripts
 cp app.js app.js_backup
 edit the app.js

find out the line(39892) : onNetworkIssuesExist: function () {

Change the line from :

  /**
   * Use Local Repo if some network issues exist
   */
  onNetworkIssuesExist: function () {
    if (this.get('networkIssuesExist')) {
      this.get('content.stacks').forEach(function (stack) {
          stack.setProperties({
            usePublicRepo: false,
            useLocalRepo: true
          });
          stack.cleanReposBaseUrls();
      });
    }
  }.observes('networkIssuesExist'),

to

  /**
   * Use Local Repo if some network issues exist
   */
  onNetworkIssuesExist: function () {
    if (this.get('networkIssuesExist')) {
      this.get('content.stacks').forEach(function (stack) {
        if(stack.get('useLocalRepo') != true){
          stack.setProperties({
            usePublicRepo: false,
            useLocalRepo: true
          });
          stack.cleanReposBaseUrls();
        }
      });
    }
  }.observes('networkIssuesExist'),
```

### 21.2删除Service

备注：网上找到的，没有完整验证过

```bash
Usually service can be removed using API calls, but if the service is inconsistent state then API's does not work.

so only way to delete is by running SQL queries. here is the list of steps to delete KNOX service.

1. delete from serviceconfigmapping where service_config_id in (select service_config_id from serviceconfig where service_name like '%KNOX%')

2. delete from confgroupclusterconfigmapping where config_type like '%knox%'

3. delete from clusterconfig where type_name like '%knox%'

4. delete from clusterconfigmapping where type_name like '%knox%'

5. delete from serviceconfig where service_name = 'KNOX'

6. delete from servicedesiredstate where service_name = 'KNOX'

7. delete from hostcomponentdesiredstate where service_name = 'KNOX'

8. delete from hostcomponentstate where service_name = 'KNOX'

9.delete from servicecomponentdesiredstate where service_name = 'KNOX'

10.delete from clusterservices where service_name = 'KNOX'

11. DELETE from alert_history where alert_definition_id in ( select definition_id from alert_definition where service_name = 'KNOX')

12.DELETE from alert_notice where history_id in ( select alert_id from alert_history where alert_definition_id in ( select definition_id from alert_definition where service_name = 'KNOX'))

13.DELETE from alert_definition where service_name like '%KNOX%'

Note1: I have tried and tested this in Ambari 2.4.x

Note2: Above queries are case sensitive - so use Upper/Lower case for service name.
```



# 22.windows安装kerberos

## 1.下载并安装软件

wget -c 'http://web.mit.edu/kerberos/dist/kfw/4.1/kfw-4.1-amd64.msi'

## 2.环境变量

C:\Program Files\MIT\Kerberos\bin

备注：

1.PATH的设置里面，kerberos的位置一定要移动到很靠前的位置，一定要比JDK的位置靠前，因为jdk也带了kinit，一定要放到system32前面，系统自带的也有kinit。

2.如果PATH不设置顺序，必须写命令的全路径

## 3.修改配置

#从生产集群/etc/krb5.conf copy出来，保存到C:\ProgramData\MIT\Kerberos5\krb5.ini

#C:\ProgramData\MIT\Kerberos5\krb5.ini

[libdefaults]
  renew_lifetime = 7d
  forwardable = true
  default_realm = CTYUN.NET
  ticket_lifetime = 24h
  dns_lookup_realm = false
  dns_lookup_kdc = false
  default_ccache_name = /tmp/krb5cc_%{uid}
  #default_tgs_enctypes = aes des3-cbc-sha1 rc4 des-cbc-md5
  #default_tkt_enctypes = aes des3-cbc-sha1 rc4 des-cbc-md5

[domain_realm]
  .ctyun.net = CTYUN.NET
  ctyun.net = CTYUN.NET

[logging]
  default = FILE:///C:/ProgramData/MIT/Kerberos5/krb5kdc.log
  admin_server = FILE:///C:/ProgramData/MIT/Kerberos5/kadmind.log
  kdc = FILE:///C:/ProgramData/MIT/Kerberos5/krb5kdc.log

[realms]
  CTYUN.NET = {
    admin_server = cdnlog040.ctyun.net
    kdc = cdnlog040.ctyun.net
  }

## 4.修改hosts

150.223.254.40  cdnlog040.ctyun.net

## 5.下载keytab并且运行kinit

下载/etc/security/keytabs/spnego.service.keytab放到C:\ProgramData\MIT\Kerberos5

```
cd C:\ProgramData\MIT\Kerberos5

"C:\Program Files\MIT\Kerberos\bin\klist.exe" -k "C:\ProgramData\MIT\Kerberos5\spnego.service.keytab"

"C:\Program Files\MIT\Kerberos\bin\kinit.exe" -kt  "C:\ProgramData\MIT\Kerberos5\spnego.service.keytab" HTTP/cdnlog040.ctyun.net
"C:\Program Files\MIT\Kerberos\bin\klist.exe"



"C:\Program Files\MIT\Kerberos\bin\klist.exe" -k "C:\ProgramData\MIT\Kerberos5\zeppelin.service.keytab"


"C:\Program Files\MIT\Kerberos\bin\klist.exe" -k "C:\ProgramData\MIT\Kerberos5\yarn.service.keytab"

"C:\Program Files\MIT\Kerberos\bin\kinit.exe" -kt  "C:\ProgramData\MIT\Kerberos5\yarn.service.keytab"yarn/ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net

"C:\Program Files\MIT\Kerberos\bin\klist.exe"


-----生产spark
"C:\Program Files\MIT\Kerberos\bin\klist.exe" -k "C:\ProgramData\MIT\Kerberos5\spark.headless.keytab"
"C:\Program Files\MIT\Kerberos\bin\kinit.exe" -kt "C:\ProgramData\MIT\Kerberos5\spark.headless.keytab"  spark-cdnlog@CTYUN.NET
"C:\Program Files\MIT\Kerberos\bin\klist.exe"


"C:\Program Files\MIT\Kerberos\bin\klist.exe" -k "C:\ProgramData\MIT\Kerberos5\keytabs-prod\kylin.keytab"

"C:\Program Files\MIT\Kerberos\bin\kinit.exe" -kt "C:\ProgramData\MIT\Kerberos5\keytabs-prod\kylin.keytab"  kylin/cdnlog040.ctyun.net@CTYUN.NET


"C:\Program Files\MIT\Kerberos\bin\klist.exe" -k "C:\ProgramData\MIT\Kerberos5\keytabs-prod\hdfs.headless.keytab"

"C:\Program Files\MIT\Kerberos\bin\kinit.exe" -kt  "C:\ProgramData\MIT\Kerberos5\keytabs-prod\hdfs.headless.keytab" hdfs-cdnlog@CTYUN.NET


"C:\Program Files\MIT\Kerberos\bin\klist.exe" -k "C:\ProgramData\MIT\Kerberos5\keytabs-prod\yarn.service.keytab"


"C:\Program Files\MIT\Kerberos\bin\kinit.exe" -kt "C:\ProgramData\MIT\Kerberos5\keytabs-prod\yarn.service.keytab"  yarn/cdnlog040.ctyun.net@CTYUN.NET

"C:\Program Files\MIT\Kerberos\bin\klist.exe"


"C:\Program Files\MIT\Kerberos\bin\klist.exe" -k "C:\ProgramData\MIT\Kerberos5\keytabs-prod\rm.service.keytab"

"C:\Program Files\MIT\Kerberos\bin\kinit.exe" -kt "C:\ProgramData\MIT\Kerberos5\keytabs-prod\rm.service.keytab"   rm/cdnlog036.ctyun.net@CTYUN.NET


```

## 6.修改火狐配置：

1. 地址栏输入： about:config

2.  network.negotiate-auth.trusted-uris设置为 ctyun.net,ctcdn.cn（多个主机以,分割）

   network.auth.use-sspi设置为false



# 23.安装ELK

### 1.压测工具安装

- 添加用户

```bash
useradd elasticsearch -g cdnlog
usermod -G hadoop elasticsearch
```



- 配置阿里云镜像

```bash
cd  /etc/yum.repos.d/
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
yum clean all
yum makecache
yum update
```

- 安装新版本git

```bash
yum -y  install curl-devel expat-devel gettext-devel openssl-devel zlib-devel
mkdir /data2/gitsource
cd /data2/gitsource
git clone https://github.com/git/git.git
cd /data2/gitsource/git
git tag
git checkout v2.9.5
git checkout v2.23.0
make configure

./configure
make && make install
```

- 安装python36

配置epel源，这个源有python36，esrally要求必须版本>=3.5

```bash
cat /etc/yum.repo.d/epel.repo

[epel]
name=Extra Packages for Enterprise Linux 7 - $basearch
#baseurl=http://download.fedoraproject.org/pub/epel/7/$basearch
metalink=https://mirrors.fedoraproject.org/metalink?repo=epel-7&arch=$basearch
failovermethod=priority
enabled=1
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7

[epel-debuginfo]
name=Extra Packages for Enterprise Linux 7 - $basearch - Debug
#baseurl=http://download.fedoraproject.org/pub/epel/7/$basearch/debug
metalink=https://mirrors.fedoraproject.org/metalink?repo=epel-debug-7&arch=$basearch
failovermethod=priority
enabled=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7
gpgcheck=1

[epel-source]
name=Extra Packages for Enterprise Linux 7 - $basearch - Source
#baseurl=http://download.fedoraproject.org/pub/epel/7/SRPMS
metalink=https://mirrors.fedoraproject.org/metalink?repo=epel-source-7&arch=$basearch
failovermethod=priority
enabled=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7
gpgcheck=1

yum repo list
yum -y install python36
yum -y install python36-pip
yum -y install python36-devel
pip3 install esrally

#非必需
pip3 install --upgrade  pip

```

压测工具安装：

```
useradd elasticsearch -g cdnlog
usermod -G hadoop elasticsearch
echo 'elasticsearch   ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers
su - elasticsearch

esrally --distribution-version=7.3.1
```

JDK12安装

```bash
#不能是jdk11，压测一定要jdk12
```





### 2.安装ES



#拷贝软件

#40

cd /data3

for ip in `echo 41 42 43 44 45 27 28`
do
scp -r ./elk root@192.168.2.${ip}:/data3
done

#解压软件，建立软链

cd /data3/elk

tar zxvf ./binary/7.3.1/elasticsearch-7.3.1-linux-x86_64.tar.gz -C /data3/elk/

 tar zxvf ./binary/7.3.1/logstash-7.3.1.tar.gz -C  /data3/elk/

tar zxvf ./binary/7.3.1/kibana-7.3.1-linux-x86_64.tar.gz -C /data3/elk

 ln -fs elasticsearch-7.3.1 elasticsearch
 ln -fs filebeat-7.3.1-linux-x86_64 filebeat
 ln -fs kibana-7.3.1-linux-x86_64 kibana
 ln -fs logstash-7.3.1 logstash



chown -R elasticsearch:cdnlog /data3/elk

#建立数据目录
```bash
for i in `seq 1 10`
do
mkdir -p /data${i}/elk-data/elasticsearch
mkdir -p /data${i}/elk-data/filebeat
mkdir -p /data${i}/elk-data/kibana
mkdir -p /data${i}/elk-data/logstash
chown -R elasticsearch:cdnlog /data${i}/elk-data
done
```



#修改配置

node.name: node-40

path.data: /data1/elk-data/elasticsearch,/data2/elk-data/elasticsearch,/data3/elk-data/elasticsearch,/data4/elk-data/elasticsearch,/data5/elk-data/elasticsearch,/data6/elk-data/elasticsearch,/data7/elk-data/elasticsearch,/data8/elk-data/elasticsearch,/data9/elk-data/elasticsearch,/data10/elk-data/elasticsearch

path.logs: /data3/elk/elasticsearch/logs

network.host: 0.0.0.0

cluster.initial_master_nodes: ["node-40"]



jvm.options：

-Xms4g
-Xmx4g

使用G1，注释掉UseConcMarkSweepGC，开始10-:



测试：

curl "http://36.111.140.:9200/_xpack"

### 3.性能测试

首先配置使用自己的集群

esrally configure --advanced-config

esrally --pipeline=benchmark-only

esrally list tracks

esrally list cars

esrally list races

esrally list pipeline

**使用本地es****集群测试**

--pipeline=benchmark-only

**去****es****官网下载**

--pipeline=from-distribution

**测试数据集，默认是****geonames**

--track=geonames

**使用离线的数据集**

--offline

**常用命令组合**

//第一次压测需要从远端下载数据集

esrally --pipeline=benchmark-only --target-hosts=host:9200 --distribution-version=5.2.2（本人用的5.2.2）

//之后数据集不变的话，直接使用本地数据集

esrally --pipeline=benchmark-only --target-hosts=host:9200 --distribution-version=5.2.2 --offline

**注意**

es集群必须处理green状态，否则会被禁止race

因为我们自己有集群，所以这样用：

esrally --pipeline=benchmark-only --target-hosts=host:9200

这时候会下载数据，下载完毕后可以这样用：

esrally --pipeline=benchmark-only --target-hosts=host:9200 --offline

esrally race --track=logging --challenge=append-no-conflicts --car="4gheap"

默认的压测数据的压测配置在 **~/.rally/benchmarks/tracks/default/geonames/track.json**

默认压测的内容比较多，可以自定义压测内容，比如数据导入，数据搜索，统计搜索等，都是些es支持的命令



我的测试：

```bash
#数据集geonames

esrally --pipeline=benchmark-only --target-hosts=ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:9200  --track=geonames --offline --user-tag="node:one-node-on-40"


#数据集http_logs
esrally --pipeline=benchmark-only --target-hosts=ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:9200  --track=http_logs --user-tag="http_logs:one-node-on-40"

#数据集
esrally --pipeline=benchmark-only --target-hosts=ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:9200  --track=nyc_taxis --user-tag="nyc_taxis:one-node-on-40"

```







有用的文档链接;

https://esrally.readthedocs.io/en/latest/race.html

https://esrally.readthedocs.io/en/latest/track.html

### 4.安装elasticsearch-head

```bash
cd /data3/elk/elasticsearch-head
git clone git://github.com/mobz/elasticsearch-head.git
yum -y install npm
cd elasticsearch-head
npm install

cd /data3/elk/elasticsearch-head
npm run start

修改es的配置：（https://www.jianshu.com/p/1869823e72a4）

http.cors.enabled: true
http.cors.allow-origin: "*"
http.cors.allow-methods: OPTIONS, HEAD, GET, POST, PUT, DELETE
http.cors.allow-headers: "X-Requested-With, Content-Type, Content-Length, X-User"
```

访问：

http://36.111.140.40:9100/

连接 http://36.111.140.40:9200/

### 5.安装配置logstash和filebeat

参见 https://www.cnblogs.com/cjsblog/p/9459781.html

```bash
tar zxvf filebeat-7.3.1-linux-x86_64.tar.gz
ln -fs filebeat-7.3.1-linux-x86_64 filebeat

#修改filebeat配置
# vi filebeat.yml
- type: log

  # Change to true to enable this input configuration.
  # 这里要改成true
  enabled: true

  # Paths that should be crawled and fetched. Glob based paths.
  paths:
    #- /var/log/*.log
    #这里修改成自己的目录，支持通配符
    - /data3/elk/filebeat/data/logstash-tutorial*.log

   ......
#----------------------------- Logstash output --------------------------------
output.logstash:
  # The Logstash hosts
  hosts: ["localhost:5044"]


#cat /data3/elk/logstash/config/ctg-nginx2es.conf
input {
     beats {
        port => "5044"
     }
}

output {
     stdout {
        codec => rubydebug
     }
}

#测试配置：
logstash -f /data3/elk/logstash/config/ctg-nginx2es.conf --config.test_and_exit
#启动logstash
logstash -f /data3/elk/logstash/config/ctg-nginx2es.conf --config.reload.automatic
#启动filebeat
./filebeat -e -c filebeat.yml -d "publish"
#生成测试文件
for i in `seq 1 1000000`
do
	datestr=`date`
	echo "${i}.${i}.${i}.${i} - - [${datestr}] \"GET /style2.css HTTP/1.1\" 200 4877 \"http://www.semicomplete.com/projects/xdotool/${i}\" \"Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140205 Firefox/24.0 Iceweasel/24.3.0\"" >> /data3/elk/filebeat/data/logstash-tutorial-zws-3.log
done
```







/data3/elk/logstash/bin/logstash -f /data3/elk/logstash/config/ctg-nginx2es.conf



### 6.源码编译filebeat

下载go

```bash
export GOROOT=/root/go
mkdir -p /root/elk/source/
export GOPATH=/root/elk/source/
mkdir -p ${GOPATH}/src/github.com/elastic
git clone https://github.com/elastic/beats ${GOPATH}/src/github.com/elastic/beats

cd ${GOPATH}/src/github.com/elastic/beats
git checkout v7.3.1

#40
export GOROOT=/data3/elk/source
```



### 7.ES数据测试

```bash
curl --user 'elastic:elastic123!@' -H "Content-Type: application/json" -XGET http://192.168.2.43:19200/edge_computing_event_dev/_search -d '{
"query" : {
"match" : { "cluster" : "guangzhou"}
},
"sort" : [{"event.lastTimestamp" : {"order" : "desc"}}],
"from":0,
"size":3
}'



#构造数据
curl --user 'elastic:elastic123!@' -H "Content-Type: application/json" -XPUT http://192.168.2.43:19200/edge_computing_event_dev/_doc/27369621-2d89-43b4-adc0-46114f69f4c5_zz-yus-6cddc54ccf-bgspk.15f94b0fa5a11252 -d '{
    "cluster": "guangzhou1",
    "time": "1583220219160",
    "message": "Deployment synced successfully",
    "resourceName": "pond-agent",
    "resourceKind": "Deployment",
    "namespace": "default-8",
    "event": {
        "metadata": {
            "name": "pond-agent.15f644824412d338",
            "namespace": "default-8",
            "selfLink": "/api/v1/namespaces/default-8/events/pond-agent.15f644824412d338",
            "uid": "50e0b089-ba2e-4ab6-b635-5429ad30c7dc",
            "resourceVersion": "4024595",
            "creationTimestamp": "1583220219160"
        },
        "involvedObject": {
            "kind": "Deployment",
            "namespace": "default-8",
            "name": "pond-agent",
            "uid": "5e1de52a-9eeb-4067-bf64-049d47218390",
            "apiVersion": "apps/v1",
            "resourceVersion": "3773619"
        },
        "reason": "Synced",
        "message": "Deployment synced successfully",
        "source": {
            "component": "deployment-controller"
        },
        "firstTimestamp": "1583220219160",
        "lastTimestamp": "1583220219160",
        "count": 313,
        "type": "Normal",
        "eventTime": null,
        "reportingComponent": "",
        "reportingInstance": ""
    }
}'
```





# 24.配置Ambari服务

参考文章：https://github.com/BalaBalaYi/Ambari-Elastic-Service

```python
#python获取本机IP

import socket
print(socket.gethostbyname(socket.getfqdn(socket.gethostname())))

ip4=(int)(str.split(".")[3])
str=format("%03d" % (ip4))
```

- 上传zip包

文件位置：C:\Work\Source\ambari-service\KAFAKMANAGER.zip

server:  /var/lib/ambari-server/resources/stacks/HDP/3.0/services

agent:  /var/lib/ambari-agent/cache/stacks/HDP/3.0/services



root/admin
cdnlog@kdc!@#



- 解压

```bash
unzip KAFAKMANAGER.zip
mv KAFAKMANAGER KAFKAMANAGER
```

- 安装

```
修改端口： 29090
zk： ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181/kafka-manager

kafkamanager Download Url
http://36.111.140.40:17080/ambari/kafka-manager-2.0.0.2.tar.gz
root/admin  cdnlog@kdc!@#


scp -r ./KAFKAMANAGER/* 192.168.2.41:/var/lib/ambari-agent/cache/stacks/HDP/3.0/services/KAFKAMANAGER
scp -r ./KAFKAMANAGER/* 192.168.2.43:/var/lib/ambari-agent/cache/stacks/HDP/3.0/services/KAFKAMANAGER
scp -r ./KAFKAMANAGER/* 192.168.2.42:/var/lib/ambari-agent/cache/stacks/HDP/3.0/services/KAFKAMANAGER




scp -r /var/lib/ambari-server/resources/stacks/HDP/3.0/services/ElasticSearch-7.1/* 192.168.254.3:/var/lib/ambari-agent/cache/stacks/HDP/3.0/services/ElasticSearch-7.1
```





# 25.HUE

https://demo.gethue.com

demo/demo



# 26.spark executor配置：



-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/data2/core_files/spark-%p.hprof
-XX:OnOutOfMemoryError="rm -f /data2/core_files/spark-%p.hprof ;/usr/local/jdk/bin/jmap -dump:live,format=b,file=/data2/core_files/spark-%p.hprof;kill -9 %p "



# 27.编译Mysql8:

```bash
yum -y install cmake3-3.14.6-2.el7.x86_64
yum install bison -y

yum -y install centos-release-scl
yum install devtoolset-8
scl enable devtoolset-8 -- bash
source /opt/rh/devtoolset-8/enable


cd /data2
tar zxvf mysql-boost-8.0.17.tar.gz
cd mysql-8.0.17
mkdir objs
cd objs
cmake3 -DWITH_BOOST=/data2/mysql-8.0.17/boost/boost_1_69_0/ ..
```

# 28.防火墙

https://wangchujiang.com/linux-command/c/firewall-cmd.html

```bash
systemctl status firewalld
systemctl is-enabled firewalld.service
systemctl enable firewalld
systemctl start firewalld


sudo firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=36.111.140.30/24 accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=192.168.2.40/24 accept'


sudo firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=192.168.189.0/25 accept'
sudo firewall-cmd --permanent --remove-rich-rule 'rule family=ipv4 source address=192.168.189.0/25 accept'
sudo firewall-cmd --reload
sudo firewall-cmd --list-all


sudo firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=58.62.0.226 accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=36.111.140.26 accept'


sudo firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 port port=6667 protocol=tcp  accept'
sudo firewall-cmd --reload
sudo firewall-cmd --list-all

sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="36.111.140.26" port port="19200" protocol="tcp" accept'

sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="36.111.140.26" port port="15601" protocol="tcp" accept'

firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=36.111.140.30/24 port port=3306 protocol=tcp accept'
sudo firewall-cmd --permanent --remove-rich-rule 'rule family="ipv4" source address="36.111.140.26" port port="19200" protocol="tcp" accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=36.111.140.26 port port=8181 protocol=tcp accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=150.223.254.39 accept'

sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="36.111.140.26" port port="19200" protocol="tcp" accept'

sudo firewall-cmd --reload

rule family="ipv4" source address="150.223.254.0/25" accept


sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="36.111.140.26" port port="19995" protocol="tcp" accept'

sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="150.223.254.40" accept'


sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="58.58.53.2" port port="6667" protocol="tcp" accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="58.58.53.3" port port="6667" protocol="tcp" accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="58.58.53.4" port port="6667" protocol="tcp" accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="58.58.53.5" port port="6667" protocol="tcp" accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="58.58.53.7" port port="6667" protocol="tcp" accept'

sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="150.223.254.0/26" accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="192.168.254.0/26" accept'


sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="125.88.39.158" port port="6667" protocol="tcp" accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="125.88.39.159" port port="6667" protocol="tcp" accept'
sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="125.88.39.167" port port="6667" protocol="tcp" accept'

--43--
sudo firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="125.88.39.157" port port="9806" protocol="tcp" accept'
sudo firewall-cmd --reload
sudo firewall-cmd --list-all

```

# 29.Spark-Shell

## 1.shell

```scala
val parquetFile = sqlContext.read.parquet("/apps/cdn/log/2020-09-08/2020-09-08-21/minute=2020-09-08-21-00/part-00141-77793485-3f72-42f4-9bcf-bd5f07920029-c000.snappy.parquet")



spark-shell --conf spark.executor.memoryOverhead=3000 --conf spark.executor.instances=10 --conf spark.executor.memory=10G --conf spark.driver.memory=10G

val sqlContext = new org.apache.spark.sql.SQLContext(sc)

val parquetFile = sqlContext.parquetFile("/apps/cdn/log/2019-10-10/2019-10-10-13/minute=2019-10-10-13-50")
val parquetFile = sqlContext.parquetFile("/apps/cdn/tmp/2020-09-08/2020-09-08-21/minute=2020-09-08-21-00")
val parquetFile = sqlContext.parquetFile("/apps/cdn/log/2020-09-08/2020-09-08-21/minute=2020-09-08-21-00/part-00141-77793485-3f72-42f4-9bcf-bd5f07920029-c000.snappy.parquet")


val tt2 = sqlContext.parquetFile("/apps/cdn/log/2020-09-08/2020-09-08-21/minute=2020-09-08-21-00/")

parquetFile.toDF().registerTempTable("test")
val hiveContext = new org.apache.spark.sql.hive.HiveContext(sc)
val aa=hiveContext.sql("select * from test limit 10")
aa.show()

val df = parquetFile.toDF()

import sqlContext.implicits._
val parquetFile = sqlContext.read.parquet("/apps/cdn/log/2020-09-08/2020-09-08-21/minute=2020-09-08-21-00")
parquetFile.registerTempTable("logs")

val aa=spark.sql("select channel from logs limit 10")

import sqlContext.implicits._
import org.apache.spark.sql.functions._


var ppp:Int =0
val ff = spark.udf.register("getPart",(channel:String)=>{
    if(channel=="v95-dy.ixigua.com")
    {ppp+=1
    ppp
    }
    else
    1
})

val bb=aa.withColumn("part",col("channel"))

val updatedDf = df.withColumn("part", regexp_replace(col("part"), "v95-dy.ixigua.com", "1"))

val updatedDf = bb.withColumn("part", ff(col("channel"))

SparkSession spark = SparkSession
		             .builder()
		             .appName("spark-job")
		             .getOrCreate();

import org.apache.spark.sql.RuntimeConfig
import org.apache.spark.sql._
val conf:RuntimeConfig = spark.conf();
// text compress
conf.set("mapreduce.output.fileoutputformat.compress", "true");
conf.set("mapreduce.output.fileoutputformat.compress.type", SequenceFile.CompressionType.BLOCK.toString());
conf.set("mapreduce.output.fileoutputformat.compress.codec", "org.apache.hadoop.io.compress.GzipCodec");
conf.set("mapreduce.map.output.compress", "true");
conf.set("mapreduce.map.output.compress.codec", "org.apache.hadoop.io.compress.GzipCodec");
                              .write()
    .format("text")
    .mode(SaveMode.Overwrite)
    .save("hdfs://bbbb");
updatedDf.write.format("gz").partitionBy("part").save("/tmp/zws-test2")
updatedDf.write.format("text").mode(SaveMode.Overwrite).option("compression", "gzip").save("/tmp/zws-test4")

 updatedDf.write.format("parquet").partitionBy("part").save("/tmp/zws-test1")


tt2.rdd.getNumPartitions

    val newDF = df.mapPartitions(
      iterator => {
        val result = iterator.map(row=>
                                   {
                                       val channel=row.getString("channel")
                                       if( channel == "v95-dy.ixigua.com" )
                                       if (data.get(data.fieldIndex("part")))
                                   }

                                 ).toList
        //return transformed data
        result.iterator
        //now convert back to df
      }

).toDF()



    val buffer: mutable.Buffer[Object] = Row.unapplySeq(row).get.map(_.asInstanceOf[Object]).toBuffer
              buffer.append(要加的字段)

              val schema: StructType = row.schema.add("aaa", StringType).add("bbb", StringType).add("ccc", StringType)
              val new_row = new GenericRowWithSchema(buffer.toArray, schema)
```



## 2.spark shell生产跑数据

```bash
spark-shell --conf spark.executor.memoryOverhead=3000 --conf spark.executor.instances=10 --conf spark.executor.memory=2G --conf spark.driver.memory=2G --jars

spark-shell --conf spark.executor.memoryOverhead=2G --conf spark.executor.instances=10 --conf spark.executor.memory=8G --conf spark.driver.memory=3G --conf spark.yarn.queue=default --conf spark.executor.cores=4

import org.apache.spark.sql.RuntimeConfig
import org.apache.spark.sql._

val sqlContext = new org.apache.spark.sql.SQLContext(sc)


import sqlContext.implicits._
import java.lang.Double
import java.util.Date
import java.text.SimpleDateFormat
import org.apache.spark.Partitioner
import org.apache.spark.api.java.function.PairFlatMapFunction
import java.util.ArrayList
import org.apache.spark.api.java.JavaPairRDD

val schemaStr="serverIp string,timestamp string,respondTime long,httpCode integer,eventTime string,clientIp string,clientPort integer,method string,protocol string,channel string,url string,httpVersion string,bodyBytes long,destIp string,destPort integer,status string,full_status string,referer string,Ua string,fileType string,host_name string,source_ip string,source_id string,source_old string,type string,range string,vendorCode byte,genericsChannel string,clientId integer,keyFlag byte,productType byte,hostingType byte,uri string,url_param string,requestBytes long,body_sent long,proxyIp string,via string,sent_http_content_length long,http_range string,sent_http_content_range string,http_tt_request_traceid string,liveProtocol string,currentTime string,requestTime string,command string,connTag string,appName string,stream string,sendBytes string,recvBytes  string"

val parquetFile = sqlContext.read.parquet("/apps/cdn/log/2020-09-09/2020-09-09-17/minute=2020-09-09-17-20/part-00040-efc48350-f9e6-4f72-adb1-69d7caefccb5-c000.snappy.parquet")

val parquetFile = sqlContext.read.schema(schemaStr).parquet("/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-00","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-05","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-10","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-15","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-20","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-25","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-30","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-35"),"/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-40","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-45","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-50","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-55")

#val parquetFile = sqlContext.read.parquet("/apps/cdn/log/2021-04-29/2021-04-29-14/minute=2021-04-29-14-45/task-341.parquet")

val parquetFile = sqlContext.read.parquet("/apps/cdn/log/2021-04-01/2021-04-01-10/minute=2021-04-01-10-10")

ab.write.mode(SaveMode.Append).format("jdbc").option("driver","com.github.housepower.jdbc.ClickHouseDriver").option("url", "jdbc:clickhouse://192.168.2.40:18000").option("user", "default").option("password", "").option("dbtable", "default.t_cdnlog_analysis_c").option("batchsize", 10000).option("isolationLevel", "NONE").save

parquetFile.printSchema

parquetFile.registerTempTable("logs")

<<<<<<< HEAD
 |-- serverIp: string (nullable = true)
 |-- timestamp: string (nullable = true)
 |-- respondTime: long (nullable = true)
 |-- httpCode: integer (nullable = true)
 |-- eventTime: string (nullable = true)
 |-- clientIp: string (nullable = true)
 |-- clientPort: integer (nullable = true)
 |-- : string (nullable = true)
 |-- protocol: string (nullable = true)
 |-- channel: string (nullable = true)
 |-- url: string (nullable = true)
 |-- httpVersion: string (nullable = true)
 |-- bodyBytes: long (nullable = true)
 |-- destIp: string (nullable = true)
 |-- destPort: integer (nullable = true)

val ab = spark.sql("select serverIp,timestamp,respondTime,httpCode,eventTime,clientIp,clientPort,method,protocol,channel,url,httpVersion,bodyBytes,destIp,destPort from logs")
val aa=spark.sql("select eventTime, channel, serverIp,timestamp,uri,source_ip,sendBytes,recvBytes,country,province,city,clientId,type from logs ")
=======
val aa=spark.sql("select serverIp,timestamp,respondTime,httpCode,eventTime,clientIp,clientPort,method,protocol,channel,url,httpVersion,bodyBytes,destIp,destPort,status,full_status,referer,Ua,fileType,host_name,source_ip,source_id,source_old,type,range,vendorCode,genericsChannel,clientId,keyFlag,productType,hostingType,uri,url_param,requestBytes,body_sent,proxyIp,via,sent_http_content_length,http_range,sent_http_content_range,http_tt_request_traceid,liveProtocol,currentTime,requestTime,command,connTag,appName,stream,sendBytes,recvBytes from logs ")

val bb=aa.withColumn("part",col("channel"))


var ppp_ixigua:Int =0
var ppp_ixigua_2:Int =0
var ppp_ltssjy:Int =0
var ppp_ltssjy2:Int =0
var ppp_ltssjy_other:Int =0
var ppp_ugcsjy:Int = 0
var ppp_other:Int =0

val simpleDateFormat: SimpleDateFormat  = new SimpleDateFormat("yyyy-MM-dd-HH-mm")
val procTimeStr="2020-09-08-21-00"
val  procDateTime: Date = simpleDateFormat.parse(procTimeStr)
val ddd1 = procDateTime.getTime()

val ff = spark.udf.register("getPart",(channel:String,eventtime:String)=>{
    val evtime_d=eventtime.toDouble * 1000
    val evtime_l=evtime_d.asInstanceOf[Number].longValue
    val intervals=ddd1-evtime_l
    val batch_ixigua=90
    val batch_ltssjy=20
    val batch_other=40
   if(channel=="v95-dy.ixigua.com") {
      if( intervals<= 300000 ){
      ppp_ixigua+=1
         "v95-dy-"+(ppp_ixigua % batch_ixigua)}
      else
         {"v95-dy-other"}
    }
    else if(channel=="v95-dy-a.ixigua.com" ) {
        if( intervals<= 300000 ){
        ppp_ixigua_2+=1
           "v95-dy-a-"+(ppp_ixigua_2 % batch_ixigua)
        }
        else{
            "v95-dy-a-other"
        }
    }
    else if(channel=="ltssjy.qq.com"  ) {
        if( intervals<= 300000 ){
          ppp_ltssjy+=1
         "ltssjy-"+(ppp_ltssjy % batch_ltssjy)}
       else if( intervals<= 600000 ){
         ppp_ltssjy2+=1
         "ltssjy-sec"
       }
       else{
       ppp_ltssjy_other+=1
        "ltssjy-other-"+(ppp_ltssjy_other % batch_ltssjy)
       }
    }
    else if(channel=="ugcsjy.qq.com" ) {
      ppp_ugcsjy+=1
        "ugcsjy-"+(ppp_ugcsjy % batch_ltssjy)
    }
    else{
        ppp_other+=1
        "other-"+(ppp_other % batch_other)
    }
})
val updatedDf = bb.withColumn("part", ff(col("channel"),col("timestamp")))


class CustomPartitioner() extends Partitioner{
  override def numPartitions: Int = 35

  override def getPartition(key: Any): Int = {
    val keyStr = key.toString
    if( keyStr == "v95-dy-0") {
         0
    } else if( keyStr == "v95-dy-1") {
         1
    } else   if( keyStr == "v95-dy-2") {
         2
    } else   if( keyStr == "v95-dy-3") {
         3
    } else   if( keyStr == "v95-dy-4") {
         4
    } else   if( keyStr == "v95-dy-other") {
         5
    } else   if( keyStr == "v95-dy-a-0") {
         6
    } else   if( keyStr == "v95-dy-a-1") {
         7
    } else   if( keyStr == "v95-dy-a-2") {
         8
    } else   if( keyStr == "v95-dy-a-3") {
         9
    } else   if( keyStr == "v95-dy-a-4") {
         10
    } else   if( keyStr == "v95-dy-a-other") {
         11
    } else   if( keyStr == "ltssjy-0") {
         12
    } else   if( keyStr == "ltssjy-1") {
         13
    } else   if( keyStr == "ltssjy-2") {
         14
    } else if( keyStr == "ltssjy-3") {
         15
    } else  if( keyStr == "ltssjy-4") {
         16
    } else if( keyStr == "ltssjy-sec") {
         17
    } else  if( keyStr == "ltssjy-other-0") {
         18
    } else  if( keyStr == "ltssjy-other-1") {
         19
    } else  if( keyStr == "ltssjy-other-2") {
         20
    } else  if( keyStr == "ltssjy-other-3") {
         21
    } else  if( keyStr == "ltssjy-other-4") {
         22
    } else if( keyStr == "ugcsjy-0") {
         23
    } else if( keyStr == "other-0") {
         24
    }else  if( keyStr == "other-1") {
         25
    } else if( keyStr == "other-2") {
         26
    } else  if( keyStr == "other-3") {
         27
    } else  if( keyStr == "other-4") {
         28
    } else  if( keyStr == "other-5") {
         29
    } else  if( keyStr == "other-6") {
         30
    }  else if( keyStr == "other-7") {
         31
    }  else if( keyStr == "other-8") {
         32
    } else  if( keyStr == "other-9") {
         33
    }else
       34
  }
}

val myhash:CustomPartitioner = new CustomPartitioner

val FlatMapData: PairFlatMapFunction[java.util.Iterator[Row], String, Row] = new PairFlatMapFunction[java.util.Iterator[Row], String, Row]() {
    override def call(x: java.util.Iterator[Row]) = {
        import java.util
        val tuple = new util.ArrayList[Tuple2[String, Row]]
        while(x.hasNext ){
           val r = x.next
           val part:String = r.getString(r.fieldIndex("part"))
           tuple.add(Tuple2(part, r))
        }
        tuple.iterator()
    }
}

#val wordPairRDD:JavaPairRDD[String, Row] = updatedDf.toJavaRDD.mapPartitionsToPair(FlatMapData)
#val hashedrdd =wordPairRDD.partitionBy(myhash)

#val updatedDf = bb.withColumn("part", ff(col("channel"),col("timestamp")))
```

```bash
#测试1，直接测试partitionBy
val updatedDf = aa.withColumn("part", ff(col("channel"),col("timestamp")))
updatedDf.write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").csv("/tmp/zws-test1")
```

分区数：
updatedDf.rdd.getNumPartitions
211
共产生文件：

hdfs dfs -ls /tmp/zws-test1/*|grep -v Found|wc -l
4246

耗时1.9分钟：

```bash
#测试2，直接测试repartition
val updatedDf = aa.withColumn("part", ff(col("channel"),col("timestamp")))
updatedDf.repartition(col("part")).write.mode(SaveMode.Overwrite).option("compression", "gzip").option("delimiter", "#").csv("/tmp/zws-test2")

效果：有数据写在一起的现象

v95-dy-0
v95-dy-4
```


共产生文件：

hdfs dfs -ls /tmp/zws-test2/*|grep -v Found|wc -l
31

耗时3.8分钟

有数据倾斜，跑两次，第一次3.8分钟，第二次4.8分钟

zcat part-00002-24a746e3-30b4-486b-8cb3-85907bcaa008-c000.csv.gz |rev|awk -F'#' '{print $1;}'|sort -u|rev



```bash
#测试3，直接测试repartition，然后write的时候partitionBy
val updatedDf = aa.withColumn("part", ff(col("channel"),col("timestamp")))
updatedDf.repartition(col("part")).write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").option("delimiter", "#").csv("/tmp/zws-test3")

效果：4.5分钟，35个文件，可以把文件分开，有shuffle
```



```bash
#测试4，使用coalesce和输出partitionBy
val updatedDf = aa.withColumn("part", ff(col("channel"),col("timestamp")))
updatedDf.coalesce(6).write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").option("delimiter", "#").csv("/tmp/zws-test4")

有spill ，10G内存，2.9G spill到disk，只有6个executor工作，太慢，7.9分钟，有小文件,每个part有5个小文件
```



改启动命令：（10个executor，40G内存）

```bash
#测试5，10个executor，40G内存，用coalesce
val updatedDf = aa.withColumn("part", ff(col("channel"),col("timestamp")))
updatedDf.coalesce(6).write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").option("delimiter", "#").csv("/tmp/zws-test5")

input花了3.2分多钟，只有6个executor，共花了8.9分钟，有小文件,每个part有5个小文件，没有spill，没有shuffle
```



```bash
#测试6，40个executor，10G内存，使用自定义partitioner

import org.apache.hadoop.io.compress.GzipCodec

val updatedDf = aa.withColumn("part", ff(col("channel"),col("timestamp")))
val wordPairRDD:JavaPairRDD[String, Row] = updatedDf.toJavaRDD.mapPartitionsToPair(FlatMapData)
val hashedrdd =wordPairRDD.partitionBy(myhash)
hashedrdd.saveAsTextFile("/tmp/zws-test6",classOf[GzipCodec])

（1.7+4.2）5.9分钟，35个文件，shuffle了19G
```



```bash
#测试7，测试两个批次的
val parquetFile = sqlContext.read.schema(schemaStr).parquet("/apps/cdn/log/2020-09-08/2020-09-08-21/minute=2020-09-08-21-00","/apps/cdn/log/2020-09-08/2020-09-08-21/minute=2020-09-08-21-05")

......


val updatedDf = aa.withColumn("part", ff(col("channel"),col("timestamp")))
updatedDf.repartition(col("part")).write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").option("delimiter", "#").csv("/tmp/zws-test7")
```



```bash
#测试8
val parted = updatedDf.repartitionByRange(col("part"))
parted.write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").csv("/tmp/zws-test8")
```



```bash
#测试9 两个批次
val parted = updatedDf.repartitionByRange(col("part"))
parted.write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").csv("/tmp/zws-test9")
```



```bash
#测试10 三个批次
val parquetFile = sqlContext.read.schema(schemaStr).parquet("/apps/cdn/log/2020-09-08/2020-09-08-21/minute=2020-09-08-21-00","/apps/cdn/log/2020-09-08/2020-09-08-21/minute=2020-09-08-21-05","/apps/cdn/log/2020-09-08/2020-09-08-21/minute=2020-09-08-21-10")

parquetFile.registerTempTable("logs")
val aa=spark.sql("select serverIp,timestamp,respondTime,httpCode,eventTime,clientIp,clientPort,method,protocol,channel,url,httpVersion,bodyBytes,destIp,destPort,status,full_status,referer,Ua,fileType,host_name,source_ip,source_id,source_old,type,range,vendorCode,genericsChannel,clientId,keyFlag,productType,hostingType,uri,url_param,requestBytes,body_sent,proxyIp,via,sent_http_content_length,http_range,sent_http_content_range,http_tt_request_traceid,liveProtocol,currentTime,requestTime,command,connTag,appName,stream,sendBytes,recvBytes from logs ")

val updatedDf = aa.withColumn("part", ff(col("channel"),col("timestamp")))

val parted = updatedDf.repartitionByRange(col("part"))
parted.write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").csv("/tmp/zws-test10")

#测试11 半个小时的批次

```



```bash
#测试12：一个小时的数据

val parquetFile = sqlContext.read.schema(schemaStr).parquet("/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-00","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-05","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-10","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-15","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-20","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-25","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-30","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-35","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-40","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-45","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-50","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-55")

parted.write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").csv("/tmp/zws-test12")
不到8分钟

#测试13 ，使用6个core（spark出错了）
spark-shell --conf spark.executor.memoryOverhead=2G --conf spark.executor.instances=40 --conf spark.executor.memory=8G --conf spark.driver.memory=3G --conf spark.yarn.queue=batch --conf spark.executor.cores=4

这个时间点腾讯的数据是没有的（量切走了）。ixigua的数据都是1G的，所以可以适当增大ixigua的分区数

    val batch_ixigua=90
    val batch_ltssjy=40
    val batch_other=40

    parted.write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").csv("/tmp/zws-test13")
```






```
#
val parted = updatedDf.repartitionByRange(col("part"))
parted.registerTempTable("parted")
val cc = spark.sql("select * from parted limit 10")

#val parted = updatedDf.repartition(6,col("part"))

parted.write.mode(SaveMode.Overwrite).option("compression", "gzip").csv("/tmp/zws-test9")

parted.write.partitionBy("part").mode(SaveMode.Overwrite).option("compression", "gzip").csv("/tmp/zws-test9")
#updatedDf.coalesce(3).write.mode(SaveMode.Overwrite).partitionBy("part").csv("/tmp/zws-test6")
#updatedDf.write.mode(SaveMode.Overwrite).csv("/tmp/zws-test5")
updatedDf.rdd.getNumPartitions


------------------------------------------------------------------

select sum(req_cnt),event_time,proc_time,client_id,channel
from CDN_LOG_BASE_V01
where event_time=1599570000
group by event_time,proc_time,client_id,channel
order by 1 desc
------------------------------------------------------------------
parquetFile.rdd.mapPartitionsWithIndex(
      (x,iterator) => {
        val result = iterator.map(row=>
                                   {
                                       val channel=row.getString("channel")
                                       if( channel == "v95-dy.ixigua.com" )
                                       if (data.get(data.fieldIndex("part")))
                                   }

                                 ).toList
        //return transformed data
        result.iterator
        //now convert back to df
      }

```




```
create /kafka_auth_test ""
addauth digest kafka:Kafka0701@2019
setAcl /kafka_auth_test auth:kafka:Kafka0701@2019:rwadc
getAcl /kafka_auth_test


addauth digest kafka:Kafka0701@2019
echo -n 'kafka:Kafka0701@2019' | openssl dgst -binary -sha1 | openssl base64
Mzhi+zkz666H8mFYTEXjsyKT5uk=
create /kafka-digest-test 'digest'
setAcl /kafka-digest-test digest:kafka:Mzhi+zkz666H8mFYTEXjsyKT5uk=:rwdca
getAcl /kafka-digest-test
addauth digest kafka:Kafka0701@2019



/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper hbase36.ecloud.com:2181/kafka-no-auth2  --topic zwstest    --partitions 1 --replication-factor 1


```

## 3.thriftserver

```bash
metastore.catalog.default
默认为spark，需要修改为hive

#注意，后面的principal要是thriftserver所在的机器的

/usr/hdp/current/spark2-client/bin/beeline -u "jdbc:hive2://cdnlog029.ctyun.net:10016/;principal=spark/cdnlog029.ctyun.net@CTYUN.NET"

----spark sql能跑通
select count(*) from (select cast(cast(substring(timestamp,1,11) as int)/300 as int)*300 as ttt,channel,source_ip,cast(region/100 as int)*100 as rrr
 from  cdn_log_origin
where dateminute>='2020-07-30-16-30'
and  dateminute<='2020-07-30-16-40'
group by ttt,channel,source_ip,rrr
) aaa

----hive
select count(1) from (
SELECT ttt,channel,source_ip,rrr
FROM(
SELECT
cast( cast( substring( `TIMESTAMP`, 1, 11 ) AS INT )/ 300 AS INT )* 300 AS ttt,
 channel,
source_ip,
cast( region / 100 AS INT )* 100 AS rrr
FROM
cdn_log_origin
 WHERE
dateminute >= '2020-07-29-21-30'
AND dateminute <= '2020-07-29-21-40'
and vendorcode=1
) aaa
group by ttt,channel,source_ip,rrr
) bbb
```



# 30.Zeppellin

默认driver从org.postgresql.Driver改为

org.apache.hive.jdbc.HiveDriver

url:

jdbc:postgresql://localhost:5432/   ->  jdbc:hive2://ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-028.ctyuncdn.net:12181/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=hiveserver2

user:

gpadmin > hive



# 31.查看磁盘信息

yum install smartmontools

 smartctl -a /dev/sdb

# 32.Hbase问题排查

![1571019650938](/img/1571019650938.png)


```bash
41主机：

klist -k /etc/security/keytabs/hbase.service.keytab
kinit -kt /etc/security/keytabs/hbase.service.keytab hbase/ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net

hbase shell

scan 'hbase:meta',{ROWPREFIXFILTER => 'kylin:KYLIN_OO6KVM9J4T'}

put 'hbase:meta','kylin:KYLIN_OO6KVM9J4T','table:state',"\x08\x01",1579464201498

get  'hbase:meta',"kylin:KYLIN_OO6KVM9J4T,,1579464200900.c6a968c41414509c708fa01c18f9c805."


put 'hbase:meta','kylin:KYLIN_OO6KVM9J4T,,1579464200900.c6a968c41414509c708fa01c18f9c805.','info:state','CLOSED',1584929438589
put 'hbase:meta',"kylin:KYLIN_OO6KVM9J4T,\x00\x01,1579464200900.b42993d61501407ed4a97be442467716.",'info:state','CLOSED',1584929438597

put 'hbase:meta',"kylin:KYLIN_OO6KVM9J4T,\x00\x02,1579464200900.4bfe3dbd9c0c13aca179acf8972fa1ad.",'info:state','CLOSED',1584950118350
put 'hbase:meta',"kylin:KYLIN_OO6KVM9J4T,\x00\x03,1584950118349.10898d68f5f99a83435a5880dab78596.",'info:state','CLOSED',1584929438597
put 'hbase:meta',"kylin:KYLIN_OO6KVM9J4T,\x00\x04,1579464200900.6ab620ef74f7be7304dbc55c5e047c46.",'info:state','CLOSED',1584950118318




echo "scan 'hbase:meta',{FILTER => org.apache.hadoop.hbase.filter.PrefixFilter.new(org.apache.hadoop.hbase.util.Bytes.toBytes('kylin:KYLIN_Q4ZG4MY5R1'))}"|hbase shell -n|grep OPENING


klist -k /etc/security/keytabs/zk.service.keytab
kinit -kt /etc/security/keytabs/zk.service.keytab zookeeper/ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net

/usr/hdp/current/zookeeper-client/bin/zkCli.sh -server ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181

/usr/hdp/current/zookeeper-client/bin/zkCli.sh -server ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181 ls /hbase-secure/table | grep KYLIN_TJFUCO5QZ0


echo 'scan "hbase:meta"'|hbase shell -n |grep a55f86bc482c366d84c6296e8dec6f98

```

1.租约问题（开发集群）

设置了他为 hbase.regionserver.lease.period 2分钟，但是hbase.rpc.timeout为3分钟，要求hbase.rpc.timeout> hbase.regionserver.lease.period

警告是hbase.regionserver.lease.period已经修改为hbase.client.scanner.timeout.period

但是这个设置为了3分钟，所以实际上是 hbase.rpc.timeout要大于hbase.client.scanner.timeout.period

2.物联网

Scanner超时，增加了timeout参数和scan的

 hbase.client.scanner.timeout.period
hbase.client.scanner.caching



```bash



```





# 33.多环境

1.增加cdnlog-dev和cdnlog-test组

```bash
for ip in `seq 40 45 ` `seq 27 28`
do
	ssh 192.168.2.${ip} groupadd cdnlog-dev;
done

for ip in `seq 40 45 ` `seq 27 28`
do
	ssh 192.168.2.${ip} groupadd cdnlog-test;
done

for ip in `seq 40 45 ` `seq 27 28`
do
	ssh 192.168.2.${ip} useradd cdnlog-dev -g cdnlog-dev
done

for ip in `seq 40 45 ` `seq 27 28`
do
	echo  192.168.2.${ip} useradd cdnlog-test -g cdnlog-test
	ssh 192.168.2.${ip} useradd cdnlog-test -g cdnlog-test
done

for ip in `seq 40 45 `
do
	echo  192.168.2.${ip}
	ssh 192.168.2.${ip} mkdir /data8/apps-dev
	ssh 192.168.2.${ip} mkdir /data9/apps-test
done



sed -i '/APP_BASE=/d' /home/cdnlog-dev/.bash_profile
echo 'export APP_BASE=/data8/apps-dev' >> /home/cdnlog-dev/.bash_profile
sed -i '/APP_BASE=/d' /home/cdnlog-test/.bash_profile
echo 'export APP_BASE=/data9/apps-test' >> /home/cdnlog-test/.bash_profile


sed -i '/APP_PROFILE=/d' /home/cdnlog-dev/.bash_profile
echo 'export APP_PROFILE=dev' >> /home/cdnlog-dev/.bash_profile
sed -i '/APP_PROFILE=/d' /home/cdnlog-test/.bash_profile
echo 'export APP_PROFILE=test' >> /home/cdnlog-test/.bash_profile

sed -i '/APP_PORT_PREFIX=/d' /home/cdnlog-dev/.bash_profile
echo 'export APP_PORT_PREFIX=10' >> /home/cdnlog-dev/.bash_profile
sed -i '/APP_PORT_PREFIX=/d' /home/cdnlog-test/.bash_profile
echo 'export APP_PORT_PREFIX=20' >> /home/cdnlog-test/.bash_profile

mkdir /data8/apps-dev/cdn-log
mkdir /data8/apps-dev/object-log
mkdir /data8/apps-dev/oss-transcode

mkdir /data9/apps-test/cdn-log
mkdir /data9/apps-test/object-log
mkdir /data9/apps-test/oss-transcode

chown -R cdnlog-dev:cdnlog-dev  /data8/apps-dev
chown -R cdnlog-test:cdnlog-test  /data9/apps-test

```



2.kerberos添加账号

```bash

#------------------cdnlog-dec
ssh 192.168.2.40 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net"'

ssh 192.168.2.40 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-dev.keytab cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net"'

ssh 192.168.2.41 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net"'

ssh 192.168.2.41 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-dev.keytab cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net"'

ank -randkey hive/cdnlog036.ctyun.net@CTYUN.NET
xst -k /etc/security/keytabs/hive.service.keytab hive/cdnlog036.ctyun.net@CTYUN.NET

ssh 192.168.2.42 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net"'

ssh 192.168.2.42 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-dev.keytab cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net"'


ssh 192.168.2.43 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net"'

ssh  192.168.2.43 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-dev.keytab cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net"'


ssh 192.168.2.44 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-011.ctyuncdn.net"'

ssh 192.168.2.44 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-dev.keytab cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-011.ctyuncdn.net"'

ssh 192.168.2.45 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-012.ctyuncdn.net"'

ssh 192.168.2.45 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-dev.keytab cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-012.ctyuncdn.net"'

ssh 192.168.2.27 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net"'

ssh 192.168.2.27 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-dev.keytab cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net"'


ssh 192.168.2.28 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-028.ctyuncdn.net"'

ssh 192.168.2.28 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-dev.keytab cdnlog-dev/ctl-nm-hhht-yxxya6-ceph-028.ctyuncdn.net"'

##----------------------------
ssh 192.168.2.40 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-test/ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net"'

ssh 192.168.2.40 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-test.keytab cdnlog-test/ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net"'

ssh 192.168.2.41 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-test/ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net"'

ssh 192.168.2.41 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-test.keytab cdnlog-test/ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net"'


ssh 192.168.2.42 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-test/ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net"'

ssh 192.168.2.42 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-test.keytab cdnlog-test/ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net"'


ssh 192.168.2.43 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-test/ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net"'

ssh  192.168.2.43 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-test.keytab cdnlog-test/ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net"'


ssh 192.168.2.44 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-test/ctl-nm-hhht-yxxya6-ceph-011.ctyuncdn.net"'

ssh 192.168.2.44 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-test.keytab cdnlog-test/ctl-nm-hhht-yxxya6-ceph-011.ctyuncdn.net"'

ssh 192.168.2.45 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-test/ctl-nm-hhht-yxxya6-ceph-012.ctyuncdn.net"'

ssh 192.168.2.45 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-test.keytab cdnlog-test/ctl-nm-hhht-yxxya6-ceph-012.ctyuncdn.net"'

ssh 192.168.2.27 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-test/ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net"'

ssh 192.168.2.27 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-test.keytab cdnlog-test/ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net"'


ssh 192.168.2.28 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "ank -randkey cdnlog-test/ctl-nm-hhht-yxxya6-ceph-028.ctyuncdn.net"'

ssh 192.168.2.28 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/cdnlog-test.keytab cdnlog-test/ctl-nm-hhht-yxxya6-ceph-028.ctyuncdn.net"'
```

3.HBASE建立命名空间

```bash
hbase shell:
create_namespace "cdnlog_dev"
grant 'cdnlog-dev','RWXCA','@cdnlog_dev'

create_namespace "cdnlog_test"
grant 'cdnlog-test','RWXCA','@cdnlog_test'

quit
```

4.HDFS目录

```bash
 kinit -kt /etc/security/keytabs/hdfs.headless.keytab  hdfs-cdnlog@CTYUNCDN.NET

 hdfs dfs -mkdir /apps-dev
 hdfs dfs -mkdir /apps-test

 hdfs dfs -chown -R cdnlog-dev:cdnlog-dev /apps-dev
 hdfs dfs -chown -R cdnlog-test:cdnlog-test /apps-test


```

5.Hive

```bash
使用各自的HDFS目录建立外表
```

6.队列

```bash
已增加测试环境队列：
kylin-test
etl-test
```



# 34.CDN新需求：

```bash
1.网络安全（优先级高）
2.实时计算（高）
3.客户日志定制化需求
4.动态路由优化（高）
5.海量日志的查询（延迟越小越好，用于定位问题）
6.请求链路跟踪和查询
7.希望能够深入CDN业务
8.目前30个节点，年底扩到120-200个节点


```

上线部署：2019-11-08



# 35.Ambari新增用户

cdnlog/cdnlog@26VLvZ3F6Esa

cdnlogview: cdnlog@26VLvZ3F6Esa

- Kafka建Topic



# 36.运维客户端

https://42.123.69.96:2653/

zhangwusheng/K**2@cdn



# 37.直播建Topic

```bash
#白山云直播
topicName=baishanYun_live
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
KAFKA_USER="baishanYun"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 5 --replication-factor 3
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --consumer --group grp-${KAFKA_USER}


#验证数据
#/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  cdnlog003.ctyun.net:5044    --topic ${topicName} --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-${KAFKA_USER}

#==================================================================================
#白山云直播-海外
topicName=baishanYun_live_haiwai
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
KAFKA_USER="baishanYun"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 3 --replication-factor 3
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --producer

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --consumer --group grp-${KAFKA_USER}

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}

#===============================================
#浩瀚云直播
topicName=haohanYun_live
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
KAFKA_USER="haohanYun"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 5 --replication-factor 3
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --consumer --group grp-${KAFKA_USER}


#验证数据
#/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  cdnlog003.ctyun.net:5044    --topic ${topicName} --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-${KAFKA_USER}

#==================================================================================
#浩瀚云直播-海外
topicName=haohanYun_live_haiwai
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
KAFKA_USER="haohanYun"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 3 --replication-factor 3
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --producer

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --consumer --group grp-${KAFKA_USER}

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}


#===============================================
#有谱云直播
topicName=youpuYun_live
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
KAFKA_USER="youpuYun"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 5 --replication-factor 3
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --consumer --group grp-${KAFKA_USER}


#验证数据
#/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  cdnlog003.ctyun.net:5044    --topic ${topicName} --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-${KAFKA_USER}

#==================================================================================
#浩瀚云直播-海外
topicName=youpuYun_live_haiwai
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
KAFKA_USER="youpuYun"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 3 --replication-factor 3
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --producer

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --consumer --group grp-${KAFKA_USER}

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}



#===============================================
#有谱云直播
topicName=huaweiYun_live
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
KAFKA_USER="huaweiYun"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 20 --replication-factor 3
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --consumer --group grp-${KAFKA_USER}


#验证数据
#/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  cdnlog003.ctyun.net:5044    --topic ${topicName} --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-${KAFKA_USER}

#==================================================================================
#浩瀚云直播-海外
topicName=youpuYun_live_haiwai
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
KAFKA_USER="youpuYun"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 12 --replication-factor 3
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --producer

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --consumer --group grp-${KAFKA_USER}

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}
```



# 38.Ubuntu:

- root不能登录:


```
sudo vi /etc/pam.d/gdm-autologin

注释行 "auth requied pam_succeed_if.so user != root quiet success"

sudo vi /etc/pam.d/gdm-password

注释行 "auth requied pam_succeed_if.so user != root quiet success"

```

- ambari:


```bash
wget -c 'http://public-repo-1.hortonworks.com/HDP/ubuntu18/3.x/updates/3.1.0.0/HDP-3.1.0.0-ubuntu18-deb.tar.gz'

wget -c 'http://public-repo-1.hortonworks.com/ambari/ubuntu18/2.x/updates/2.7.3.0/ambari-2.7.3.0-ubuntu18.tar.gz'

wget -c 'http://public-repo-1.hortonworks.com/HDP-UTILS-1.1.0.22/repos/ubuntu18/HDP-UTILS-1.1.0.22-ubuntu18.tar.gz'

wget -c 'http://public-repo-1.hortonworks.com/HDP-GPL/ubuntu18/3.x/updates/3.1.0.0/HDP-GPL-3.1.0.0-ubuntu18-gpl.tar.gz'

https://packages.gitlab.com/gitlab/gitlab-ce/packages/ubuntu/bionic/gitlab-ce_12.4.2-ce.0_amd64.deb

curl -s https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash

sudo apt-get install gitlab-ce=12.4.2-ce.0

wget --content-disposition https://packages.gitlab.com/gitlab/gitlab-ce/packages/ubuntu/bionic/gitlab-ce_12.4.2-ce.0_amd64.deb/download.deb
```

- 无安全的两个问题：

1. Kafka的timeline配置，false，61888，http
2. zeppelin需要自己创建pid目录



# 39.AXE创建Topic

```bash
axe-SubTaskCallback
axe-TemplateExecuteTask
axe-BareMetalSearchTask
axe-BareMetalPowerTask
axe-BareMetalCreateTask
axe-BareMetalInstallTask
axe-ServerCompareTask
axe-JobAgentLog

topicName=axe-SubTaskCallback
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
OSS_USER="axetask"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 1 --replication-factor 3
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${OSS_USER} --topic ${topicName}   --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${OSS_USER} --topic ${topicName}   --consumer --group grp-${OSS_USER}


#验证数据
#/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  cdnlog003.ctyun.net:5044    --topic ${topicName} --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-${OSS_USER}


topicName=axe-SubTaskCallback
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
OSS_USER="axetask"
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --alter --zookeeper ${ZK_CONN} --topic ctYun --partitions ${PART_NUM}
```





# 40.GC设置

```bash
function GetGcOpts()
{
   local log_dir=$1
   local component_name=$2
   local use_g1=$3
   local timestamp_str=`date +'%Y%m%d%H%M'`
   gc_log_filename="${log_dir}/${component_name}.gc.log"
   local gc_log_enable_opts="-verbose:gc -Xloggc:${gc_log_filename}"
   local gc_log_rotation_opts="-XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=10 -XX:GCLogFileSize=10M"
   local gc_log_format_opts="-XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:+PrintGCDateStamps"
   local gc_g1_opts="-XX:+UseG1GC -XX:MaxGCPauseMillis=100 -XX:-ResizePLAB "
   local gc_error_opt="-XX:ErrorFile=${log_dir}/hs_err_${component_name}_pid%p.log"
   #######################################################
   ##NOTE: In hbase.distro
   #exec "$JAVA" -Dproc_$COMMAND -XX:OnOutOfMemoryError="kill -9 %p"
   #NOTE: in hdfs.distro
   #-XX:OnOutOfMemoryError=\"/usr/hdp/current/hadoop-hdfs-namenode/bin/kill-name-node\"
   #######################################################
   local gc_oom_opt="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=${log_dir}/heapdump-${component_name}-${timestamp_str}.hprof"
   local gc_cmd_flags=" -XX:+PrintCommandLineFlags -XX:+PrintFlagsFinal"

   if [ "X${use_g1}" = "Xuse_g1" ]
   then
       echo "${gc_g1_opts} ${gc_log_enable_opts} ${gc_log_rotation_opts} ${gc_log_format_opts}  ${gc_error_opt} ${gc_oom_opt} ${gc_cmd_flags}"
   else
       echo "${gc_log_enable_opts} ${gc_log_rotation_opts} ${gc_log_format_opts}  ${gc_error_opt} ${gc_oom_opt} ${gc_cmd_flags}"
   fi
}



```

kafka的特殊，需要整理ambari服务，或者手工修改：

```bash
#修改kafka-run-class.sh
#1. 增加函数定义 GetGcOpts()
#2. 增加如下参数
kafka_gc_opts=`GetGcOpts “${LOG_DIR}” "kafka" "notuse_g1"`
#3. 修改变量
KAFKA_GC_LOG_OPTS="-Xloggc:$LOG_DIR/$GC_LOG_FILE_NAME -verbose:gc -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+PrintGCTimeStamps -XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=10 -XX:GCLogFileSize=100M"
	KAFKA_GC_LOG_OPTS=${kafka_gc_opts}

#scp到每一台机器

#另外，kafka的内存是在kafka-server-start.sh里面设置的
if [ "x$KAFKA_HEAP_OPTS" = "x" ]; then
    export KAFKA_HEAP_OPTS="-Xmx10g -Xms10g -XX:MetaspaceSize=96m -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M -XX:MinMetaspaceFreeRatio=50 -XX:MaxMetaspaceFreeRatio=80"
fi


#发布脚本


for ip in `cat cdn_hosts_kafka.txt `
do
echo ${ip}
ssh ${ip} -p 9000 "cp  /usr/hdp/current/kafka-broker/bin/kafka-run-class.sh /usr/hdp/current/kafka-broker/bin/kafka-run-class.sh.20191211"
done


scp -P 9000 /home/zhangwusheng/kafka-run-class.sh 192.168.254.3:/usr/hdp/current/kafka-broker/bin/


for ip in `cat cdn_hosts_all.txt `
do
  echo ${ip}
  ssh -p 9000 ${ip} "mkdir -p /data1/var/log/spark2/object-log;mkdir -p /data1/var/log/spark2/cdnlog;"
  ssh -p 9000 ${ip} "chmod -R a+rwx /data1/var/log/spark2;"
done
```



# 41.Spark-Shell

```scala
hdfs dfs -mkdir /tmp/2020-05-31

spark-shell --conf spark.executor.memoryOverhead=3000 --conf spark.executor.instances=10 --conf spark.executor.memory=2G

import spark.sql

val sqlContext = new org.apache.spark.sql.SQLContext(sc)

val filename="/apps/druid_018/2020-05-31/2020-05-31-01"
val filename="/tmp/202005/druid_parquet_202005.db/proc_time=202005312355"
val filename="/apps/druid_018/2020-05-31-00/minute=2020-05-31-00-55/part-00058-b979ae85-7821-4cf4-9ee8-9c0fb03ef148-c000.snappy.parquet"

val parquetFile = sqlContext.parquetFile(filename)

parquetFile.printSchema()

parquetFile.registerTempTable("test_tmp")

val bb = sql("select TraceContext, body_sent, connTag, type, serverIp, liveProtocol, bodyBytes, completion, region, hostingType, qypid, destIp, recvBytes, ServerTiming, http_range, keyFlag, tcpinfo_rttvar, host_name, respondTime,cast(timestamp*1000 as bigint) as timestamp, clientIp, bytessent, url, tcpinfo_rtt, sendBytes, sent_http_content_length, protocol, isp, source_old, url_param, Error_Reason, http_hls_param, qyid, source_id, minute, genericsChannel, httpVersion, fileType, requestTime, playDur, Ua, httpCode, uri, vendorCode, clientPort, lakeId, range, requestBytes, channel, stream, appName, proxyIp, http_tt_request_traceid, currentTime, TT_Request_TraceId, command, sent_http_content_range, source_ip, status, referer, via, clientId, destPort, productType, eventTime, method from test_tmp")

bb.write.parquet("/tmp/2020-05-31/01")

val bb2 = sql("select timestamp from test_tmp  limit 2")
bb2.show

bb2.registerTempTable("ccc")
sql("select cast(timestamp*1000 as bigint) from ccc").show

sql("select count(distinct serverIp) from test_tmp  limit 2").show

sql("select uri,count(1) as total from test_tmp group by uri order by total desc ").show


val df = spark.read.parquet("/apps/cdn/log/2020-02-19/2020-02-19-00")




val df = spark.read.parquet("/tmp/zws-parquet-4")


```



spark-sql

生产

```bash
修改配置：metastore.catalog.default  spark 改成 hive

/usr/hdp/current/spark2-client/bin/beeline -u "jdbc:hive2://cdnlog029.ctyun.net:10016/;principal=spark/cdnlog029.ctyun.net@CTYUN.NET"
```

见 29.





# 42.恢复Hbase元数据

## 42.1 恢复整个集群

> 目前我们使用的Hbase版本（2.0.0和2.0.2）是比较尴尬的版本，提供的hbck2工具基本不可使用。 2.0.3, 2.1.2, 2.2.0之后的版本才会提供可用的hbck2，但是开发环境中kylin已经造成了两次集群数据不可用，因此要找到一种方法来恢复元数据，经过探索， 发现了一个可以恢复元数据的方法，记录如下：

- 准备工作：

1. 备份数据

   主要是namespace列表，因为恢复完毕后不会自动创建namespace，需要手动创建

2. 修改配置： conf.setBoolean("hbase.hregion.memstore.mslab.enabled", false);

   否则后面的OfflineMetaRepair 后抛出NPE异常

3. 如果有可能，flush一下表

   ```bash
    echo 'flush tablname' |hbase shell -n
   ```

4. 停止集群

5. 将HDFS上的Hbase的数据目录备份走

   ```bash
    hdfs dfs -mkdir -p /apps/hbase-backup-20200110/data
    hdfs dfs -mv /apps/hbase/data/data /apps/hbase-backup-20200110/data
   ```

   后续的恢复工作以/apps/hbase-backup-20200110/data为基础，因为数据少，所以后面的是copy数据

-
  恢复工作


1. 停止集群

2. 修改hbase的根目录和zk的根目录的配置

   ```bash
    #Hbase目录
    /apps/hbase25/staging
    /apps/hbase25/data
    #zk目录
    /hbase25-unsecure
    #一定要换目录，是为了确保目录下面是干净的！如果不换目录，请确保已经删除了所有的文件！
   ```

3. 重启集群

   这个重启是必须的，用来生成HBASE的version文件和id文件

4. 验证集群是正常启动的

   ```bash
   echo 'list'|hbase shell -n
   echo 'scan "hbase:meta"'|hbase sh
   ```

5. 停止集群

6. 挪动数据目录

   ```bash
   #！！！切换到HDFS用户，kerberos是不同的命令
   su - hdfs
   #删除default，一般不存在，有时候会出现，确保删掉
   hdfs dfs -rmr /apps/hbase25/data/data/default
   #copy数据
   hdfs dfs -cp /apps/hbase-backup-20200110/data/data/cdnlog /apps/hbase25/data/data

   hdfs dfs -cp /apps/hbase-backup-20200110/data/data/default /apps/hbase25/data/data

   hdfs dfs -cp /apps/hbase-backup-20200110/data/data/zws /apps/hbase25/data/data

   hdfs dfs -chown -R hbase:hdfs /apps/hbase25/data

   hdfs dfs -ls /apps/hbase25/data/data/*

   ```

7. 删除zk目录

   ```bash
   #一定要在集群关闭的状态下删除！
   /usr/hdp/current/zookeeper-client/bin/zkCli.sh -server t135:2181 rmr /hbase25-unsecure
   ```

8. 启动集群，验证是否正常（这一步应该可以省略）

   ```bash
   echo 'list'|hbase shell -n
   echo 'scan "hbase:meta"'|hbase shell -n
   echo 'list'|hbase shell -n
   ```

9. 不正常重新来，一定要确保命令是正常运行的

10. 停止集群

11. 运行命令

    ```bash
    su - hbase
    hbase org.apache.hadoop.hbase.util.hbck.OfflineMetaRepair -fix
    ```

12. 启动集群

    ```bash
    #验证可以读取数据
    echo 'scan "hbase:meta" ' | hbase shell -n
    ```

13. 删除region相关的数据

    ```bash
    echo 'scan "hbase:meta" ' | hbase shell -n  2>/dev/null|grep ','|grep -v zookeeper|awk '{print $1;}'|grep -v 'hbase:'|grep ','|awk '{printf("deleteall \"hbase:meta\",\"%s\"\n",$1);}'
    
    #验证上面输出
    #在hbase shell里面执行，不同的数据输出是不同的！
    
    deleteall "hbase:meta", "cdnlog:testtable,,1578551500025.b7f684b7ef4d39bca29182f88ab9df93."
    deleteall "hbase:meta", "cdnlog:testtable,00000000000000000000010000,1578551500025.f25045990e8bf33efccc9bbb7b090237."
    deleteall "hbase:meta", "cdnlog:testtable,00000000000000000000020000,1578551500025.02c8ec8051730292c1a81068763a6525."
    deleteall "hbase:meta", "cdnlog:testtable,00000000000000000000030000,1578551500025.09986e2942c662be0a6ed6c44f843412."
    deleteall "hbase:meta", "cdnlog:testtable,00000000000000000000040000,1578551500025.2f5c3942c6ed35bb743f0dc71fd7adea."
    deleteall "hbase:meta", "cdnlog:testtable,00000000000000000000050000,1578551500025.c6640bfb422a7c90371d9680b69d636a."
    deleteall "hbase:meta", "cdnlog:testtable,00000000000000000000060000,1578551500025.e1888be48220f0a00c0da5ed2b531432."
    deleteall "hbase:meta", "cdnlog:testtable,00000000000000000000070000,1578551500025.178aad1c6262dc5675cb4fee63e01b4b."
    deleteall "hbase:meta", "cdnlog:testtable,00000000000000000000080000,1578551500025.ed7d49f1e2dfdcf0b44b63f7c61bfb11."
    deleteall "hbase:meta", "cdnlog:testtable,00000000000000000000090000,1578551500025.d3e62896b2651dac4f98a8c523d9deab."
    deleteall "hbase:meta", "testtable,,1578551478240.62610b4494f71428b8d3198c97f9e98b."
    deleteall "hbase:meta", "testtable,00000000000000000000010000,1578551478240.16c876a34b4bde70e25e4f121148506e."
    deleteall "hbase:meta", "testtable,00000000000000000000020000,1578551478240.e949c1158c5157a3f51ffce95117f499."
    deleteall "hbase:meta", "testtable,00000000000000000000030000,1578551478240.158e1cfc21041173dbfa0933890d15b7."
    deleteall "hbase:meta", "testtable,00000000000000000000040000,1578551478240.81179946305bd69be0a3dbea04e7b1ab."
    deleteall "hbase:meta", "testtable,00000000000000000000050000,1578551478240.3a028f391f4d5085c0a9c9e51fcc4f9b."
    deleteall "hbase:meta", "testtable,00000000000000000000060000,1578551478240.c8ea8b3543c07ceaa9ffeed25411de77."
    deleteall "hbase:meta", "testtable,00000000000000000000070000,1578551478240.7706a4936316b6c1b9e143853d4c6d48."
    deleteall "hbase:meta", "testtable,00000000000000000000080000,1578551478240.b5c3fefc80de158f178d45dafcee324b."
    deleteall "hbase:meta", "testtable,00000000000000000000090000,1578551478240.10b6ec98bf5db7fdbfdfc996c3a22258."
    deleteall "hbase:meta", "zws:testtable,,1578551494048.6238e0b66e6203fa0c5566532da91d8a."
    deleteall "hbase:meta", "zws:testtable,00000000000000000000010000,1578551494048.4478f421a32fe206d9cb1a73732f8fcf."
    deleteall "hbase:meta", "zws:testtable,00000000000000000000020000,1578551494048.94cca9bef528ec2466e54c2f9d2c31aa."
    deleteall "hbase:meta", "zws:testtable,00000000000000000000030000,1578551494048.eb5ad3c230d08aaff7743f8da7389e59."
    deleteall "hbase:meta", "zws:testtable,00000000000000000000040000,1578551494048.def014fa8dcefca2b2baa8c61b54dee2."
    deleteall "hbase:meta", "zws:testtable,00000000000000000000050000,1578551494048.501b997e23409e5251b390f7a22f3a39."
    deleteall "hbase:meta", "zws:testtable,00000000000000000000060000,1578551494048.e507ddd8a7b1ebc07d49956205ca2ebb."
    deleteall "hbase:meta", "zws:testtable,00000000000000000000070000,1578551494048.e0c4007576835d8c2d42e0192cd3fb4a."
    deleteall "hbase:meta", "zws:testtable,00000000000000000000080000,1578551494048.2e1360529420f2ce8d32a6f37fcd1edb."
    deleteall "hbase:meta", "zws:testtable,00000000000000000000090000,1578551494048.88c4293a2a80543dcd31ebb61a326d57."
    ```



14. 上传hbase-operator-tools的jar包到/usr/hdp/current/hbase-client/lib

    ```bash
    git clone https://github.com/apache/hbase-operator-tools
    #编译通过
    #上传到 /usr/hdp/current/hbase-client/lib
    ```

15. 运行修复命令

    ```bash
    cd /usr/hdp/current/hbase-client/bin/
    ls /usr/hdp/current/hbase-client/lib/hbase-hbck2-1.1.0-SNAPSHOT.jar
    hbase hbck -j ../lib/hbase-hbck2-1.1.0-SNAPSHOT.jar addFsRegionsMissingInMeta cdnlog
    hbase hbck -j ../lib/hbase-hbck2-1.1.0-SNAPSHOT.jar addFsRegionsMissingInMeta zws
    hbase hbck -j ../lib/hbase-hbck2-1.1.0-SNAPSHOT.jar addFsRegionsMissingInMeta default

    #一定要记录每条命令的输出
    assigns 10b6ec98bf5db7fdbfdfc996c3a22258 158e1cfc21041173dbfa0933890d15b7 16c876a34b4bde70e25e4f121148506e 3a028f391f4d5085c0a9c9e51fcc4f9b 62610b4494f71428b8d3198c97f9e98b 7706a4936316b6c1b9e143853d4c6d48 81179946305bd69be0a3dbea04e7b1ab b5c3fefc80de158f178d45dafcee324b c8ea8b3543c07ceaa9ffeed25411de77 e949c1158c5157a3f51ffce95117f499
    #都要记录下来！
    ```

16. 重启集群,验证数据

    ```bash
    echo 'scan "hbase:meta", {FILTER => "(PrefixFilter ('"'"'zws:testtable,'"'"')"} ' | hbase shell -n
    ```

17. assign region

    ```bash
    #针对所有的第15步的assigns，运行
    echo 2e1360529420f2ce8d32a6f37fcd1edb 4478f421a32fe206d9cb1a73732f8fcf 501b997e23409e5251b390f7a22f3a39 6238e0b66e6203fa0c5566532da91d8a 88c4293a2a80543dcd31ebb61a326d57 94cca9bef528ec2466e54c2f9d2c31aa def014fa8dcefca2b2baa8c61b54dee2 e0c4007576835d8c2d42e0192cd3fb4a e507ddd8a7b1ebc07d49956205ca2ebb eb5ad3c230d08aaff7743f8da7389e59 |awk '{for(i=1;i<=NF;i++){printf("assign \"%s\"\n",$i);}}'
    
    #产生类似如下输出：
    assign "2e1360529420f2ce8d32a6f37fcd1edb"
    assign "4478f421a32fe206d9cb1a73732f8fcf"
    assign "501b997e23409e5251b390f7a22f3a39"
    assign "6238e0b66e6203fa0c5566532da91d8a"
    assign "88c4293a2a80543dcd31ebb61a326d57"
    assign "94cca9bef528ec2466e54c2f9d2c31aa"
    assign "def014fa8dcefca2b2baa8c61b54dee2"
    assign "e0c4007576835d8c2d42e0192cd3fb4a"
    assign "e507ddd8a7b1ebc07d49956205ca2ebb"
    assign "eb5ad3c230d08aaff7743f8da7389e59"
    
    #将这些命令在hbase shell里面运行
    
    ```



18. 重启集群

19. 创建nemespace

    ```bash
    list_namespace
    create_name
    grant
    ```



20. 验证集群可读可写

    ```bash
    #一般写会出问题！
    scan "hbase:meta", {FILTER => "(PrefixFilter ('"'"'zws:testtable,'"'"')"}
    put 'zws:testtable','2','info0:1','1'
    get 'zws:testtable','2','info0:1'
    put 'cdnlog:testtable','2','info0:1','1'
    get 'cdnlog:testtable','2','info0:1'
    put 'testtable','2','info0:1','1'
    get 'testtable','2','info0:1'
    
    #验证能创建表
    hbase pe --nomapred --rows=1000 --presplit=10 --table=testtable111_hbase25 sequentialWrite 1
    ```



21. TODO：

    ```bash
    1. kylin建的表带有很多自定义属性，尤其是带了协处理器，需要验证
    2. 验证集群带有本来就disable的表，目前恢复出来的表都是enable的（这个属性是记录到表的序列化的信息里面的，但是最好验证一下）
    3. OfflineMetaRepair 在2.1.6中会被废弃
    ```



22.

## 42.2单个表遇到了RIT

- 第一步：清理zk

  ```bash
  #1  清理zookeeper的目录
  #使用hbase的keytab
  kinit -kt /etc/security/keytabs/hbase.service.keytab hbase/sct-nmg-huhehaote2-tsdb-04.in.ctyun.net@CTYUN.NET
  #使用域名连接zk
  /usr/hdp/current/zookeeper-client/bin/zkCli.sh -server cdnlog036.ctyun.net:12181
  #删除表
  rmr /hbase-secure/table/tsdb:cdn_monitor-rollup
  ```


- 第二步：清理hdfs目录

  ```bash
   hdfs dfs -mkdir /tmp/hbase-tsdb-backup
   hdfs dfs -mv /apps/hbase/data/data/tsdb/cdn_monitor-rollup /tmp/hbase-tsdb-backup
  ```

- 第三步：清理hbase meta表

  ```bash
  
  echo  'scan "hbase:meta",{ROWPREFIXFILTER=>"tsdb:cdn_monitor-rollup",COLUMNS=>["info:state"]}' | hbase shell -n > cdn_monitor-rollup.meta
  
  cat cdn_monitor-rollup.meta |awk -F' column=' '{printf("deleteall \"hbase:meta\",\"%s\"\n",$1);}'|sort -u > cdn_monitor-rollup.rowkey
  
  ## !! 检查命令，手工执行输出！！
  
  #检查是否删除干净
  scan "hbase:meta",{ROWPREFIXFILTER=>"tsdb:cdn_monitor-rollup"}
  ```



- 第四步：清理MasterWal

  ```bash
  # 最好停掉两个master
  hdfs dfs -mv /apps/hbase/data/MasterProcWALs/* /tmp/hbase-tsdb-backup/MasterProcWALs
  ```

- 第五步：重启Master

  ```bash
  检查结果！！
  ```

- 第六步(恢复单个表)

  ```bash
  如果需要恢复表，那么进行如下操作：
  
  ```

#找出所有的region和时间戳
  hdfs dfs -ls /apps/hbasenew-20200324/data/data/tsdb/cdn_monitor-rollup

  #生成表的信息
  put 'hbase:meta','tsdb:cdn_monitor_tsdb','table:state',"\x08\x00"
  ```









遇到了连接太多的问题，修改



hadoop.proxyuser.hive.hosts 改成*

hadoop.proxyuser.yarn.hosts 改成*





部署flink：

​```bash
#config.sh最后面增加两行

export HADOOP_CLASSPATH=`hadoop classpath`
export HADOOP_CONF_DIR=/etc/hadoop/conf

/usr/hdp/current/zookeeper-client/bin/zkCli.sh  -server 36.111.140.27:12181 create /flink ""
/usr/hdp/current/zookeeper-client/bin/zkCli.sh  -server 36.111.140.27:12181 create /flink/cdnlog ""

#console1
nc -l -p 9000
#console2
bin/flink run examples/streaming/SocketWindowWordCount.jar   --hostname 192.168.2.40 --port 9000
#console3
tail -f flink-root-taskexecutor-0-ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net.out
  ```



编译kafka HDP自带的2.0：

build.gradle

```java

buildscript {
  repositories {
    mavenCentral()
    jcenter()

    #增加如下仓库
    maven {
      url  "http://repo.hortonworks.com/content/groups/public/"
    }
    maven {
      url  "http://repo.hortonworks.com/content/repositories/releases"
    }
  }
```

gradle.properties

```java
#repoUrl=http://nexus-private.hortonworks.com/nexus/content/groups/public
repoUrl=http://repo.hortonworks.com/content/groups/public/
#mavenUrl=http://nexus-private.hortonworks.com:8081/nexus/content/repositories/IN-QA
#mavenUsername=
#mavenPassword=
```



编译HDP的phoneix

mvn versions:set -DnewVersion=5.1.0-HBase-2.0-CTG



# 43.安装KafkaRestProxy

## 1.开发环境

- 官方网址

  https://docs.confluent.io/current/kafka-rest/config.html#kafka-rest-https-config

- 下载软件

  ```bash
  #36.111.140.40主机
  cd /data1/Soft
  wget -c http://packages.confluent.io/archive/5.4/confluent-community-5.4.0-2.12.tar.gz
  tar zxvf confluent-community-5.4.0-2.12.tar.gz -C /data2
  cd /data2/confluent-5.4.0
  ```

- 安装准备

```bash
#建立kafka-rest的zk目录
/usr/hdp/current/zookeeper-client/bin/zkCli.sh -server ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181 create /kafka-rest-server "nodata"




#设置环境变量
export KAFKA_REST_HOME=/data2/confluent-5.4.0
export KAFKA_REST_CONF_DIR=${KAFKA_REST_HOME}/etc/kafka-rest
export KAFKA_REST_JAAS_CONF="${KAFKA_REST_CONF_DIR}/kafka-rest.jaas"
export KAFKAREST_OPTS="-Djava.security.auth.login.config=${KAFKA_REST_JAAS_CONF} -Dkafka-rest.log.dir=."
cd ${KAFKA_REST_HOME}

#增加用户
useradd kafkarest -g hadoop

#生成jaas文件

cat > ${KAFKA_REST_JAAS_CONF}<<EOF
KafkaClient {
org.apache.kafka.common.security.plain.PlainLoginModule required
username="admin"
password="admin-sec";
};

krest.ctyuncdn.cn {
org.eclipse.jetty.jaas.spi.PropertyFileLoginModule required
debug="true"
file="/data2/kafka-rest-zws/etc/kafka-rest/password.properties";
};
EOF

cat > /data2/kafka-rest-zws/etc/kafka-rest/password.properties<<EOF
aliyunuser:aliyunpwd,aliyun
ossuser:osspwd,oss
EOF


#创建topic
topicName=KafkaRestTest2
userName="DebugTopic"
ZK_CONN="ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1"
#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 1 --replication-factor 3
#检查
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}
#授权可写
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic ${topicName}   --producer
#授权可读
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${userName} --topic ${topicName}   --consumer --group grp-${topicName}
#检查授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}
#控制台写数据
/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667   --topic ${topicName} --producer-property security.protocol=SASL_PLAINTEXT --producer-property sasl.mechanism=PLAIN
#控制台读数据
cat /usr/hdp/3.1.0.0-78/kafka/consumer-kafka-rest.properties
security.protocol=SASL_PLAINTEXT
sasl.mechanism=PLAIN
group.id=grp-KafkaRestTest2
#从头开始读取数据
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667    --topic ${topicName} --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-${topicName} --consumer.config /usr/hdp/3.1.0.0-78/kafka/consumer-kafka-rest.properties
#从指定partition读取数据
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667    --topic ${topicName} --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --offset latest --partition 0 --group grp-${topicName} --consumer.config /usr/hdp/3.1.0.0-78/kafka/consumer-kafka-rest.properties

#增加partition数目
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --alter --zookeeper ${ZK_CONN} --topic ${topicName} --partitions 15

#压测

 #binary数据
 curl -X POST -H "Content-Type: application/vnd.kafka.binary.v2+json" -H "Accept: application/vnd.kafka.v2+json" --data '{"records":[{value":"S2Fma2E="}]}' http://192.168.2.40:18682/topics/KafkaRestTest2

  curl -X POST -H "Content-Type: application/vnd.kafka.binary.v2+json" -H "Accept: application/vnd.kafka.v2+json" --data '{"records":[{value":"S2Fma2E="}]}' http://192.168.2.40:18682/topics/KafkaRestTest2

 wget http://www.acme.com/software/http_load/http_load-12mar2006.tar.gz
```
## 2.生产环境

```bash

 -----------------------------------------------
 OSS实例
 /usr/hdp/current/zookeeper-client/bin/zkCli.sh -server cdnlog040.ctyun.net:12181  create /oss-kafkaproxy "nodata"

 mkdir -p /usr/local/kafkaproxy/oss/confluent-5.4.0
 ln -fs /usr/local/kafkaproxy/oss/confluent-5.4.0 /usr/local/oss-kafkaproxy

cat > ${KAFKA_REST_JAAS_CONF}<<EOF
export OSS_KAFKA_REST_HOME=/usr/local/oss-kafkaproxy
export OSS_KAFKA_REST_CONF_DIR=${OSS_KAFKA_REST_HOME}/etc/kafka-rest
export OSS_KAFKA_REST_JAAS_CONF="${OSS_KAFKA_REST_CONF_DIR}/oss-kafka-rest.jaas"
export OSS_KAFKA_REST_LOG_DIR=${OSS_KAFKA_REST_HOME}/logs
mkdir -p ${OSS_KAFKA_REST_LOG_DIR}
export KAFKAREST_OPTS="-Djava.security.auth.login.config=${KAFKA_REST_JAAS_CONF} -Dkafka-rest.log.dir=${OSS_KAFKA_REST_LOG_DIR}"
EOF

topicName=KafkaRestTest2
userName="DebugTopic"
ZK_CONN="ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181/kafka-auth-test-1"

1.存储/点播-容量---- oss-vod-capacity
2.点播-转码        ---- oss-vod-transcode
3.直播-流量        -----oss-live-flow
4.直播-转码       ------oss-live-transcode
5.直播-API调用 ------oss-live-api
6.直播-流数量 ------   oss-live-streamcount

topicName="oss-vod-capacity"
userName="ossVod"
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
PART_NUM=2

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic oss-vod-capacity   --partitions ${PART_NUM} --replication-factor 3
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic oss-vod-transcode   --partitions ${PART_NUM} --replication-factor 3
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic oss-live-flow   --partitions ${PART_NUM} --replication-factor 3
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic oss-live-transcode   --partitions ${PART_NUM} --replication-factor 3

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic oss-live-api   --partitions ${PART_NUM} --replication-factor 3
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic oss-live-streamcount   --partitions ${PART_NUM} --replication-factor 3


/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic oss-vod-capacity   --producer
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic  oss-vod-transcode   --producer

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic oss-live-flow   --producer
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic oss-live-transcode  --producer
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic oss-live-api  --producer
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic oss-live-streamcount  --producer


curl -X POST -H "Content-Type: application/vnd.kafka.json.v2+json"      -H "Accept: application/vnd.kafka.v2+json"       --data '{"records":[{"value":{"foo":"bar"},"partition":0}]}' "http://192.168.254.13:18682/topics/oss-vod-capacity"

curl -X GET -H "Accept: application/vnd.kafka.v1+json, application/vnd.kafka+json, application/json"  "http://192.168.254.13:18682/topics/oss-vod-capacity"

#使用admin的账号
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server cdnlog003.ctyun.net:5044    --topic oss-vod-capacity --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning   --group grp-oss-vod-capacity

#从指定partition的最后面读数据
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server cdnlog003.ctyun.net:5044    --topic oss-vod-capacity --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --offset latest --partition 0 --group grp-oss-vod-capacity

#生产系统03主机使用debugtopic用户读取最后的数据
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server cdnlog003.ctyun.net:5044    --topic ctYun --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --offset latest --partition 0 --group grp-oy-ctyun

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic  oss-vod-transcode   --operation Read


#https
curl -k --cert /usr/local/openresty/nginx/conf/server.cer --key /usr/local/openresty/nginx/conf/server.key -X POST -H "Content-Type: application/vnd.kafka.json.v2+json"      -H "Accept: application/vnd.kafka.v2+json"       --data '{"records":[{"value":{"foo-https":"bar-https"},"partition":0}]}' "https://150.223.254.4:443/topics/oss-vod-capacity"
```

- 修改配置


```bash
#配置文件：

id=kafka-rest-40
#schema.registry.url=http://localhost:8081
#zookeeper.connect=localhost:2181
#bootstrap.servers=PLAINTEXT://localhost:9092
#
# Configure interceptor classes for sending consumer and producer metrics to Confluent Control Center
# Make sure that monitoring-interceptors-<version>.jar is on the Java class path
#consumer.interceptor.classes=io.confluent.monitoring.clients.interceptor.MonitoringConsumerInterceptor
#producer.interceptor.classes=io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor

bootstrap.servers=SASL_PLAINTEXT://ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:6667,ctl-nm-hhht-yxxya6-ceph-010.ctyuncdn.net:6667

zookeeper.connect=ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-028.ctyuncdn.net:12181/kafka-rest-server

listeners=http://0.0.0.0:18682

producer.threads=3
producer.compression.type=lz4
shutdown.graceful.ms=10000
client.sasl.mechanism = PLAIN
client.security.protocol=SASL_PLAINTEXT
debug=true
#client.sasl.jaas.config="KafkaClient\n{\norg.apache.kafka.common.security.plain.PlainLoginModule required\nusername="admin"\npassword="admin-sec";\n};"

#ssl.enabled.protocols=http,https
ssl.client.authentication=REQUIRED
#authentication.method=BASIC
authentication.method=DIGEST
authentication.realm=krest.ctyuncdn.cn
authentication.roles=aliyun,oss
authentication.multitenant.enabled=true
authentication.topics=aliyun:Test2,test3;oss:oss,oss3

access.control.allow.methods=POST

```

- 启动应用程序

```bash
${KAFKA_REST_HOME}/bin/kafka-rest-start ${KAFKA_REST_CONF_DIR}/kafka-rest.properties
```

- 写入测试数据

```bash
#写入json测试数据
curl -X POST -H "Content-Type: application/vnd.kafka.json.v2+json"      -H "Accept: application/vnd.kafka.v2+json"       --data '{"records":[{"value":{"foo":"bar"}}]}' "http://192.168.2.40:18682/topics/KafkaRestTest2"
#写入指定分区数据
curl -X POST -H "Content-Type: application/vnd.kafka.json.v2+json"      -H "Accept: application/vnd.kafka.v2+json"       --data '{"records":[{"value":{"foo":"bar"},"partition":0}]}' "http://192.168.2.40:18682/topics/KafkaRestTest2"
#BASIC 认证
curl --basic --user 'ossuser:osspwd' -X POST -H "Content-Type: application/vnd.kafka.json.v2+json"      -H "Accept: application/vnd.kafka.v2+json"       --data '{"records":[{"value":{"foo":"bar"},"partition":0}]}' "http://192.168.2.40:18682/topics/KafkaRestTest2"
#DIGEST认证
 curl -vvv --digest --user ossuser:osspwd -X POST -H "Content-Type: application/vnd.kafka.json.v2+json"      -H "Accept: application/vnd.kafka.v2+json"       --data '{"records":[{"value":{"foo22":"bar22"},"partition":0}]}' "http://192.168.2.40:18682/topics/KafkaRestTest2"

#生成binary数据
curl -X POST -H "Content-Type: application/vnd.kafka.binary.v2+json" -H "Accept: application/vnd.kafka.v2+json" --data '{"records": [{"value": "H4sIAAAAAAAAAOVb227bSne+71OwAbawg26Scx7SgRHIZ8eW48T2VuKiEMjhUKItkQpJHezi/2971V71qle97hMURR+nRXvXV+gaSnaiUyw5h12gdmRIMyNyOOtb6/vWmsl//92//Nc//+Nf/O2LQudDnR/3X2y9wB51MBUOFtwh9MVvL8qkp4sy6FWdXGLiCZ9DH8HQmeuin6XRJYyBbuQgZFo7ZdnfzSLTRBCCBj3UaTkd9NdYum9V6RKE/S1Mtijf4tz6K+Qh9DcwVHUTGFtNhWDPkdzBzMHSf+w6z/ISOgWR1fR6uuxkETQc7l/Cx36elZnKutBgZmG+1QnSVJuGno6SwLm/yTLlqBS6BvnDuC3Xne11C9XJsm43a2e/kAOifOwhj4iIUh4LgTC882JfchkgSaVz02+/vkjaaVAOcr39C9lp+qNmv97UH3UzIlmxe0pJ3hmfcjb6he7V6s2LulK6KE703XG0HUaxZjoMPeoTHFMuPBzX9sf9BJZ326w5lZRiMV3Z33VeJFkKMz+6vDx3sWOWPMyiu527UhfQ7HnILFcEZlswKaw5PIixCdi0HJjhR8eXVpxnPWt2XGXdWOc6/7xGo9Ho8wrBgKsA+hrZfdLtBi53kPVrM0mjbFRYZ5cWBji8sppvm4K9tOr9flc3dXiSlC6HBaPC+vXk6LJx+pvVTW61dajVbfbS2u3ARLQrqIMcSqjvEGFdBHGQJw/f2s1yDc8MI4T0PIchZL17t5PDPXXuwi2pQzxGTTvML066+vKub2Bnw8f3GsyTFtkgV/r4fAJY87uF5jpnwPs+SNsPV+hkRdlKgwrIM55ibDD5bitZcCM8tcYUulMDlJOJ3Sd3QfrFtw2WwyRI7wZfNmdd057q0Ys/LfqrAAwg8BN/hbsKmAfzlrormnVXhuhT7iq2kFjqrmYWDJ6W+fDkZN5fOTgN2sxfh1nE26p00vLOKYfY8x2V9ebddukgV+l+p2WmjKTLCPaFT3lriF2ABfqyoQUBCzll8bo9SKJtxBUmgZK2QkLZiAnPlgJJG9wxpJ5UigS6Vm7zKBDED3WtAI/fjpUXUxmwGEUSe4ph6vko9jmSDJwa+7VokG8bX0C1crxt5oQRBrtQgUStGG8LP2aRH1FNRBhFoWQeIkJBiPWCSCrirev1mKMvnd7+0sXtGWe2Hzz38uPFB/v8tP5x/72NHeIgG2KcxIKJV1Y9jfIMwPi0E803TqFkP+E6U9BSf4nnfNn3wxyHyMr78SqOw46P6TpOsx7H4aVO8+UsZvwFwMf4Zv7SzVTQNcs87yOPHe4EEW6c5b2gdG+KLF0XXlxIRDYF2GFmm4vbkyebXvUH4emRuSj/Siye9P7IYPx4p9XhmDmisu33UE8QjtlSZAF5Yg9WnHvmNQ8vwqvIsgG6jK0TtVI+zXW7UQJwC4pCl0ULcR37EeY+jSlMHHGBFYDPxUDzS7qcm+L1urAklLKZuDdrbLqm2qH0SbkzULB6oDGKchAZMCvAQqGrj3cuhaAAalC4/W4FlK8KI7jnM3URN7qISA9mjOeF0budShoxE0yA4OaUkW++yAmrmr//xGh1faA1x+dz82okKs8aoHU1+G7uCgckgsMRts50acKA2zw+OLams2hqAFz5M5XbxPSrwwX9geFia2sV+UCI4Gh5grWg2NizQ8Tk/rO0I71NZdoPpZ1nqJqfRTq7lzv20Zm9e2EjbF/s/26/Zz5CNibzeIIcFtAEYdj/oXpmncRdEMevAPOdqIc8RT0EyXmIUezzDSH2A7hHet/MPZjwRzWxyD14TerBz2WecJB0I7cLz/o6GJSdlgLDbYdKeYGKlSaR1kGAAi3DQFB4OhqjMNBPcdN3Sdoh/ZslgZ8a0JclFDOdP84DCWS/8CJoYtalHsgdb0VaQZ7jgctLZxA2YRoUKB+IZDHIM4LEZh6YwpycXpYmZZY7qrwbpCpKl+XjKwe6ADI9djplr7u+g81Ku4dcacGzGscXFw+u9dkG8jvywzfB0zDFxzP7pDHLFFUgnkXq7OT/2DSFCcdj5DtxBd9iq6tGIGvBtKAeF6iCI3/DJPg7F3kj4gdIR0iHaK7IO7yL1Wl9X3tXl3XSuBsdA2rZdZ03h43nlngrrlzLMwTHq5kHFnvNrIc/yT3r5zKvrMs8qfhJGgrJh1sYO+jlF0zxU1mAfa0iO+n9g6sA2PHkd6wCrKgvmblw41wM5rKgxTgi6A+uAyS9tms80Omn7XXhT4AKvNX4/1lZ/zRiMBExRTXSJmKwyItUqJVQlFTVADfSZZB0HwZ7ZjAk4Q+DYwGxhkYRX1OZJalxtfHm8kwaz6KcQh6C5uSZtR+1tWsyFI8K8lPd9P9q9i3pctf8wdm3EJJt5o7/n7Pvw2v78OODpjq6mKqqeUQRRB1utIzzKCe/E5zg5z///h/+41//7X/+/Z9msTW9J/natpwn0QLEsLewtyAWAAagYlt0IdID3WIiHEi6K+zOCiky0dIbACt2hkDnmTPSSZjNi30XITY+PMzPumMkx+9J9zDx30JEZ3AbJM7OP6B9s7HW67O1Qzr1hY/n0TZjrHnFvxyAFw17F3CAWp4JUa1q+vAeokormOxptUZJnMyisnpUdzLdKRw6o2Jxy8hoc8/xyZRLl1p1sWzH17UpXtgdoo4vHV+YXdXFLA7JDW3aGQ3AknaUq9SJwiC9XbCrN/1xsahCGIKbuET4SAqGCJgdt6q1apEW9gn6gMGFWpBOohb8bmJvWC3xFWvPhBpg7+W2biaFPu8Gd2br36n2DCkC1pzuXVoVAl5ZUYxDqeLIFlpom2ke2L5EZpeXy5hjxmISv7LO39ft+ilCH14+DxrcMfs6ziRkLgMGX2QUjKVcyPpXgAPz+eMxgEbPKDtu/H4eHcQj/tPnY4oZeAwj6oTRVMHNwKIXBfaNao86xUiN+rjXHw7GSxs3cnnBOOJf8/mvoqCaPxCd6g+cMEiiQVVlCPqJCwKHgOxCkQgle9BfXFLpYQGrIt3Kpq9VP4m231zLy3Z6pw4P0sNgZ/j7XViicb+xU6+/6fi8PThrNvbQ/aer8uT2tHV5e3Wt2hmyj8eyebDT+8T3293x7vXHd++O+vFhdtPqE/8NGQzjdvvqfi/FvdtePch78rzzpnnFcKDa7zLv/kO86ye71/qWq1svJKeNVl18kG992hznH49I3Bl8op1Pu8Pgw7hxez+4O+i8GRfHRTs56NzHx3tv9k4aZ6XyitR/f9U+y3bC7nnc9+u9owPv5I2/vx/59+VhpN7t3bLssj/a2xfp1UEoW2c0sz8SVZx0Tw7U/gfae7t7ffzxUlx7R+3idpx9vEF4f79Q18NhGAbX747ioGEPfv/U/uAVai+lJ9n+7t2bN2fH7bgrLttXY/k2vs/uUONtfs39N2PmixFug3+NagXoZr0NGuS2ULnWaS3NWqZUuY1roENGQR5tg6Vq8GoNJzjZJjUVFa0CUmb4BPS7LX0PaS0DwWnEQCSHoQ6ohxQDta0CoWtg+dYgnY4+bjT2eCuGoWB4Dim2ktiTAcI0wiqkjEcxCWgtyhSk44z/+Qs81IDOi4XWXxiitKaLBNprue4GpY62Ua0/zMxRkQAR0MqIiQCuHEgdIYowBtLzRS3WOirOg3wbt2gL1ybKYbtqrelxH+6UDrrdmsrSOGlP3WTS1M6zwWN/OFC3unwcPXHTbd/8LE0WTpN0MH48uWH5r6yjxiSmWTtVrfjoqt7cP35ofGWNhmsnEdNZmu3Fx4TCbDVSSUy9V1iNLISYOZdXjG7Dyf6jxRwj563q8At+XoBllbypXnJVjJWL9Sq8WFddRb9knn6RuR82hRJHLkRYLqS34QnEpzQV7fObE9SuNJW87px4w6mm4qHsvQdNRTbjWAIZNn1ufH1k2eS8k6Xa/w23zIb9VFH5ju+w1qSrxdrWXjZKu1kQARXv5tBWWs2dgwk3P8fcZgfb1AVNUipX7GZ5Qi5am6xRRa+sTeSCgDb1cuxQUHfVqs3yKfHJ06XIWT4Nkl7bKSGBibLBrKn7g7CbKDcYBmWQG6ElXcQRqC7mM8IIpTiri5umKTn+ZdELuitK5sRB8xkbI1x+s8UvPg2CXO8FqdKuAFEDwSU5D6JXVvL2wsLEYabqdwH5pTZTQHOKKekFbe3e9HX76yb+nCPJVWJaLJ5aZOva11uRIJljxdWZkTm9hIi/oX37SRoNMvhn7AzJY/tWw4dZS6sgLzNgqECVyTAp79w4HySmojSqjjrYQD2rK1+L9mXAad8qmKYCb2bC0xKdq4rCzTVMtgWNPZg3CRnVEWExp17APE8hLR0Y9QCVaU5lPcFE5/X3i0z00PitTCSEYSLKfWNfq/H51AsY27rcuXARY5DJLOcoq9/pPGaGw8eLSwDLTNdku9VTOEKRJED9PA792AsQDSAHYgKxMI6DUEHMZQGZ+eoUMW5ntMxRJtZf7SdUOIwA/2xWSVjXTRbqCMwcEQAngWRm4RAvFdx7ulw86yS9QZEou5+o4mt552QpIMPk1N3bE/Vdubezw/ZIfbfOqGD1/d0DD+2KPUF3SCvLk3aSBt1j86VNvAdz4vPnus9jdNwLusPkFi6Pv8D61frC63nh8nOGuRoGi6UHui4MFkoP5vA9wsCIQML+AhIgmHpPVyq/Y7iM7tKgl6gWPHUB69Uaso0M7/nP1kGPYRNskSg9idtVzByNKeEMhZEHyQmRXCLXo8ztw/zsOA96+mG3ex2tvn+6vwiZh8ZvjpCyipC+cDxpfWju77i+B5GyAe8u9k5cc04e0eXxsRp0vOcCEBYO85mrStBpBP+KxkQihCStv7TO88zsfEIu3g9zCIJk9qzfKZh+YDB/32ntnj0nJJpkgFDPISb54CvK+GuJhxWpwKJ4IHSyhwZLuKQS528qHdKi47T7HQeEsg4KPacOg1J1Wti3MbIR/BU249OP8B4TGyEHLtBfNw+glKJvTwO6SahggjYYqCrsz/0HGzA2SFpQFoC8TJW6tIsSlETvCZnvOdLsO0F2uDKnW0JubO2cbrFMzqqqGWjAhaDGPEI3PG4wJMKO7pxknACkZ60YoZhwjXwe+2EYK5/FUusYRzGEDEl96pq6QRxB0JimRC4hiCmKkU9DL9Qhi3zmKxJ5IVGSMe77cYixoJHylDlwDD7LY/BVBrqDuOuCwWfC976dBOsjbQ4ke5CgWrsH4N+jLL91PeQ51NoL8lGSulg4dB4lK7O//wWQfBOljDgAAA==","partition": 1}]}' http://192.168.2.40:18682/topics/KafkaRestTest2
```

- 压力测试

```bash
36.111.140.42机器
cd /home/zhangwusheng
echo '{"records":[{"value":{"foo":"bar"}}]}'  > ./kafka.proxy.data
#json数据

ab -c60 -n50000  -H "Accept: application/vnd.kafka.v2+json" -k -p ./kafka.test.2800 -T "application/vnd.kafka.json.v2+json"  http://192.168.2.40:18682/topics/KafkaRestTest2

#binary数据
ab -c1 -n1  -H "Accept: application/vnd.kafka.v2+json" -k -p kafka-partition-1 -T "application/vnd.kafka.binary.v2+json"  http://192.168.2.40:18682/topics/KafkaRestTest2


curl -X POST -H "Content-Type: application/vnd.kafka.binary.v2+json" -H "Accept: application/vnd.kafka.v2+json" --data '{"records":[{"key":"key1","value":"S2Fma2E=","partition":1}]}' http://192.168.2.40:18682/topics/KafkaRestTest2

ab -c50 -n30000  -H "Accept: application/vnd.kafka.v2+json" -p kafka-partition.txt -T "application/vnd.kafka.binary.v2+json"  http://192.168.2.40:18682/topics/KafkaRestTest2
ab -c50 -n30000  -H "Accept: application/vnd.kafka.v2+json" -p kafka-partition-1 -T "application/vnd.kafka.binary.v2+json"  http://192.168.2.40:18682/topics/KafkaRestTest2

#加上KeepAlive参数，结果就会比较稳定
ab -c50 -n60000 -k -H "Accept: application/vnd.kafka.v2+json" -p $FILENAME -T "application/vnd.kafka.json.v2+json"  http://192.168.2.40:18682/topics/KafkaRestTest2

 ab -c50 -n60000 -k  -H "Accept: application/vnd.kafka.v2+json" -p kafka-bin-684 -T "application/vnd.kafka.binary.v2+json"  http://192.168.2.40:18682/topics/KafkaRestTest2
```

- 压测结果

- [ ]
  格式说明
  	json	数据有效负载为json
  	bin	数据药效负载为二进制数据，传给proxy时需要base64编码
  	bin-partition	上报数据时，指定partition
  	bin-no-partition	上报数据时，不指定partition，由kafka自己轮询

- [ ]  测试说明
        不同的包大小各运行五次

- [ ]
  测试结果


| 并发数 | 记录数 | 字节大小 | Partition | 格式             | 第一次 | 第二次 | 第三次 | 第四次 | 第五次 |      |
| ------ | ------ | -------- | --------- | ---------------- | ------ | ------ | ------ | ------ | ------ | ---- |
| 50     | 60000  | 512      | 10        | json             | 5460   | 5361   | 5377   | 5385   | 5505   |      |
| 50     | 60000  | 760      | 10        | json             | 5414   | 5493   | 5617   | 5586   | 5487   |      |
| 50     | 60000  | 1009     | 10        | json             | 5472   | 5620   | 5246   | 5457   | 5309   |      |
| 50     | 60000  | 1507     | 10        | json             | 5221   | 5303   | 5441   | 5580   | 5484   |      |
| 50     | 60000  | 4246     | 10        | json             | 4668   | 4897   | 4250   | 4784   | 4582   |      |
| 50     | 60000  | 8230     | 10        | json             | 4245   | 4115   | 4171   | 4194   | 4175   |      |
| 50     | 60000  | 79942    | 10        | json             | N/A    | N/A    | N/A    | N/A    | N/A    |      |
|        |        |          |           |                  |        |        |        |        |        |      |
| 50     | 60000  | 684      | 10        | bin              | 5526   | 5611   | 5462   | 5810   | 5772   |      |
| 50     | 60000  | 1016     | 10        | bin              | 5705   | 5529   | 5685   | 5481   | 5716   |      |
| 50     | 60000  | 1376     | 10        | bin              | 5589   | 5559   | 5402   | 5585   | 5585   |      |
| 50     | 60000  | 2040     | 10        | bin              | 5437   | 5496   | 5355   | 5586   | 5607   |      |
| 50     | 60000  | 5692     | 10        | bin              | 5097   | 5036   | 4898   | 5127   | 5192   |      |
| 50     | 60000  | 11004    | 10        | bin              | 4522   | 4370   | 4444   | 4401   | 4342   |      |
|        |        |          |           |                  |        |        |        |        |        |      |
| 50     | 60000  | 200351   | 10        | bin-no-partition | 690    | 699    | 697    | 676    | 695    |      |
| 50     | 60000  | 200960   | 10        | bin-partition    | 663    | 448    | 669    | 527    | 527    |      |
|        |        |          |           |                  |        |        |        |        |        |      |
| 50     | 60000  | 512      | 15        | json             | 5201   | 5579   | 5423   | 5657   | 5667   |      |
| 50     | 60000  | 760      | 15        | json             | 5595   | 5848   | 5617   | 5788   | 5095   |      |
| 50     | 60000  | 1009     | 15        | json             | 5632   | 5461   | 5593   | 5512   | 5806   |      |
| 50     | 60000  | 4246     | 15        | json             | 4967   | 4837   | 4658   | 4804   | 4707   |      |
| 50     | 60000  | 8230     | 15        | json             | 4202   | 4131   | 4207   | 4173   | 4268   |      |
|        |        |          |           |                  |        |        |        |        |        |      |
| 50     | 60000  | 1016     | 15        | bin              | 5849   | 5832   | 5779   | 5658   | 5826   |      |
| 50     | 60000  | 2040     | 15        | bin              | 5204   | 5719   | 5658   | 5483   | 5642   |      |
| 50     | 60000  | 5692     | 15        | bin              | 5115   | 5266   | 5104   | 5245   | 4980   |      |
| 50     | 60000  | 11004    | 15        | bin              | 4572   | 4490   | 4521   | 4695   | 4570   |      |
|        |        |          |           |                  |        |        |        |        |        |      |
| 50     | 60000  | 200351   | 15        | bin-no-partition | 725    | 706    | 695    | 706    | 708    |      |
| 50     | 60000  | 200960   | 15        | bin-partition    | 1153   | 1173   | 1179   | 1151   | 1211   |      |

- [ ] 结论
  1	每秒5000左右的tps
  2	随着数据包大小的增加，tps下降的不是很明显，这个应该是kafka producer端做了缓存有关，tps缓慢下降是因为包逐渐变大，网络传输和数据反序列化需要占用时间
  3	压测数据有时候受到机器负责的影响
  4	bin格式的性能比json格式的稍好，json格式的需要把整个数据都反序列为对象，bin格式的value只是base解码，而无需反序列化为对象，这可能是bin比json稍高的原因
  5	bin格式很大的数据包，ab也能跑出数据，json在数据79K时无法跑出数据
  6	bin格式可以是gzip压缩后再base64的数据，同样的包大小可以承载gzip压缩倍数的有效负载，因此bin更适合数据传输
  7	partition数量由10增加到15时，各个数据均有提升，但是提升幅度不算大
  8	partitin为10时，数据中指定partition比不指定partition（此时kafka roundbin）性能稍好，但是partition数目增加到15时，指定分区性能猛增1倍

- [ ] 建议
  	上报数据时，使用bin上报
    	数据包可选择压缩后10K左右进行上报（每秒48M传输）
    	上报时同时指定partition(可选)

- [ ] TODO：

- 测试Producer的压缩

kafka的配置是**compression.type**，rest的配置是**producer.compression.type**

- 测试Producer幂等性

- > **enable.idempotence**: When set to 'true', the producer will  ensure that exactly one copy of each message is written in the stream.  If 'false', producer retries due to broker failures, etc., may write  duplicates of the retried message in the stream. Note that enabling  idempotence requires `max.in.flight.requests.per.connection` to be less than or equal to 5, `retries` to be greater than 0 and `acks` must be 'all'. If these values are not explicitly set by the user,  suitable values will be chosen. If incompatible values are set, a `ConfigException` will be thrown.
  >
  > - **Type**: boolean
  > - **Default**: false
  > - **Valid Values**:
  > - **Importance**: low
  >
  > `acks`这个会降低吞吐量，`max.in.flight.requests.per.connection`太少可能会导致异常，`retries`倒是个好的设置

- [ ]

# 44.组件部署机器

| 组件                    | Master主机     | 备份主机       |
| ----------------------- | -------------- | -------------- |
| ambari-server           | 192.168.254.40 | 192.168.254.36 |
|                         |                | 192.168.254.39 |
|                         |                | 192.168.254.41 |
|                         |                | 192.168.254.42 |
| KDC                     | 192.168.254.40 | 192.168.254.36 |
|                         |                | 192.168.254.39 |
| pgsql                   | 192.168.254.40 | 192.168.254.36 |
| namenode                | 192.168.254.36 | 192.168.254.39 |
| ZKFaileOver             | 192.168.254.36 | 192.168.254.39 |
| RM                      | 192.168.254.36 | 192.168.254.39 |
| HMaster                 | 192.168.254.36 | 192.168.254.39 |
| ZooKeeper               | 192.168.254.36 |                |
|                         | 192.168.254.39 |                |
|                         | 192.468.254.40 |                |
|                         | 192.468.254.41 |                |
|                         | 192.468.254.42 |                |
| Kylin                   | 192.468.254.41 |                |
|                         | 192.468.254.42 |                |
|                         | 192.468.254.31 |                |
|                         | 192.468.254.32 |                |
| object-log              | 192.468.254.21 | 192.468.254.22 |
| cdn-log                 | 192.468.254.41 | 192.468.254.42 |
| oss-transcode(尚未部署) | 192.468.254.21 | 192.468.254.22 |
| kafka-proxy             |                |                |
| flume                   |                |                |



- ambari-server之间的切换：

https://docs.cloudera.com/HDPDocuments/Ambari-2.7.5.0/administering-ambari/content/amb_populate_the_new_ambari_database.html



# 45.添加新机器

```bash
#建立脚本目录
ansible cdnlog  -m shell -a 'mkdir -p /home/zhangwusheng/scripts/third/'
#备份hosts
ansible thirdnew -m shell -a 'cp /etc/hosts /etc/hosts.`date +%s` '
#幂等操作
ansible thirdnew -m shell -a 'sed -i "/sct-nmg-huhehaote/d" /etc/hosts'
#添加新的机器
ansible thirdnew -m shell -a 'echo "192.168.254.119 sct-nmg-huhehaote2-loganalysis-02.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.127 sct-nmg-huhehaote2-loganalysis-07.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.118 sct-nmg-huhehaote2-loganalysis-03.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.128 sct-nmg-huhehaote2-loganalysis-06.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.120 sct-nmg-huhehaote2-loganalysis-01.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.130 sct-nmg-huhehaote2-loganalysis-04.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.136 sct-nmg-huhehaote2-loganalysis-11.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.129 sct-nmg-huhehaote2-loganalysis-05.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.138 sct-nmg-huhehaote2-loganalysis-09.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.137 sct-nmg-huhehaote2-loganalysis-10.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.139 sct-nmg-huhehaote2-loganalysis-08.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.145 sct-nmg-huhehaote2-loganalysis-15.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.147 sct-nmg-huhehaote2-loganalysis-13.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.146 sct-nmg-huhehaote2-loganalysis-14.in.ctyun.net" >> /etc/hosts'
ansible thirdnew -m shell -a 'echo "192.168.254.148 sct-nmg-huhehaote2-loganalysis-12.in.ctyun.net" >> /etc/hosts'

#40新增防火墙，允许安装ambari
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.29" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.28" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.30" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.37" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.38" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.39" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.40" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.46" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.47" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.48" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.49" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.55" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.56" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.57" port port="8181" protocol="tcp" accept'
firewall-cmd --permanent --add-rich-rule 'rule family="ipv4" source address="182.42.255.58" port port="8181" protocol="tcp" accept'
firewall-cmd --reload
firewall-cmd --list-all


ansible cdnlog -m shell -a 'wget http://192.168.254.40:8181/scripts/third/firewall.sh -O /home/zhangwusheng/scripts/third/firewall.sh'
ansible thirdnew -m shell -a 'bash /home/zhangwusheng/scripts/third/firewall.sh'

#
192.168.254.119 sct-nmg-huhehaote2-loganalysis-02.in.ctyun.net
192.168.254.127 sct-nmg-huhehaote2-loganalysis-07.in.ctyun.net
192.168.254.118 sct-nmg-huhehaote2-loganalysis-03.in.ctyun.net
192.168.254.128 sct-nmg-huhehaote2-loganalysis-06.in.ctyun.net
192.168.254.120 sct-nmg-huhehaote2-loganalysis-01.in.ctyun.net
192.168.254.130 sct-nmg-huhehaote2-loganalysis-04.in.ctyun.net
192.168.254.136 sct-nmg-huhehaote2-loganalysis-11.in.ctyun.net
192.168.254.129 sct-nmg-huhehaote2-loganalysis-05.in.ctyun.net
192.168.254.138 sct-nmg-huhehaote2-loganalysis-09.in.ctyun.net
192.168.254.137 sct-nmg-huhehaote2-loganalysis-10.in.ctyun.net
192.168.254.139 sct-nmg-huhehaote2-loganalysis-08.in.ctyun.net
192.168.254.145 sct-nmg-huhehaote2-loganalysis-15.in.ctyun.net
192.168.254.147 sct-nmg-huhehaote2-loganalysis-13.in.ctyun.net
192.168.254.146 sct-nmg-huhehaote2-loganalysis-14.in.ctyun.net
192.168.254.148 sct-nmg-huhehaote2-loganalysis-12.in.ctyun.net
#

cat /etc/hosts|grep 'sct-nmg-huhehaote2'|awk '{print $2;}'|awk '{print "kylin/"$1;}'


/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "ank -randkey kylin/sct-nmg-huhehaote2-loganalysis-02.in.ctyun.net@CTYUN.NET"

/usr/bin/kadmin -p root/admin -w 'cdnlog@kdc!@#' -q "xst -k /etc/security/keytabs/kylin.keytab kylin/cdnlog002.ctyun.net"
```



# 46.nginx

openresty安装步骤：
wget https://openresty.org/download/openresty-1.33.6.2.tar.gz
tar zxvf openresty-1.33.6.2.tar.gz
cd openresty-1.33.6.2
./configure --prefix=/usr/local/openresty --with-luajit --with-http_iconv_module
make
make install
export PATH=$PATH:/usr/local/openresty/nginx/sbin

# 47.HDFS复制慢

dfs.namenode.blockmanagement.queues.shuffle= true
dfs.namenode.replication.max-streams= 12 默认是2，限制一个datanode复制数量，即一个datanode同时最多有2个block在复制；
dfs.namenode.replication.max-streams-hard-limit=12 默认是4
dfs.namenode.replication.work.multiplier.per.iteration= 4 默认2 / namenode一次调度的数量=该值×datanodes数量，默认为2，即每次处理datanode数量*2个block；

dfs.namenode.replication.max-streams，默认是2，

# 48.dmesg时间转换

```bash
date -d "1970-01-01 UTC `echo "$(date +%s)-$(cat /proc/uptime|cut -f 1 -d' ')+69740.690129"|bc `seconds"
```



# 49.Hbase RsGroup

```bash

#To enable, add the following to your hbase-site.xml and restart your Master:
#first 修改配置

<property>
  <name>hbase.coprocessor.master.classes</name>
  <value>org.apache.hadoop.hbase.rsgroup.RSGroupAdminEndpoint</value>
</property>
<property>
  <name>hbase.master.loadbalancer.class</name>
  <value>org.apache.hadoop.hbase.rsgroup.RSGroupBasedLoadBalancer</value>
</property>

重启hmaster

kinit -kt /etc/security/keytabs/hbase.service.keytab  hbase/cdnlog041.ctyun.net@CTYUN.NET
hbase shell
> add_rsgroup 'tsdb'

move_servers_rsgroup 'tsdb',['sct-nmg-huhehaote2-tsdb-01.in.ctyun.net:16020']
move_servers_rsgroup 'tsdb',['sct-nmg-huhehaote2-tsdb-02.in.ctyun.net:16020']
move_servers_rsgroup 'tsdb',['sct-nmg-huhehaote2-tsdb-03.in.ctyun.net:16020']
move_servers_rsgroup 'tsdb',['sct-nmg-huhehaote2-tsdb-04.in.ctyun.net:16020']
move_servers_rsgroup 'tsdb',['sct-nmg-huhehaote2-loganalysis-15.in.ctyun.net:16020']
move_servers_rsgroup 'tsdb',['sct-nmg-huhehaote2-loganalysis-14.in.ctyun.net:16020']

move_servers_rsgroup 'tsdb',['sct-nmg-huhehaote2-loganalysis-13.in.ctyun.net:16020']
move_servers_rsgroup 'tsdb',['sct-nmg-huhehaote2-loganalysis-12.in.ctyun.net:16020']


create_namespace 'tsdb'
grant 'tsdb','RWXCA','@tsdb'

create 'tsdb:cdn_monitor_tsdb-uid',
  {NAME => 'id', COMPRESSION => 'SNAPPY', BLOOMFILTER => 'ROW',NEW_VERSION_BEHAVIOR => 'true'},
  {NAME => 'name', COMPRESSION => 'SNAPPY', BLOOMFILTER => 'ROW',NEW_VERSION_BEHAVIOR => 'true'},'MEMSTORE_FLUSHSIZE'=>35651584

create 'tsdb:cdn_monitor_tsdb',{NAME => 't', VERSIONS => 1, COMPRESSION => 'SNAPPY', BLOOMFILTER => 'ROW',NEW_VERSION_BEHAVIOR => 'true',TTL => 7776000},SPLITS => ['\x01','\x02','\x03','\x04','\x05','\x06','\x07','\x08','\x09']

create 'tsdb:cdn_monitor_tsdb-tree',{NAME => 't', VERSIONS => 1, COMPRESSION => 'SNAPPY', BLOOMFILTER => 'ROW',NEW_VERSION_BEHAVIOR => 'true'}

create 'tsdb:cdn_monitor_tsdb-meta',{NAME => 'name', COMPRESSION => 'SNAPPY', BLOOMFILTER => 'ROW',NEW_VERSION_BEHAVIOR => 'true'},{NAME => 'count', COMPRESSION => 'NONE', BLOOMFILTER => 'ROW',NEW_VERSION_BEHAVIOR => 'true'},{NAME => 'del', COMPRESSION => 'NONE', BLOOMFILTER => 'ROW',NEW_VERSION_BEHAVIOR => 'true'}

create 'tsdb:cdn_monitor_tsdb-tag', {NAME => 'm', COMPRESSION => 'NONE', BLOOMFILTER => 'ROW'}, {NAME => 'k', COMPRESSION => 'NONE', BLOOMFILTER => 'ROW'}, {NAME => 'v', COMPRESSION => 'NONE', BLOOMFILTER => 'ROW'}

move_tables_rsgroup 'tsdb',['tsdb:cdn_monitor_tsdb-uid']
move_tables_rsgroup 'tsdb',['tsdb:cdn_monitor_tsdb']
move_tables_rsgroup 'tsdb',['tsdb:cdn_monitor_tsdb-tree']
move_tables_rsgroup 'tsdb',['tsdb:cdn_monitor_tsdb-meta']
move_tables_rsgroup 'tsdb',['tsdb:cdn_monitor_tsdb-tag']

hdfs storagepolicies -help

hdfs storagepolicies -setStoragePolicy
hdfs storagepolicies -getStoragePolicy -path <path>

#会递归的设置子目录的
hdfs storagepolicies -setStoragePolicy -policy HOT -path /apps/hbase/data/data/tsdb
hdfs storagepolicies -getStoragePolicy -path /apps/hbase/data/data/tsdb/cdn_monitor_tsdb
```

# 50.Docker升级

```bash
systemctl stop  docker
yum remove docker docker-common docker-selinux docker-engine
 wget http://192.168.254.40:8181/soft/docker-ce-17.12.1.ce-1.el7.centos.x86_64.rpm
 yum install docker-ce-17.12.1.ce-1.el7.centos.x86_64.rpm
 systemctl enable docker && systemctl start docker


 modprobe ip_vs
 cat /proc/net/ip_vs

```



# 51.Rsync

```bash
rpm -qa | grep rsync

cat /etc/rsyncd.conf

uid =  root
gid = root
use chroot = no
max connections = 200
timeout = 300
pid file = /var/run/rsyncd.pid
lock file = /var/run/rsync.lock
log file = /var/log/rsyncd.log
ignore errors
read only = yes
list = yes
hosts allow = 192.168.254.0/24
hosts deny = 0.0.0.0/32
#auth users = rsync_backup
#secrets file = /etc/rsync.password

[ambari]
path = /var/www/html
comment = ftp export area
#ignore errors　　#忽略I/O错误
#read only = no　　#默认为ture,不让客户端上传文件到服务器上.
#list = no
#auth users = zhu　　#虚拟用户
#secrets file = /etc/rsyncd.d/pass.server　　#虚拟用户密码存放地址

# mkdir /etc/rsyncd.d/
# vim /etc/rsysd.d/pass.server
zhu:111
test:111

# chmod 600 /etc/rsyncd.d/pass.server

telnet 192.168.254.40 873

cat /etc/rsync.passwd
111
ll /etc/rsync.passwd
-rw-------. 1 root root 4 Sep  4 01:59 /etc/rsync.passwd

cd /var/www/html
rsync -avz test@192.168.254.40::ambari/* /var/www/html
#--password-file=/etc/rsync.passw
```



# 52.TSDB

```bash
#上传包
ansible tsdbhbase -m shell -a "mkdir -p /home/zhangwusheng/soft/tsdb"

#ansible datanode -m shell -a "groupadd tsdb"
ansible datanode -m shell -a "useradd tsdb -g cdnlog"
ansible datanode -m shell -a "usermod -G hadoop tsdb"

ansible datanode -m shell -a "wget http://192.168.254.40:8181/soft/tsdb/tsdb.keytab -O /etc/security/keytabs/tsdb.keytab"

ansible datanode -m shell -a "ls /etc/security/keytabs/tsdb.keytab"


#ansible thirdnew -m shell -a "groupadd tsdb"
ansible thirdnew -m shell -a "useradd tsdb -g cdnlog"
ansible thirdnew -m shell -a "usermod -G hadoop tsdb"
ansible thirdnew -m shell -a "wget http://192.168.254.40:8181/soft/tsdb/tsdb.keytab -O /etc/security/keytabs/tsdb.keytab"
ansible thirdnew -m shell -a "ls /etc/security/keytabs/tsdb.keytab"


ansible tsdbhbase -m shell -a "wget http://192.168.254.40:8181/soft/tsdb/hbase-server-2.0.2.3.1.0.0-78-patched.jar -O /home/zhangwusheng/soft/hbase-server-2.0.2.3.1.0.0-78-patched.jar"

ansible tsdbhbase -m shell -a "wget http://192.168.254.40:8181/soft/tsdb/tsd-compaction-0.0.1.jar -O /home/zhangwusheng/soft/tsd-compaction-0.0.1.jar"

#替换包
ansible tsdbhbase -m shell -a "cp /home/zhangwusheng/soft/hbase-server-2.0.2.3.1.0.0-78-patched.jar /usr/hdp/3.1.0.0-78/hbase/lib/"
ansible tsdbhbase -m shell -a "cp /home/zhangwusheng/soft/tsd-compaction-0.0.1.jar /usr/hdp/3.1.0.0-78/hbase/lib/"
ansible tsdbhbase -m shell -a "mv /usr/hdp/3.1.0.0-78/hbase/lib/hbase-server-2.0.2.3.1.0.0-78.jar /usr/hdp/3.1.0.0-78/hbase/"

ansible tsdbhbase -m shell -a "rm -f /usr/hdp/3.1.0.0-78/hbase/lib/hbase-server.jar"
ansible tsdbhbase -m shell -a "ln -fs /usr/hdp/3.1.0.0-78/hbase/lib/hbase-server-2.0.2.3.1.0.0-78-patched.jar /usr/hdp/3.1.0.0-78/hbase/lib/hbase-server.jar"
```



# 53.Druid

## 安装

```bash
192.168.2.40:3306
easyscheduler/KLETUadgj1!
cdnlog-dev /cdnlog123@
root/  QETUadgj1!

 mysql -h 192.168.2.40 -u cdnlog-dev -p

 CREATE DATABASE druid DEFAULT CHARACTER SET utf8mb4;

 CREATE USER 'druid'@'192.168.2.%' IDENTIFIED BY 'diurd';

 CREATE USER 'druid' IDENTIFIED BY 'diurd';

 GRANT ALL PRIVILEGES ON druid.* TO 'druid'@'192.168.2.%';

--drop user dolphinscheduler@'192.168.254.%';
--create user 'dolphinscheduler'@'192.168.254.%' identified by 'BL4OUvXtZWefh5Z!';
-- grant all privileges on dolphinscheduler.* to 'dolphinscheduler'@'192.168.254.%' identified by 'BL4OUvXtZWefh5Z!' ;
grant all privileges on druid.* to 'druid'@'192.168.2.%' identified by 'diurd' WITH GRANT OPTION;
FLUSH PRIVILEGES;


192.168.2.44
 root   /   QETUadgj1!


 问题：
1.修改数据库字符编码

alter database druid character set utf8 collate utf8_general_ci;

2.保存mysql新版本的jar包到meta的那个目录和lib目录，都需要
```



下载软件

```bash
wget -c 'https://mirror.bit.edu.cn/apache/druid/0.18.1/apache-druid-0.18.1-bin.tar.gz'

#下载至/home/zhangwusheng/soft/hadoop
put apache-druid-0.18.1-bin.tar.gz

cd /home/zhangwusheng/soft
tar zxvf /home/zhangwusheng/soft/hadoop/apache-druid-0.18.1-bin.tar.gz -C /home/zhangwusheng/soft

#kdc增加druid用户，这个是ambari自己增加好了。生产需要自己增加这一步
ansible cdnlog -m shell -a "chmod a+r /etc/security/keytabs/druid.headless.keytab"


#建立数据目录
ansible cdnlog -m shell -a "mkdir -p /data1/zhangwusheng/druid;chown -R zhangwusheng:zhangwusheng /data1/zhangwusheng"
ansible cdnlog -m shell -a "mkdir -p /data2/zhangwusheng/druid;chown -R zhangwusheng:zhangwusheng /data2/zhangwusheng"
ansible cdnlog -m shell -a "mkdir -p /data3/zhangwusheng/druid;chown -R zhangwusheng:zhangwusheng /data3/zhangwusheng"
ansible cdnlog -m shell -a "mkdir -p /data4/zhangwusheng/druid;chown -R zhangwusheng:zhangwusheng /data4/zhangwusheng"
ansible cdnlog -m shell -a "mkdir -p /data5/zhangwusheng/druid;chown -R zhangwusheng:zhangwusheng /data5/zhangwusheng"
ansible cdnlog -m shell -a "mkdir -p /data6/zhangwusheng/druid;chown -R zhangwusheng:zhangwusheng /data6/zhangwusheng"
ansible cdnlog -m shell -a "mkdir -p /data7/zhangwusheng/druid;chown -R zhangwusheng:zhangwusheng /data7/zhangwusheng"
ansible cdnlog -m shell -a "mkdir -p /data8/zhangwusheng/druid;chown -R zhangwusheng:zhangwusheng /data8/zhangwusheng"
ansible cdnlog -m shell -a "mkdir -p /data9/zhangwusheng/druid;chown -R zhangwusheng:zhangwusheng /data9/zhangwusheng"
ansible cdnlog -m shell -a "mkdir -p /data10/zhangwusheng/druid;chown -R zhangwusheng:zhangwusheng /data10/zhangwusheng"


ansible cdnlog -m shell -a "mkdir -p /data1/zhangwusheng/druid/var/logs/druid;mkdir -p /data1/zhangwusheng/druid/var/druid;mkdir -p /data1/zhangwusheng/druid/var/tmp;mkdir -p /data1/zhangwusheng/druid/var/sv;chown -R zhangwusheng:zhangwusheng /data1/zhangwusheng"
#zk建立目录
/usr/hdp/current/zookeeper-client/bin/zkCli.sh -server ctl-nm-hhht-yxxya6-ceph-027.ctyuncdn.net:12181 create /druid_018_20200603 "zwscreated"

#建立hdfs目录
hdfs dfs -mkdir -p /apps/druid_018_20200603/warehouse
hdfs dfs -chown -R druid:druid /apps/druid_018_20200603
hdfs dfs -ls /apps/

hdfs dfs -mkdir -p /user/druid_018_20200603/logs
hdfs dfs -chown -R druid:druid  /user/druid_018_20200603

#把hadoop的xml建立软链
ln -fs /etc/hadoop/3.1.0.0-78/0/core-site.xml /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/_common/hadoop-xml/core-site.xml
ln -fs /etc/hadoop/3.1.0.0-78/0/hdfs-site.xml /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/_common/hadoop-xml/hdfs-site.xml
ln -fs /etc/hadoop/3.1.0.0-78/0/mapred-site.xml  /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/_common/hadoop-xml/mapred-site.xml
ln -fs /etc/hadoop/3.1.0.0-78/0/yarn-site.xml /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/_common/hadoop-xml/yarn-site.xml


# cat druid-env.sh
#!/bin/bash
# Set DRUID specific environment variables here.
# The java implementation to use.
export JAVA_HOME=/usr/local/jdk
export PATH=$JAVA_HOME/bin:$PATH
#export DRUID_PID_DIR=/var/run/druid
#export DRUID_LOG_DIR=/var/log/druid
#export DRUID_CONF_DIR=/usr/hdp/current/druid-coordinator/conf
#export DRUID_LIB_DIR=/usr/hdp/current/druid-coordinator/lib
#export HADOOP_CONF_DIR=/usr/hdp/3.1.0.0-78/hadoop/conf
export HADOOP_HOME=/usr/hdp/3.1.0.0-78/hadoop

#vi /home/zhangwusheng/apache-druid-0.18.1/bin/run-druid
#line 38 增加
echo "==============================================="
echo "CONFDIR=${CONFDIR}"
source /home/zhangwusheng/apache-druid-0.18.1/conf/druid-env.sh
echo "==============================================="


cp /var/www/html/soft/zwssoft/hadoop/apache-druid-0.18.1-bin.tar.gz /var/www/html/soft
#发布软件到全网
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/apache-druid-0.18.1-bin.tar.gz -O /home/zhangwusheng/soft/apache-druid-0.18.1-bin.tar.gz"

ansible cdnlog -m shell -a "tar zxvf /home/zhangwusheng/soft/apache-druid-0.18.1-bin.tar.gz -C /home/zhangwusheng/"

ansible cdnlog -m shell -a "ls /home/zhangwusheng"

#发布环境变量
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/druid-env.sh -O /home/zhangwusheng/apache-druid-0.18.1/conf"

#发布mysql包
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/mysql-connector-java-5.1.49.jar  -O /home/zhangwusheng/apache-druid-0.18.1/lib/mysql-connector-java-5.1.49.jar"

ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/mysql-connector-java-5.1.49.jar  -O /home/zhangwusheng/apache-druid-0.18.1/extensions/mysql-metadata-storage/mysql-connector-java-5.1.49.jar"

#发布修改的脚本
#这里增加了 source druid-env
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/run-druid -O /home/zhangwusheng/apache-druid-0.18.1/bin/run-druid"
#这里修改了输出的日志目录
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/start-cluster-master-no-zk-server  -O /home/zhangwusheng/apache-druid-0.18.1/bin/start-cluster-master-no-zk-server "

ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/start-cluster-query-server  -O /home/zhangwusheng/apache-druid-0.18.1/bin/start-cluster-query-server"

ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/start-cluster-data-server  -O /home/zhangwusheng/apache-druid-0.18.1/bin/start-cluster-data-server"


ssh -p 9000 192.168.254.21 '/usr/bin/kadmin -p root/admin -w "cdnlog@kdc!@#" -q "xst -k /etc/security/keytabs/druid.keytab kylin/cdnlog003.ctyun.net"'


####
cat druid_jaas.conf
KafkaClient {
   com.sun.security.auth.module.Krb5LoginModule required
   useKeyTab=true
   keyTab="/etc/security/keytabs/druid.headless.keytab"
   storeKey=true
   useTicketCache=false
   serviceName="kafka"
   principal="druid-cdnlog@CTYUNCDN.NET";
};

#发布jaas
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/druid_jaas.conf -O /home/zhangwusheng/apache-druid-0.18.1/conf/druid_jaas.conf"


#这个版本的度量需要自己编译出来，所以先删掉
ansible cdnlog -m shell -a "rm -f /home/zhangwusheng/apache-druid-0.18.1/extensions/ambari-metrics-emitter"

ansible cdnlog -m shell -a "ln -fs /usr/hdp/3.1.0.0-78/druid/extensions/ambari-metrics-emitter /home/zhangwusheng/apache-druid-0.18.1/extensions/ambari-metrics-emitter"


#####注意修改hosts
##common配置
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/common.runtime.properties -O /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/_common/common.runtime.properties"

ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/modify-common-host.sh -O /home/zhangwusheng/apache-druid-0.18.1/bin/modify-common-host.sh"

ansible cdnlog -m shell -a "bash /home/zhangwusheng/apache-druid-0.18.1/bin/modify-common-host.sh"

ansible cdnlog -m shell -a "grep druid.host /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/_common/common.runtime.properties"

cp /usr/hdp/3.1.0.0-78/druid/conf/druid_jaas.conf /var/www/html/soft/druid/
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/druid_jaas.conf -O /home/zhangwusheng/apache-druid-0.18.1/conf/druid_jaas.conf"

#middleManager配置
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/middleManager-jvm.config -O /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/data/middleManager/jvm.config"

ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/middleManager-runtime.properties -O /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/data/middleManager/runtime.properties"

# historical配置
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/historical-jvm.config -O /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/data/historical/jvm.config"

ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/historical-runtime.properties -O /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/data/historical/runtime.properties"

#broker配置
ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/broker-jvm.config -O /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/query/broker/jvm.config"

ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/broker-runtime.properties -O /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/query/broker/runtime.properties"

#master配置

ansible cdnlog -m shell -a "wget http://192.168.2.40:17080/soft/druid/coordinator-overlord-jvm.config -O /home/zhangwusheng/apache-druid-0.18.1/conf/druid/cluster/master/coordinator-overlord/jvm.config"

#修改目录权限
ansible cdnlog -m shell -a "chown -R zhangwusheng:zhangwusheng /home/zhangwusheng/apache-druid-0.18.1"

#启动程序

 nohup /home/zhangwusheng/apache-druid-0.18.1/bin/start-cluster-master-no-zk-server &

 nohup /home/zhangwusheng/apache-druid-0.18.1/bin/start-cluster-query-server &

 nohup /home/zhangwusheng/apache-druid-0.18.1/bin/start-cluster-data-server &


#验证数据库是否创建
root/QETUadgj1!

mysql -h 192.168.2.44 -u root -p
use druid_018_20200603;
show tables;

#下载 ambari插件
https://repo1.maven.org/maven2/org/apache/druid/extensions/contrib/ambari-metrics-emitter/0.18.1/


#修改代码，处理
druid.segmentCache.locationSelectorStrategy=mostAvailableSize

#建立tmp目录
java.io.tmpdir=/data1/druid_18/tmp
#启动logrotate
```



测试

```bash
导入csv
#第一行要有header
导入kadka

ZK_CONN="ctl-nm-hhht-yxxya6-ceph-028.ctyuncdn.net:12181/kafka-auth-test-1"
userName="DebugTopic"
topicName="zws-druid-test"

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}   --topic zws-druid-test    --partitions 30 --replication-factor 3


#授权可写
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${userName} --topic ${topicName}   --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}
#授权可读
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${userName} --topic ${topicName}   --consumer --group grp-${userName}

/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667  --topic ${topicName} --producer-property security.protocol=SASL_PLAINTEXT --producer-property sasl.mechanism=PLAIN < /home/zhangwusheng/apache-druid-0.18.1/quickstart/tutorial/zws-2015-09-12.json

#修改好consumer的kafka_client_jaas_conf，然后修改好consumer.properties
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667  --topic  ${topicName} --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property sasl.mechanism=PLAIN --consumer-property  auto.offset.reset=earliest --consumer-property group.id=grp-${userName} --consumer-property client.id=zws-druid-consumer --from-beginning


{
  "security.protocol":"SASL_PLAINTEXT",
  "sasl.mechanism":"PLAIN",
  "client.id":"zws-druid-consumer",
  "group.id":"grp-DebugTopic"
}


  "auto.offset.reset":"latest",



  #转换数据
  CREATE EXTERNAL TABLE `druid_202005`(
  `client_id` int  ,
  `protocol_type` tinyint  ,
  `product_code` tinyint  ,
  `channel` string  ,
  `province_code` int  ,
  `isp_code` tinyint  ,
  `vendor_code` tinyint  ,
  `http_code` int  ,
  `netflag_type` tinyint  ,
  `event_time` int  ,
  `req_cnt` int  ,
  `hit_req_cnt` int  ,
  `miss_req_cnt` int  ,
  `pv_req_cnt` int  ,
  `flow` bigint  ,
  `hit_flow` bigint  ,
  `miss_flow` bigint  ,
  `int_flag` tinyint  ,
  `hosting_type` tinyint  ,
  `response_time` bigint,
  `city_code` int,
  `county_code` int,
  `lake_id` int)
PARTITIONED BY (
  `proc_time` string  )
ROW FORMAT SERDE
  'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.SequenceFileInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveSequenceFileOutputFormat'


ALTER TABLE druid_202005 ADD IF NOT EXISTS PARTITION (proc_time='202005010000') LOCATION '/apps/druid_018_20200603/202005/01/00/00';

 CREATE EXTERNAL TABLE `druid_parquet_202005`(
  `client_id` int  ,
  `protocol_type` tinyint  ,
  `product_code` tinyint  ,
  `channel` string  ,
  `province_code` int  ,
  `isp_code` tinyint  ,
  `vendor_code` tinyint  ,
  `http_code` int  ,
  `netflag_type` tinyint  ,
  `event_time` int  ,
  `req_cnt` int  ,
  `hit_req_cnt` int  ,
  `miss_req_cnt` int  ,
  `pv_req_cnt` int  ,
  `flow` bigint  ,
  `hit_flow` bigint  ,
  `miss_flow` bigint  ,
  `int_flag` tinyint  ,
  `hosting_type` tinyint  ,
  `response_time` bigint,
  `city_code` int,
  `county_code` int,
  `lake_id` int)
PARTITIONED BY (
  `proc_time` string)
ROW FORMAT SERDE
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS INPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION
  'hdfs://cdnlog/tmp/202005/druid_parquet_202005.db'

insert overwrite table druid_parquet_202005 partition  (proc_time='202005010000')
select client_id,protocol_type,product_code,channel,province_code,isp_code,vendor_code,http_code,netflag_type,event_time,req_cnt
,hit_req_cnt,miss_req_cnt,pv_req_cnt,flow,hit_flow,miss_flow,int_flag,hosting_type,response_time,city_code,county_code,lake_id
from druid_202005 where proc_time='202005010000'
```

***必须注意的问题：***

1. logrotate
2. cache的目录配置

否则很容易引起磁盘满的问题！！！



```bash

DSQL:
./dsql --host http://ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:18888 --execute "SELECT  clientId,protocolType,productCode,channel,province,city,county,ispCode from \"cdn-log-analysis-realtime-dev-rollup\" WHERE \"eventTime\" = 1594456260"

```



## 每日查询

```bash
SELECT TIME_FLOOR("__time", 'PT5M'), SUM("upFlow")
FROM "cdn-log-tencent"
WHERE "__time" >= CURRENT_TIMESTAMP - INTERVAL '1' DAY GROUP BY TIME_FLOOR("__time", 'PT5M') ORDER BY TIME_FLOOR("__time", 'PT5M') DESC


SELECT "__time", SUM(reqCnt)/60, SUM(flow)*8/60
FROM "cdn-log-common"
WHERE "__time" >= CURRENT_TIMESTAMP - INTERVAL '1' DAY AND channel= 'vcode-api.vivo.com.cn' and vendorCode = 1 GROUP BY __time
ORDER BY "__time" DESC

```

手工compact

```bash
覃国幸(365099489)  16:17:17
{
    "type": "compact",
    "dataSource": "cdn-log-uv",


     "interval" : "2020-11-23T00:00:00.000Z/2020-12-01T00:00:00.000Z" }

覃国幸(365099489)  16:17:31
http://cdnlog002.ctyun.net:28081/druid/indexer/v1/task

覃国幸(365099489)  16:17:34
post方法

覃国幸(365099489)  16:18:01
uv时间间隔可以长一点，common因为量比较大，我之前是一天一天提交的

覃国幸(365099489)  16:18:36
之前提交一个月的失败了


```



## 扩容

```bash
1. 修改 ulimit

/etc/security/limits.d/20-nproc.conf
```





# 54.手工修改Hive元数据



```bash
#新建目录
hdfs  dfs -mkdir /tmp/zws_cdn_log_parquet2/

hdfs  dfs -mkdir /tmp/zws_cdn_log_parquet3/

#hive建表
CREATE EXTERNAL TABLE `zws_cdn_log_parquet3`(
client_id bigint,
protocol_type tinyint,
product_code tinyint,
channel string,
province_code int,
isp_code int,
vendor_code tinyint,
http_code int,
netflag_type tinyint,
event_time int,
req_cnt int,
hit_req_cnt int,
miss_req_cnt int,
pv_req_cnt int,
flow bigint,
hit_flow bigint,
miss_flow bigint,
int_flag tinyint,
hosting_type tinyint,
response_time bigint,
city_code int,
county_code int,
lake_id int
)
 PARTITIONED BY (
   `dateminute` string)
 ROW FORMAT SERDE
   'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
 STORED AS INPUTFORMAT
   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'
 OUTPUTFORMAT
   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
 LOCATION
   '/tmp/zws_cdn_log_parquet3'
   ;

hdfs dfs -mkdir /tmp/zws_cdn_log_sequence3;

CREATE EXTERNAL TABLE `zws_cdn_log_sequence3`(
client_id bigint,
protocol_type tinyint,
product_code tinyint,
channel string,
province_code int,
isp_code int,
vendor_code tinyint,
http_code int,
netflag_type tinyint,
event_time int,
req_cnt int,
hit_req_cnt int,
miss_req_cnt int,
pv_req_cnt int,
flow bigint,
hit_flow bigint,
miss_flow bigint,
int_flag tinyint,
hosting_type tinyint,
response_time bigint,
city_code int,
county_code int,
lake_id int
)
 PARTITIONED BY (
   `dateminute` string)
 ROW FORMAT SERDE
   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
 STORED AS INPUTFORMAT
   'org.apache.hadoop.mapred.SequenceFileInputFormat'
 OUTPUTFORMAT
   'org.apache.hadoop.hive.ql.io.HiveSequenceFileOutputFormat'
 LOCATION
   '/tmp/zws_cdn_log_sequence3'
   ;


   insert overwrite  table zws_cdn_log_sequence3 partition(dateminute='202005312355')
   select
client_id ,protocol_type ,product_code ,channel ,province_code ,isp_code ,vendor_code ,
http_code ,netflag_type ,event_time ,req_cnt ,hit_req_cnt ,miss_req_cnt ,pv_req_cnt ,
flow ,hit_flow ,miss_flow ,int_flag ,hosting_type ,response_time ,city_code ,county_code ,
lake_id
   from zws_cdn_log_parquet3 where
   dateminute='202005312355'





alter table zws_cdn_log_parquet3 add partition (dateminute='202005312355') location '/tmp/202005/druid_parquet_202005.db/proc_time=202005312355';
#mysql元数据修改

select "TBL_ID","OWNER","SD_ID","TBL_NAME" from "TBLS" where "TBL_NAME"='zws_cdn_log_parquet3';
29519	cdnlog-dev	153338	zws_cdn_log_origin

select "SD_ID","CD_ID","SERDE_ID" from "SDS" where "SD_ID"=153338;

153338	44062	153338

select * from "COLUMNS_V2" where "CD_ID"=44062 order by "INTEGER_IDX";





```



# 55.安装GCC

```bash
sudo yum install centos-release-scl


yum install centos-release-scl
yum install devtoolset-8
scl enable devtoolset-8 -- bash
enable the tools:
source /opt/rh/devtoolset-8/enable
```

# 56.Kafka死锁排查

- 死锁排查

```bash
ps -ef|grep 'kafka.Kafka'

#有的时候没有反应
jstack 4800 > /home/zhangwusheng/data/4800.kafka.jstack
jstack -F 4800 > /home/zhangwusheng/data/4800.kafka.jstack

ls -al /home/zhangwusheng/data/4800.kafka.jstack
sz -bye   /home/zhangwusheng/data/4800.kafka.jstack

```
- 成都环境升级

```

int-chengdu-loganalysis-125-ecloud.com:2181

#白山云直播
topicName=zws-upgrade-test
ZK_CONN="int-chengdu-loganalysis-125-ecloud.com:2181"
KAFKA_USER="zws-upgrade-test"

/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list int-chengdu-loganalysis-125-ecloud.com:6667  --topic ${topicName} < /data2/zhangwusheng/messages

nohup /usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server int-chengdu-loganalysis-125-ecloud.com:6667  --topic ${topicName} --from-beginning --group grp5-${KAFKA_USER} > /data2/zhangwusheng/messages5.log &

/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --list --zookeeper ${ZK_CONN}

#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 5 --replication-factor 3

/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  int-chengdu-loganalysis-125-ecloud.com:6667   --topic ${topicName} --from-beginning --group grp-${KAFKA_USER}

/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list int-chengdu-loganalysis-125-ecloud.com:6667  --topic ${topicName}

#------------------------------------------------------------------------
#成都的按时没有加上授权
#
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${KAFKA_USER} --topic ${topicName}   --consumer --group grp-${KAFKA_USER}


#验证数据
#/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  cdnlog003.ctyun.net:5044    --topic ${topicName} --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-${KAFKA_USER}

```

- 开发环境升级

```bash
#第一步
新增自定义变量，可以尝试重启一下kafka，看看是否正常
inter.broker.protocol.version
设置为2.0

#第二步
#每台机器操作
下载新版本2.2.2
wget http://192.168.2.40:17080/soft/kafka_2.11-2.2.2.tgz -O /home/zhangwusheng/soft/kafka_2.11-2.2.2.tgz

#停掉kafka，然后
tar zxvf /home/zhangwusheng/soft/kafka_2.11-2.2.2.tgz -C  /home/zhangwusheng/soft
cp -R /home/zhangwusheng/soft/kafka_2.11-2.2.2/libs /usr/hdp/3.1.0.0-78/kafka/libs-2.2.2
mv /usr/hdp/3.1.0.0-78/kafka/libs /usr/hdp/3.1.0.0-78/kafka/libs-2.0.0
ln -fs /usr/hdp/3.1.0.0-78/kafka/libs-2.2.2 /usr/hdp/3.1.0.0-78/kafka/libs
ls -al /usr/hdp/3.1.0.0-78/kafka

grep version /usr/hdp/current/kafka-broker/conf/server.properties

tail -f /data10/var/log/kafka/server.log

#第三步
inter.broker.protocol.version
设置为2.2
```

# 57.Kafka升级

## 1.问题

线上最近Kafka频繁出问题，原因是因为CLOSE_WAIT过高，在解决的过程中发现了有可能是Kafka的BUG引起来的，而线上采用直连kafka的方式，随着直连的机器越来越过（目前1200台左右），后续引发问题的可能性更大，因此决定首先针对此BUG进行版本升级。

## 2.版本选择：

https://issues.apache.org/jira/browse/KAFKA-7697      Possible deadlock in kafka.cluster.Partition

https://issues.apache.org/jira/browse/KAFKA-7538      Improve locking model used to update ISRs and HW

后查到2.1.0和2.1.1继续有BUG

![img](/img/N2DWD_POSZ4E87XZ67DGY%W.png)



![image-20200730092031276](/img/image-20200730092031276.png)

2.2.0的RELEASE LOG里面

![image-20200730092222447](/img/image-20200730092222447.png)

说明BUG可能仍然未得到解决，查看2.2.1和2.2.2的RELEASE LOG，发现2.2.2解决的BUG比2.2.1少，说明此时版本相对比较稳定，因此选择2.2.2版本进行升级



## 3.参考文档以及步骤

https://kafka.apache.org/22/documentation.html#upgrade

主要参考如下步骤

> ### [1.5 Upgrading From Previous Versions](https://kafka.apache.org/22/documentation.html#upgrade)
>
> #### [Upgrading from 0.8.x, 0.9.x, 0.10.0.x, 0.10.1.x, 0.10.2.x, 0.11.0.x, 1.0.x, 1.1.x, 2.0.x or 2.1.x to 2.2.0](https://kafka.apache.org/22/documentation.html#upgrade_2_2_0)
>
> **If you are upgrading from a version prior to 2.1.x, please see the note below about the change to the schema used to store consumer  offsets.    Once you have changed the inter.broker.protocol.version to the  latest version, it will not be possible to downgrade to a version prior  to 2.1.**
>
> **For a rolling upgrade:**
>
> 1.  Update server.properties on all brokers and add the following  properties. CURRENT_KAFKA_VERSION refers to the version you        are upgrading from. CURRENT_MESSAGE_FORMAT_VERSION refers to the message format version currently in use. If you have previously        overridden the message format version, you should keep its  current value. Alternatively, if you are upgrading from a version prior        to 0.11.0.x, then CURRENT_MESSAGE_FORMAT_VERSION should be set  to match CURRENT_KAFKA_VERSION.
>
>    - inter.broker.protocol.version=CURRENT_KAFKA_VERSION (e.g. 0.8.2, 0.9.0, 0.10.0, 0.10.1, 0.10.2, 0.11.0, 1.0, 1.1).
>    - log.message.format.version=CURRENT_MESSAGE_FORMAT_VERSION  (See [potential performance impact                 following the upgrade](https://kafka.apache.org/22/documentation.html#upgrade_10_performance_impact) for the details on what this configuration does.)
>
>    ​        If you are upgrading from 0.11.0.x, 1.0.x, 1.1.x, or 2.0.x and  you have not overridden the message format, then you only need to  override        the inter-broker protocol version.
>
>    - inter.broker.protocol.version=CURRENT_KAFKA_VERSION (0.11.0, 1.0, 1.1, 2.0).
>
> 2.  Upgrade the brokers one at a time: shut down the broker, update the code, and restart it. Once you have done so, the        brokers will be running the latest version and you can verify  that the cluster's behavior and performance meets expectations.        It is still possible to downgrade at this point if there are any problems.
>
> 3.  Once the cluster's behavior and performance has been verified, bump the protocol version by editing        `inter.broker.protocol.version` and setting it to 2.2.
>
> 4.  Restart the brokers one by one for the new protocol version to take effect. Once the brokers begin using the latest        protocol version, it will no longer be possible to downgrade the cluster to an older version.
>
> 5.  If you have overridden the message format version as instructed above, then you need to do one more rolling restart to        upgrade it to its latest version. Once all (or most) consumers have been upgraded to 0.11.0 or later,        change log.message.format.version to 2.2 on each broker and restart them one by one. Note that the older Scala clients,        which are no longer maintained, do not support the message format introduced in 0.11, so to avoid conversion costs        (or to take advantage of [exactly once semantics](https://kafka.apache.org/22/documentation.html#upgrade_11_exactly_once_semantics)),        the newer Java clients must be used.
>
> ##### [Notable changes in 2.2.1](https://kafka.apache.org/22/documentation.html#upgrade_221_notable)
>
> - Kafka Streams 2.2.1 requires 0.11 message format or higher and does not work with older message format.
>
> ##### [Notable changes in 2.2.0](https://kafka.apache.org/22/documentation.html#upgrade_220_notable)
>
> - The default consumer group id has been changed from the empty string (`""`) to `null`. Consumers who use the new default group id will not be able to  subscribe to topics,        and fetch or commit offsets. The empty string as consumer group  id is deprecated but will be supported until a future major release. Old clients that rely on the empty string group id will now        have to explicitly provide it as part of their consumer config.  For more information see        [KIP-289](https://cwiki.apache.org/confluence/display/KAFKA/KIP-289%3A+Improve+the+default+group+id+behavior+in+KafkaConsumer).
> - The `bin/kafka-topics.sh` command line tool is now able to connect directly to brokers with `--bootstrap-server` instead of zookeeper. The old `--zookeeper`        option is still available for now. Please read [KIP-377](https://cwiki.apache.org/confluence/display/KAFKA/KIP-377%3A+TopicCommand+to+use+AdminClient) for more information.
> - Kafka Streams depends on a newer version of RocksDBs that requires MacOS 10.13 or higher.



## 4.测试环境实施过程

1. 新建一个topic，使用console-producer写入一批数据，测试使用
2. 下载kafka新版程序包    https://www.apache.org/dyn/closer.cgi?path=/kafka/2.2.2/kafka_2.11-2.2.2.tgz
3. 将kafka_2.11-2.2.2.tgz解压后，将libs目录拷贝到/usr/hdp/3.1.0.0-78/kafka，命名为libs-2.2.2
4. 通过Ambari新增参数inter.broker.protocol.version为2.0
5. 停掉单台Kafka Broker
6. 将/usr/hdp/3.1.0.0-78/kafka/libs重命名为/usr/hdp/3.1.0.0-78/kafka/libs-2.0.0
7. 将/usr/hdp/3.1.0.0-78/kafka/libs-2.2.2软链到/usr/hdp/3.1.0.0-78/kafka/libs
8. 启动单台kafka broker，查看启动日志是否正常
9. 使用console-producer和console-consumer验证是否读写数据正常
10. 循环5-9，直到所有的broker全部重启完毕。开发
12. 循环5-9，直到所有的broker全部重启完毕。



## 5.需要继续验证的步骤

1. 验证升级期间，streaming是否能够正常工作
2. 验证升级期间，外部客户的数据写入是否会受到影响
3. 高并发写入，查看是否会出现CLOSE_WAIT的情况
4. 验证回滚情况（重要）



# 58.Fluentd Docker操作

- 准备基础镜像：

```bash
开发40机器：(需要login，赞煌有权限)

docker pull registry.ctzcdn.com/log/fluentd:v2.2.2

docker tag registry.ctzcdn.com/log/fluentd:v2.2.2  harbor.ctyuncdn.cn/cdn-log-fluentd/fluentd:v2.2.2

docker login harbor.ctyuncdn.cn

docker push harbor.ctyuncdn.cn/cdn-log-fluentd/fluentd:v2.2.2
```

- 西安测试环境：

```bash
增加nginx.fluent-xian-test-env.conf，修改kafka连接串
增加三个文件
fluentd-xian-test-env.conf
nginx.fluent-xian-test-env.conf
start-xian-test-env.sh
从各自的文件进行Copy。

yum -y install docker
systemctl start docker

#开发环境构建镜像
cd /home/zhangwusheng/soft/fluentd/2020-07-13/xian-test-env
docker build -t harbor.ctyuncdn.cn/cdn-log-fluentd/cdn-fluentd-collect:xian-test-v20200804-1 .
#导出到本地，便于上传到其他环境的机器
docker save c9738d74b998 > fluentd_xian.tar
gzip fluentd_xian.tar

#西安环境，导入镜像
上传fluentd_xian.tar.gz到西安环境，然后
gunzip fluentd_xian.tar.gz
#load it to images
docker load < fluentd_xian.tar
#tag it
docker tag c9738d74b998 fluentd/xian:v20200804

#HOSTNAME=`hostname -f`
mkdir /home/zhangwusheng/nginx-logs
touch /home/zhangwusheng/nginx-logs/nginx.log

#-p 192.168.254.100:$HOST_PORT:8585 \
#-v /etc/security/keytabs/tsdb.keytab:/etc/security/keytabs/tsdb.keytab \

sudo docker run -dit \
-v /home/zhangwusheng/nginx-logs/nginx.log:/fluentd/nginx/access.log \
-v /etc/hosts:/etc/hosts \
-e HOST_NAME=$HOSTNAME \
--cpus=4 \
-m 2G \
--name="$HOSTNAME" \
fluentd/xian:v20200804

docker ps -a

docker exec -it 76c4af8ccae2 /bin/sh
ls -al /fluentd/nginx/access.log


firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=172.17.0.2/16 accept'
firewall-cmd --reload



/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list  ecm-b254-011.ctyunxian.cn:6667  --topic ctYun


#########
echo '[12/May/2020:14:50:36 +0800]"8999999999999999999999999"200"1589266236.415"0.002"0.000"0.000"0.002"0"172.17.0.2"80"172.17.0.1"48482"GET"http"www.fakeclient.com"http://www.fakeclient.com/4K.file"HTTP/1.1"168"4096"4421"4096"172.17.0.4:8886"200"0.000"-"-"-"-"-"application/octet-stream"-"curl/7.58.0"-"-"-"-"-"-"-"haobai88888"' >> /home/zhangwusheng/nginx-logs/nginx.log

##########

/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  ecm-b254-011.ctyunxian.cn:6667    --topic ctYun --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-ctyun

##########
for i in `seq 1 10000`
do
for j in `seq 1 5`
do
echo '[12/May/2020:14:50:36 +0800]"8999999999999999999999999"200"1589266236.415"0.002"0.000"0.000"0.002"0"172.17.0.2"80"172.17.0.1"48482"GET"http"www.fakeclient.com"http://www.fakeclient.com/4K.file"HTTP/1.1"168"4096"4421"4096"172.17.0.4:8886"200"0.000"-"-"-"-"-"application/octet-stream"-"curl/7.58.0"-"-"-"-"-"-"-"haobai88888"' >> /home/zhangwusheng/nginx-logs/nginx.log
done
done
```



# 59.知识分享点(积跬步,成千里)

有能够 运行的代码demo,有基本的原理说明,每次分享10-15分钟

1. kafka常用基本命令
2. kafka mirror的测试过程
3. parquet文件格式
4. orc文件格式
5. hdfs存储策略以及验证方式
6. JDK threadlocal的

  7.curator recipe知识分享

8. JDK 并发包源码分享

9. Guice基础使用分享(multibinder)/scop

10. docker基本命令分享
11. 跳表分享
12.  一致性hash分享
13. 布隆过滤器分享
14. awk常用技巧分享
15. sed常用技巧分享
16. guice aop分享
17. spring aop分享
18. protobuf使用以及service分享
19. TriTree分享
20. ambari插件编写和安装,调试
21. hbase表备份和恢复(全量和增量)
22. Hbase表迁移
23. hyperloglog分享
24. thrift编写service
25. roaringbitmap
26. hashwheeltimer
27. jmeter使用
28. jmh使用
29. clickhouse分布式表的使用
30. kafkaproxy的使用,原理介绍
31. java常用jdk工具jstack,jconsole,jmap，jstat,eclipse memory analysizer常用负载过高和内存过高
32. 开源组件的自带性能测试工具(hbase,kafka,hadoop)
33. mysql binlog、主从搭建，基于gtid的复制
34. netty编写基本网络程序（网络基本参数的设置，主动断开，被动断开，断开重连，主动发起多个连接的处理）
35. netty解析mysql binlog等
36. canal binlog接入
37. tungsent 如何处理binlog数据？（hive sql）
38. flume的使用（详细一点）
39. springboot相关（不好拆分？）
40. druid命令行解析（类似git命令组io.airlift.airline）
41. lua基础知识分享
42. 均匀分布的随机数分享
43. 测试相关（需要细分）？
44. livy提交管理spark？
45. hbase rit处理
46. ES相关？（需要细分）
47. devops相关（那张图，工具链？）
48. Kerberos相关原理.以及备份和恢复
49. postgresql的复制
50. jmxterm？
51. Guice scope？



# 60.开发规范

## 1.框架选型：

1. web后台程序使用springboot
2. webserver使用jetty不用tomcat
3. json使用jackson
5. 命令行程序使用依赖注入框架(spring/guice)
6. zk使用curator框架

## 2.代码管理：

主要代码规范参考《阿里巴巴java开发手册1.6-泰山版.pdf》
6. gitlab目录按照***<u>功能架构</u>***来组织
7. 提交的代码，必须通过sonar+阿里p3c扫描
8. 开发流程管理使用giflow
9. 新提交的代码测试覆盖率必须达到A以上
10. 文档必须有changelog，里面包含：1需求连接，2改动点 3关联的版本号
11. 各个程序目录结构必须统一，包含bin,conf,logs等常见目录
12. 系统gitlab版本号，程序运行版本号，制品版本号，三者必须统一
13. hadoop等开源组件的配置文件，严禁copy到应用程序目录（docker除外）
14. 配置统一使用配置中心，配置中心地址通过环境变量进行共享
15. 接口统一使用yapi进行管理
16. codereview首先由各领域开发小组进行，必须包含这一步

## 3.非功能性要求

17. 所有的程序必须考虑容灾

18. 类命名不得与已有的开源类重名，比如自己写的类叫KafkaProducer

19. 所有组件的安全管理通过ldap进行

20. 开发必须就自己的程序完成一轮性能测试，查询接口要求每秒不少于1000次，调度型接口必须有限流功能

21. 后台程序测试必须支持一次性处理10亿级别的数据

22. 测试具备自动化测试

## 4.gitflow规范

详见 https://www.cnblogs.com/jeffery-zou/p/10280167.html

## 5. 数据库设计规范

 详见 https://developer.aliyun.com/article/709387

## 6.上线规范

上线评审过配置文件的修改，从git上对比上次上线到目前需要上线的时间的各种变化



# 61.DataX改造

1.查看了资料，DataX关于单表的性能感觉足够了

2.分布式





# 62.部署canal admin



## 1.下载软件

https://github.com/alibaba/canal/releases/download/canal-1.1.5-alpha-2/canal.adapter-1.1.5-SNAPSHOT.tar.gz



https://github.com/alibaba/canal/releases/download/canal-1.1.5-alpha-2/canal.admin-1.1.5-SNAPSHOT.tar.gz



https://github.com/alibaba/canal/releases/download/canal-1.1.5-alpha-2/canal.deployer-1.1.5-SNAPSHOT.tar.gz



https://github.com/alibaba/canal/releases/download/canal-1.1.5-alpha-2/canal.example-1.1.5-SNAPSHOT.tar.gz



## 2.安装CanalAdmin

mkdir -p /data1/zhangwusheng/canal/canal.admin

tar zxvf  canal.admin-1.1.5-SNAPSHOT.tar.gz -C  /data1/zhangwusheng/canal/canal.admin





# 63.Kafka常用命令

## 生产

```bash
/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list ctl-nm-hhht-yxxya6-ceph-007.ctyuncdn.net:6667  --topic zwstestnew2 --security-protocol=SASL_PLAINTEXT --producer-property sasl.mechanism=PLAIN

#删除消费者组

/usr/hdp/current/kafka-broker/bin/kafka-consumer-groups.sh --bootstrap-server edge-sh-pudongxin6-kafka-02.in.ctcdn.cn:5044 --describe --group console-consumer-13415 --state 

/usr/hdp/current/kafka-broker/bin/kafka-consumer-groups.sh --bootstrap-server edge-sh-pudongxin6-kafka-02.in.ctcdn.cn:12181 --delete --group console-consumer-13415
```





## 开发





# 64.rpm相关命令

查看 属于哪个包

rpm -qf /bin/iostat

查看某个包有哪些文件

rpm -ql



 yumdownloader --resolve clickhouse



# 65.负载过高

https://blog.csdn.net/u011183653/article/details/19489603?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-1.channel_param&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-1.channel_param

- yum -y install sysstat

查看磁盘情况

iostat -x 1 30
iostat -x -d -k 1 100

查看cpu情况

- vmstat



procs
 r 列表示运行和等待cpu时间片的进程数，如果长期大于1，说明cpu不足，需要增加cpu。
 b 列表示在等待资源的进程数，比如正在等待I/O、或者内存交换等。



 cpu 表示cpu的使用状态
 us 列显示了用户方式下所花费 CPU 时间的百分比。us的值比较高时，说明用户进程消耗的cpu时间多，但是如果长期大于50%，需要考虑优化用户的程序。
 sy 列显示了内核进程所花费的cpu时间的百分比。这里us + sy的参考值为80%，如果us+sy 大于 80%说明可能存在CPU不足。
 wa 列显示了IO等待所占用的CPU时间的百分比。这里wa的参考值为30%，如果wa超过30%，说明IO等待严重，这可能是磁盘大量随机访问造成的，也可能磁盘或者磁盘访问控制器的带宽瓶颈造成的(主要是块操作)。
 id 列显示了cpu处在空闲状态的时间百分比

- iostat

如果 %util 接近 100%，说明产生的I/O请求太多，I/O系统已经满负荷，该磁盘
 可能存在瓶颈。
 idle小于70% IO压力就较大了,一般读取速度有较多的wait.



- free -ml
- ps -ajxf



Kafka检查：

grep 'Scheduling' server.log|grep 'for deletion'|awk '{print $1"-" $2}'|awk -F',' '{print $1;}'|sort -u
[2020-11-02-10:22:01

首先查出删除日志的时间点
[2020-11-02-12:02:01
[2020-11-02-12:02:02
[2020-11-02-12:12:01
[2020-11-02-12:22:01
[2020-11-02-12:22:02
[2020-11-02-12:32:01
[2020-11-02-12:32:02
[2020-11-02-12:42:01
[2020-11-02-12:42:02
[2020-11-02-12:52:01

然后检查监控系统，12:22附近比较高，所以检查12:22时间左右的具体日志：


/opt/MegaRAID/MegaCli/MegaCli64 -PDList -aALL |grep "Slot Number\|Error Count\|Predictive Failure Count\|Firmware state"

Firmware state，首先可以看磁盘是否在线：若为Failed或Unconfigured(bad)则说明磁盘出现问题。若Firmware state为Online，则看磁盘是否有损坏，
Media Error Count不为0则代表扇区有问题，存在坏道等，其值越大危险系数越高。
Other Error Count不为0则表示磁盘可以没插紧，需要重新插入。查看问题磁盘的槽位号(注：告警描述中的硬盘槽位号（a-l）与Slot Number的（0-11）一一对应。例如，f号槽位的硬盘，其Slot Number为5)，找到相应磁盘。
Degraded：硬盘被拔出
Critical Disks：一颗 HDD 亮黄灯，可看到 VD 状态还是 Optimal (因为这个 HDD 还没死，目前是要死不死当中）
Predictive Failure Count  

/opt/MegaRAID/MegaCli/MegaCli64 -AdpBbuCmd -GetBbuStatus -aAll

3512  2021-07-10 17:50:28 ansible -i inventory/hosts toinstall -m shell -a '/opt/MegaRAID/storcli/storcli64 /c0 show patrolread' -b
 3513  2021-07-10 17:50:56 ansible -i inventory/hosts toinstall -m shell -a '/opt/MegaRAID/storcli/storcli64 /c0 set patrolread=on mode=manual' -b
 3514  2021-07-10 17:51:10 ansible -i inventory/hosts toinstall -m shell -a '/opt/MegaRAID/storcli/storcli64 /c0 stop patrolread' -b
 3515  2021-07-10 17:51:52 ansible -i inventory/hosts toinstall -m shell -a '/opt/MegaRAID/storcli/storcli64 /c0 set patrolread=off' -b
 3516  2021-07-10 17:52:01 ansible -i inventory/hosts toinstall -m shell -a '/opt/MegaRAID/storcli/storcli64 /c0 show patrolread' -b

# 66.spark优化经验

- 写kafka基本只需要调整batch.size即可（bug死循环，导致网卡跑满，kafka写入很猛）
- spark的json效率确实不太高，自己用stringbuilder效率最好
- 所有的逻辑在mapPartition里面，减少RDD的次数，确实能提高很多
- 如果能把write的action在mapPartition里面完成，可以减少job数，从而减少计算次数
- 45s的一分钟优化到8s，五分钟的效果有待验证（尚未完成开发）
- 数据旁路貌似可以在mapPartition里面去实现了
- 尽量不要cache，如果出现cache，应该整合rdd的计算逻辑
- MR的不要使用hadoop自带的groupwrite和groupread，使用spark的readsupport
- parquet使用自带的过滤





# 67.fsck



| **选项**          | **含义**                                                   |
| ----------------- | ---------------------------------------------------------- |
| -a                | 自动修复文件系统，不询问任何问题                           |
| -A                | 按照/etc/fstab配置文件的内容，检查文件内所列的全部文件系统 |
| -N                | 不执行命令，仅列出实际执行会进行的动作                     |
| -P                | 当搭配-A选项使用时，则会同时检查/目录的文件系统            |
| -r                | 采用交互模式，在执行修复时询问，让用户确认并决定处理方式   |
| -R                | 当使用-A选项检查所有文件系统的时候，跳过/目录的文件系统    |
| -t <文件系统类型> | 指定要检查的文件系统类型                                   |
| -C                | 显示完整的检查进度                                         |
| -y                | 关闭互动模式                                               |
| -c                | 检查坏块，并将它们添加到坏块列表                           |
| -p                | 自动修复文件系统错误                                       |
| -f                | 强制检查，即使文件系统被标记干净                           |

----------------------------------------------------

# 68.ClickHouse

```
sudo yum install yum-utils
sudo rpm --import https://repo.clickhouse.tech/CLICKHOUSE-KEY.GPG
sudo yum-config-manager --add-repo https://repo.clickhouse.tech/rpm/clickhouse.repo
sudo yum install clickhouse-server clickhouse-client

sudo yum install  --downloadonly --downloaddir=/root clickhouse-server clickhouse-client


ansible -i /etc/ansible/cdnlog_guiyang_hosts cdnlog -m  copy  -b -a "src=/home/zhangwusheng/clickhouse.tar.gz   dest=/home/zhangwusheng/soft  owner=zhangwusheng group=zhangwusheng"





```



```bahs
spark-shell --conf spark.executor.memoryOverhead=4G --conf spark.executor.instances=4 --conf spark.executor.memory=8G --conf spark.driver.memory=3G --conf spark.yarn.queue=kylin --conf spark.executor.cores=4 --jars /home/zhangwusheng/clickhouse-native-jdbc-2.3-stable.jar

spark-shell  --jars /home/zhangwusheng/clickhouse-native-jdbc-2.4.1.jar

import org.apache.spark.sql.RuntimeConfig
import org.apache.spark.sql._

val sqlContext = new org.apache.spark.sql.SQLContext(sc)

import sqlContext.implicits._
import java.lang.Double
import java.util.Date
import java.text.SimpleDateFormat
import org.apache.spark.Partitioner
import org.apache.spark.api.java.function.PairFlatMapFunction
import java.util.ArrayList
import org.apache.spark.api.java.JavaPairRDD




val schemaStr="serverIp string,timestamp string,respondTime long,httpCode integer,eventTime string,clientIp string,clientPort integer,method string,protocol string,channel string,url string,httpVersion string,bodyBytes long,destIp string,destPort integer,status string,full_status string,referer string,Ua string,fileType string,host_name string,source_ip string,source_id string,source_old string,type string,range string,vendorCode byte,genericsChannel string,clientId integer,keyFlag byte,productType byte,hostingType byte,uri string,url_param string,requestBytes long,body_sent long,proxyIp string,via string,sent_http_content_length long,http_range string,sent_http_content_range string,http_tt_request_traceid string,liveProtocol string,currentTime string,requestTime string,command string,connTag string,appName string,stream string,sendBytes string,recvBytes  string"

val parquetFile = sqlContext.read.schema(schemaStr).parquet("/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-00","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-05","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-10","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-15","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-20","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-25","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-30","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-35"),"/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-40","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-45","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-50","/apps/cdn/log/2020-10-08/2020-10-08-21/minute=2020-10-08-21-55")

val parquetFile = sqlContext.read.schema(schemaStr).parquet("/apps/cdn/log/2021-02-28/2021-02-28-23/minute=2021-02-28-23-00/task-80.parquet")


val parquetFile = sqlContext.read.schema(schemaStr).parquet("/apps/cdn/log/2021-02-28/2021-02-28-23/minute=2021-02-28-23-00/task-80.parquet")


parquetFile.rdd.mapPartitionsWithIndex{(index, iterator)=>{
var result = List[String]()
result.iterator
} }

parquetFile.printSchema

parquetFile.registerTempTable("logs")

val aa=spark.sql("select serverIp,timestamp,respondTime,httpCode,eventTime,clientIp,clientPort,method,protocol,channel,url,httpVersion,bodyBytes,destIp,destPort,status,full_status,referer,Ua,fileType,host_name,source_ip,source_id,source_old,type,range,vendorCode,genericsChannel,clientId,keyFlag,productType,hostingType,uri,url_param,requestBytes,body_sent,proxyIp,via,sent_http_content_length,http_range,sent_http_content_range,http_tt_request_traceid,liveProtocol,currentTime,requestTime,command,connTag,appName,stream,sendBytes,recvBytes from logs ")


aa.write.mode("append").format("jdbc").option("driver","com.github.housepower.jdbc.ClickHouseDriver").option("url", "jdbc:clickhouse://192.168.2.40:18000").option("user", "default").option("password", "").option("dbtable", "default.t_cdnlog_analysis_j").option("batchsize", 1000).option("isolationLevel", "NONE").save


parquetFile.write.mode("append").format("jdbc").option("driver","com.github.housepower.jdbc.ClickHouseDriver").option("url", "jdbc:clickhouse://192.168.2.40:18000").option("user", "default").option("password", "").option("dbtable", "default.t_cdnlog_analysis_j").option("batchsize", 10000).option("isolationLevel", "NONE").save

CLickHouse建表：

create table t_cdnlog_analysis_j( serverIp Nullable(String),timestamp String,respondTime Nullable(UInt32),httpCode Nullable(UInt32),eventTime Nullable(String),clientIp Nullable(String),clientPort Nullable(UInt32),method Nullable(String),protocol Nullable(String),channel Nullable(String),url Nullable(String),httpVersion Nullable(String),bodyBytes Nullable(UInt32),destIp Nullable(String),destPort Nullable(UInt32),status Nullable(String),full_status Nullable(String),referer Nullable(String),Ua Nullable(String),fileType Nullable(String),host_name Nullable(String),source_ip Nullable(String),source_id Nullable(String),source_old Nullable(String),type Nullable(String),range Nullable(String),vendorCode Nullable(UInt8),genericsChannel Nullable(String),clientId Nullable(UInt32),keyFlag Nullable(UInt8),productType Nullable(UInt8),hostingType Nullable(UInt8),uri Nullable(String),url_param Nullable(String),requestBytes Nullable(UInt32),body_sent Nullable(UInt32),proxyIp Nullable(String),via Nullable(String),sent_http_content_length Nullable(UInt32),http_range Nullable(String),sent_http_content_range Nullable(String),http_tt_request_traceid Nullable(String),liveProtocol Nullable(String),currentTime Nullable(String),requestTime Nullable(String),command Nullable(String),connTag Nullable(String),appName Nullable(String),stream Nullable(String),sendBytes Nullable(String),recvBytes  Nullable(String)) engine=MergeTree()  PARTITION BY(fromUnixTimestamp(toInt32( subString(timestamp,1,10)))) order by timestamp  settings storage_policy='all_sata';


create table t_cdnlog_analysis_d(  serverIp String ,  timestamp String ,  respondTime UInt32 ) engine=MergeTree()  PARTITION BY(fromUnixTimestamp(toInt32( subString(timestamp,1,10)))) order by timestamp  settings storage_policy='all_sata';

create table t_cdnlog_analysis_e(  serverIp Nullable(String) ,  timestamp String ,  respondTime Nullable( UInt32) ) engine=MergeTree()  PARTITION BY(fromUnixTimestamp(toInt32( subString(timestamp,1,10)))) order by timestamp  settings storage_policy='all_sata';


```

```bash
clickhouse-client  --port 18000 -h 192.168.2.40

spark shell:
```



# 69.SuperSet



```bash
https://aichamp.wordpress.com/2019/11/20/installing-apache-superset-into-centos-7-with-python-3-7/
https://www.jianshu.com/p/b02fcea7eb5b
  https://zhuanlan.zhihu.com/p/111295100

yum -y install conda.noarch
conda info -e
conda init bash

##新建环境
conda create -n superset python=3.6


##删除环境
conda deactivate
conda remove -n superset --all
#重命名环境
conda create -n superset2 --clone superset
conda remove -n superset --all

#进入环境
conda activate superset

#查看已有环境
conda info -e


vi /root/.conda/envs/superset/lib/python3.7/site-packages/Geohash
 from .geohash import decode_exactly, decode, encode


pip install superset
pip install flask
pip install wtforms_json
pip install flask_appbuilder
pip install flask_compress
pip install celery
pip install flask_migrate
pip install flask_talisman
pip install flask_caching
pip install sqlparse
pip install bleach
pip install markdown
pip install numpy
pip install markdown
pip install pandas
pip install parsedatetime
pip install pathlib2
pip install simplejson
pip install humanize
pip install geohash
pip install polyline
pip install geopy
pip install geopy
pip install cryptography
pip install sqlalchemy
pip install backoff
pip install polyline
pip install geopy
pip list|grep sqlalch
pip install sqlalchemy
pip install cryptography
pip install backoff
pip install msgpack
pip install pyarrow
pip install contextlib2
pip install croniter
pip install retry
pip install selenium
pip install isodate



cd ./.conda/envs/superset/lib/python3.6/site-packages
mv Geohash geohash
vi __init__.py
from .geohash import decode_exactly, decode, encode



superset db upgrade

superset init

export FLASK_APP=superset

flask fab create-admin
   admin
  jDJBr0equnP98377

superset load-examples

superset run --host 0.0.0.0 --port 28380 --reload --debugger --with-threads


pip install pydruid
pip install kylinpy


druid://<User>:<password>@<Host>:<Port-default-9088>/druid/v2/sql


kylin://CDNADMIN:KYLIN\@123!@192.168.254.41:7070/kylin/api?project=cdn_log_v02

kylin://CDNADMIN:XXXXXXXXXX@192.168.254.41:7070/kylin/api/query?project=cdn_log_v02

kylin://CDNADMIN:KYLIN\@123!@192.168.254.41:7070/kylin/cdn_log_v02?version=v1


http://kylin.apache.org/blog/2018/01/01/kylin-and-superset/
https://superset.apache.org/docs/databases/druid



druid://192.168.254.2:18888/druid/v2/sql

```

# 70.jmxterm

```bash

ANSIBLE_FILE=/home/zhangwusheng/etc/ansible/shanghai.hosts

ansible -i /home/zhangwusheng/etc/ansible/shanghai.hosts  kafka -m shell   -a "mkdir -p /home/zhangwusheng/var/lib"
ansible -i /home/zhangwusheng/etc/ansible/shanghai.hosts  kafka -m shell   -a "mkdir -p /home/zhangwusheng/usr/bin/"
ansible -i /home/zhangwusheng/etc/ansible/shanghai.hosts  kafka -m copy -b -a "src=/home/zhangwusheng/var/lib/jmxterm-1.1.0-SNAPSHOT-uber.jar dest=/home/zhangwusheng/var/lib backup=no"
ansible -i /home/zhangwusheng/etc/ansible/shanghai.hosts  kafka -m copy  -a "src=/home/zhangwusheng/usr/bin/jmxterm.sh  dest=/home/zhangwusheng/usr/bin/ backup=no"
ansible -i /home/zhangwusheng/etc/ansible/shanghai.hosts  kafka -m shell   -a "chmod +x /home/zhangwusheng/usr/bin/jmxterm.sh"
ansible -i /home/zhangwusheng/etc/ansible/shanghai.hosts  kafka -m shell -b  -a "chown zhangwusheng:zhangwusheng /home/zhangwusheng/usr/bin/jmxterm.sh"


java -jar /home/zhangwusheng/var/lib/jmxterm-1.1.0-SNAPSHOT-uber.jar

open pid
domains

domain kafka.server

beans
bean
info
get
```

# 71.贵州Kafka Mirror



```bash

ansible -i /home/zhangwusheng/cdnlog.guiyang.hosts mirror -m copy -b -a "src=/home/zhangwusheng/kafka-mirror-maker.sh dest=/usr/hdp/current/kafka-broker/bin backup=yes"

ansible -i /home/zhangwusheng/cdnlog.guiyang.hosts mirror -m copy -b -a "src=/home/zhangwusheng/mirror-producer.properties dest=/usr/hdp/current/kafka-broker/conf backup=yes"

ansible -i /home/zhangwusheng/cdnlog.guiyang.hosts kafka -m copy -b -a "src=/home/zhangwusheng/mirror-consumer.properties dest=/usr/hdp/current/kafka-broker/conf backup=yes"

ansible -i /home/zhangwusheng/cdnlog.guiyang.hosts kafka -m copy -b -a "src=/home/zhangwusheng/tools-log4j.properties dest=/usr/hdp/current/kafka-broker/conf backup=yes"

/usr/hdp/current/kafka-broker/bin/kafka-mirror-maker.sh --whitelist cdn-log-analysis-realtime  --consumer.config /usr/hdp/current/kafka-broker/conf/mirror-consumer.properties --producer.config /usr/hdp/current/kafka-broker/conf/mirror-producer.properties --offset.commit.interval.ms 2000 --num.streams 10 >> ./kafka-mirror-maker-2.log 2>&1 &

ps -ef|grep Mirror|grep -v 'grep'|awk '{print "kill "$2;}'

ps -ef|grep Mirror|grep cdn-log-analysis-realtime|grep -v 'grep'|awk '{print "kill "$2;}'|xargs kill

cd /ssd1/kafka;nohup /usr/hdp/current/kafka-broker/bin/kafka-mirror-maker.sh --whitelist cdn-log-analysis-realtime  --consumer.config /usr/hdp/current/kafka-broker/conf/mirror-consumer.properties --producer.config /usr/hdp/current/kafka-broker/conf/mirror-producer.properties --offset.commit.interval.ms 10000 --num.streams 4 > /ssd1/kafka/kafka-mirror-maker-test2.log 2>&1 &

ansible -i /home/zhangwusheng/cdnlog.guiyang.hosts kafka -m copy -b -a "src=/home/zhangwusheng/kafka_2.12-2.5.0.tgz dest=/home/zhangwusheng backup=yes"





/ssd1/kafka-2.5.0/kafka_2.12-2.5.0/bin/kafka-mirror-maker.sh --whitelist cdn-log-analysis-realtime  --consumer.config /ssd1/kafka-2.5.0/kafka_2.12-2.5.0/config/mirror-consumer.properties --producer.config /ssd1/kafka-2.5.0/kafka_2.12-2.5.0/config/mirror-producer.properties --offset.commit.interval.ms 2000 --num.streams 1 >> ./kafka-mirror-maker-2.log 2>&1 &

#经验1：调整参数
bootstrap.servers=cdnlog013.ctyun.net:5044,cdnlog014.ctyun.net:5044


#如果使用旧版Consumer，则使用zookeeper.connect
#zookeeper.connect=
#这个没变
request.timeout.ms=900000

#这个调整小一点，防止rebalance
heartbeat.interval.ms=2000

#这个设置大一点
session.timeout.ms=300000
#consumer group id
group.id=cdn_mirror_nm2gy_realtime-test1
partition.assignment.strategy=org.apache.kafka.clients.consumer.RoundRobinAssignor
#这个不能太大，1000应该足够了
max.poll.records=1000
#这个不能太小
max.poll.interval.ms=10000
#set receive buffer from default 64kB to 512kb
receive.buffer.bytes=4221440

#set max amount of data per partition to override default 1048576
max.partition.fetch.bytes=5248576

key.deserializer=org.apache.kafka.common.serialization.ByteArrayDeserializer
value.deserializer=org.apache.kafka.common.serialization.ByteArrayDeserializer

sasl.mechanism=PLAIN
security.protocol=SASL_PLAINTEXT
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="admin" password="CtYiofnwk@269Mn";



#######################################

#prod
bootstrap.servers=sct-gz-guiyang1-loganalysis-10.in.ctcdn.cn:5044,sct-gz-guiyang1-loganalysis-11.in.ctcdn.cn:5044

# name of the partitioner class for partitioning events; default partition spreads data randomly
#partitioner.class=

# 必须是异步
producer.type=async

# specify the compression codec for all data generated: none, gzip, snappy, lz4.
# the old config values work as well: 0, 1, 2, 3 for none, gzip, snappy, lz4, respectively
compression.type=lz4
# message encoder
#serializer.class=kafka.serializer.DefaultEncoder

#batch.size=16384
#key.serializer=org.apache.kafka.common.serialization.StringSerializer
key.serializer=org.apache.kafka.common.serialization.ByteArraySerializer
#value.serializer=org.apache.kafka.common.serialization.StringSerializer
value.serializer=org.apache.kafka.common.serialization.ByteArraySerializer
#retries=3
#linger.ms=100
#buffer.memory=33554432

#enable.idempotence=true

sasl.mechanism=PLAIN
security.protocol=SASL_PLAINTEXT
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="admin" password="CtYiofnwk@269Mn";

#max.in.flight.requests.per.connection=50
acks=1
#这个不能太大
batch.size=163840
send.buffer.bytes=4221440
receive.buffer.bytes=4221440
#####################################

##注意consumer和producer的数据量要匹配起来
#内蒙到贵阳，一个consumer一秒10万，一个producer一秒接近100W
/usr/hdp/current/kafka-broker/bin/kafka-mirror-maker.sh --whitelist cdn-log-analysis-realtime  --consumer.config /usr/hdp/current/kafka-broker/conf/mirror-consumer.properties --producer.config /usr/hdp/current/kafka-broker/conf/mirror-producer.properties --offset.commit.interval.ms 2000 --num.streams 3 > ./kafka-mirror-maker-debug.log 2>&1 &
```

# 72. g++多版本冲突

```bash
删掉有冲突的版本

i686的版本删除掉
yum remove glibc-2.17-322.el7_9.i686
```



# 73. rsyslog

```bash

yum -y install libuuid-devel
yum install -y libgcrypt-devel
yum search libcurl
yum install -y libcurl-devel.x86_64
yum install -y libcurl-devel.x86_64
yum search rdkafka
yum -y install librdkafka-devel.x86_64
yum -y install g++
yum -y install gcc-c++
yum update -y libstdc++.x86_64
yum install libstdc++.i686
yum -y install gcc-c++
yum -y install libstdc++-4.8.5-39.el7.i686
yum -y install gcc-c++
yum -y install libstdc++-4.8.5-44.el7.x86_64
yum remove -y libstdc++-4.8.5-39.el7.i686
yum -y install gcc-c++
yum -y install libsasl2
yum -y install yacc
yum search yacc
yum -y install byacc
yum -y install flex

#grok的安装，不同机器不同
centos
libgrok-dev libgrok1 libtokyocabinet-dev
yum -y install tokyocabinet-devel.x86_64


git clone https://github.com/civetweb/civetweb

https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/semicomplete/grok-1.20110708.1.tar.gz
https://github.com/jordansissel/grok.git
https://github.com/maiha/tokyocabinet.git
https://github.com/thkukuk/rpcsvc-proto.git

autoreconf --install

安装liblognorm-2.0.6

LIBFASTJSON_CFLAGS="-I/usr/include/libfastjson"  LIBFASTJSON_LIBS="-L/usr/lib -lfastjson" LIBRDKAFKA_CFLAGS="-I/usr/local/include" LIBRDKAFKA_LIBS="-L/usr/local/lib -lrdkafka" LIBLOGNORM_CFLAGS="-I/usr/local/include/" LIBLOGNORM_LIBS="-L/usr/local/lib -llognorm" ./configure  --prefix=/home/zhangwusheng/usr/local/  --enable-omkafka --enable-imkafka  --enable-regexp --enable-gssapi-krb5 --enable-uuid --enable-openssl --enable-mmnormalize  --enable-mmjsonparse --enable-mmgrok --enable-mmaudit --enable-mmcount --enable-mmsequence --enable-mmfields  --enable-imfile  --enable-pmnormalize  --enable-omruleset
#--enable-imjournal --enable-omjournal

#压测kafka幂等的信息 22秒257W
[root@sct-gz-guiyang1-loganalysis-01 librdkafka-1.5.3]# date;./examples/idempotent_producer sct-gz-guiyang1-loganalysis-10.in.ctcdn.cn:5044  cdn-live-test;date
Wed Jan 27 12:58:04 CST 2021
% Running producer loop. Press Ctrl-C to exit
% Failed to produce to topic cdn-live-test: Local: Queue full
% Failed to produce to topic cdn-live-test: Local: Queue full
1611723485:662687  100000
1611723486:239844  200000
1611723487:157673  300000
1611723488:57540  400000
1611723488:869915  500000
1611723489:699757  600000
1611723490:514558  700000
1611723491:395811  800000
1611723492:195446  900000
1611723493:24598  1000000
1611723493:846798  1100000
1611723494:675041  1200000
1611723495:502797  1300000
1611723496:320813  1400000
1611723497:159584  1500000
1611723497:980876  1600000
1611723498:803654  1700000
1611723499:634289  1800000
1611723500:470975  1900000
1611723501:298566  2000000
1611723502:121867  2100000
1611723502:937373  2200000
1611723503:751043  2300000
1611723504:573546  2400000
1611723505:390845  2500000
^C% Flushing outstanding messages..
% 2578850 message(s) produced, 2578850 delivered, 0 failed
Wed Jan 27 12:58:26 CST 2021


#调试rsyslogd
export RSYSLOG_DEBUG="DebugOnDemand NoStdOut"
export RSYSLOG_DEBUGLOG=/home/zhangwusheng/var/log/rsyslogd-debug.log
/home/zhangwusheng/usr/local/sbin/rsyslogd -n -f /home/zhangwusheng/etc/rsyslog.conf -i /home/zhangwusheng/var/run/rsyslog.pid

kill -USR1 `cat /home/zhangwusheng/var/run/rsyslog.pid`
kill  `cat /home/zhangwusheng/var/run/rsyslog.pid`

logger -n 192.168.189.24 -P 58085 -p local7.info "a&b&c"

ps -ef|grep rsyslog|grep zhangwusheng|awk '{print $2;}'|xargs kill

curl 'http://192.168.189.24:58080/?a&b&c'
ab -n 10000 -c 30 'http://192.168.189.24:58080/qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq'

https://my.oschina.net/MrYx3en/blog/525803

https://www.liblognorm.com/files/manual/index.html


rule=A: %date:char-to:\x20% %time:time-24hr% [%level:char-to:\x5D%] %f1:char-to::%: %f2:char-to:\x20% %errmsg:char-to:,%, client: %client:ipv4%, server: %server:rest%"

#B和C不能同时存在一个rulebase文件中，否则会导致误解析。
rule=B: %date:char-to:\x20% %time:time-24hr% [%level:char-to:\x5D%] %f1:char-to::%: %f2:char-to:\x20% %errmsg:char-to:,%, client: %client:ipv4%, server: %server:char-to:,%, request: "%verb:word% %urlpath:char-to:\x3F%?%urlparam:char-to:\x20% HTTP/%httpversion:char-to:\x22%", upstream: %upstream:char-to:,%, host: %host:rest%

rule=C: %date:char-to:\x20% %time:time-24hr% [%level:char-to:\x5D%] %f1:char-to::%: %f2:char-to:\x20% %errmsg:char-to:,%, client: %client:ipv4%, server: %server:char-to:,%, request: "%verb:word% %urlpath:char-to:\x20% HTTP/%httpversion:char-to:\x22%", upstream: %upstream:char-to:\x2C%, host: %host:rest%

rule=D: %date:char-to:\x20% %time:time-24hr% [%level:char-to:\x5D%] %f1:char-to::%: %f2:char-to:\x20% %errmsg:char-to:,%, client: %client:ipv4%, server: %server:char-to:,%, request: "%verb:word% %urlpath:char-to:\x3F%?%urlparam:char-to:\x20% HTTP/%httpversion:char-to:\x22%", host: %host:rest%

rule=F: %errmsg:rest%

cat ra.rb
rule=ra:%AA:char-to:&%&%BB:char-to:&%&%c:rest%
lognormalizer -r ra.rb   < a.txt > a.json
lognormalizer -r nginxerr.rulebase -e json -T < test0.log > normalized.log


the first thing to do is to test your ruleset

create a template:
$template raw,"%rawmsg%\n"

/var/log/testing;raw

then you can do
head -1 raw |/usr/lib/lognorm/lognormalizer -r /etc/rsyslog.rb -v -e json -T

and look at the output that you receive.

one obvious problem that I see is that the rawmsg is going to contain the
priority info (facility/severity), so before the timestamp there is going to be
<number> so your rules aren't going to match

but by logging the rawmsg to a file, you will see exactly what is being passed
to the parser, and can test the parser from the command line.





/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server  sct-gz-guiyang1-loganalysis-10.in.ctcdn.cn:5044    --topic cdn-log-analysis-batch-perf-test --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --offset latest --partition 0 --group grp-rsyslog-test


/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server edge-sh-pudongxin6-kafka-05.in.ctcdn.cn:5044 --topic ctYun_agg_shanghai --consumer-property security.protocol=SASL_PLAINTEXT  --consumer-property  sasl.mechanism=PLAIN  --offset latest --partition 46 --group grp-rsyslog-test


/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server        edge-js-yangzhou3-loganalysis-01.in.ctcdn.cn:5044 --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --offset latest --partition 0 --topic rsyslog-lizw --group grp-rsyslog-test


/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server        edge-js-yangzhou3-loganalysis-01.in.ctcdn.cn:5044 --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --topic rsyslog-lizw --group grp-rsyslog-test



堆栈：
  32   Thread 0x7f24735bf700 (LWP 10) "rdk:broker-1" 0x00007f2478830c3d in poll
    () from /lib64/libc.so.6
  31   Thread 0x7f2472dbe700 (LWP 11) "rdk:main" 0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
  30   Thread 0x7f24725bd700 (LWP 12) "rdk:broker-1" 0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
  29   Thread 0x7f2471dbc700 (LWP 13) "rdk:broker1006" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  28   Thread 0x7f24715bb700 (LWP 14) "rdk:broker1005" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  27   Thread 0x7f2470dba700 (LWP 15) "rdk:broker1012" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  26   Thread 0x7f245bfff700 (LWP 16) "rdk:broker1009" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  25   Thread 0x7f245b7fe700 (LWP 17) "rdk:broker1007" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  24   Thread 0x7f245affd700 (LWP 18) "rdk:broker1008" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  23   Thread 0x7f245a7fc700 (LWP 19) "rdk:broker1011" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  22   Thread 0x7f2459ffb700 (LWP 20) "rdk:broker1004" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
---Type <return> to continue, or q <return> to quit---
  21   Thread 0x7f24597fa700 (LWP 21) "rdk:broker1010" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  20   Thread 0x7f2458ff9700 (LWP 22) "rdk:broker1003" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  19   Thread 0x7f24705b9700 (LWP 23) "in:impstats" 0x00007f24788329a3 in select () from /lib64/libc.so.6
  18   Thread 0x7f24587f8700 (LWP 24) "in:imkafka" 0x00007f24788329a3 in select
    () from /lib64/libc.so.6
  17   Thread 0x7f242ffff700 (LWP 25) "in:imkafka" 0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
  16   Thread 0x7f241e5d1700 (LWP 26) "rs:main Q:Reg" 0x00007f247976a54d in __lll_lock_wait () from /lib64/libpthread.so.0
  15   Thread 0x7f241ddd0700 (LWP 27) "rs:action-1-omk" 0x000000000045858b in qDeqLinkedList (pThis=0x1c87950, ppMsg=0x7f241ddcfab8) at queue.c:744
  14   Thread 0x7f241d5cf700 (LWP 28) "rdk:main" 0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
  13   Thread 0x7f241cdce700 (LWP 29) "rdk:broker-1" 0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
  12   Thread 0x7f2417fff700 (LWP 30) "rdk:broker1006" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  11   Thread 0x7f24177fe700 (LWP 31) "rdk:broker1005" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  10   Thread 0x7f2416ffd700 (LWP 32) "rdk:broker1012" 0x00007f2478830c3d in pol---Type <return> to continue, or q <return> to quit---
l () from /lib64/libc.so.6
  9    Thread 0x7f24167fc700 (LWP 33) "rdk:broker1009" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  8    Thread 0x7f24149ca700 (LWP 34) "rdk:broker1007" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  7    Thread 0x7f23f7fff700 (LWP 35) "rdk:broker1008" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  6    Thread 0x7f23f77fe700 (LWP 36) "rdk:broker1011" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  5    Thread 0x7f23f6ffd700 (LWP 37) "rdk:broker1004" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  4    Thread 0x7f23f67fc700 (LWP 38) "rdk:broker1010" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  3    Thread 0x7f23f5ffb700 (LWP 39) "rdk:broker1003" 0x00007f2478830c3d in poll () from /lib64/libc.so.6
  2    Thread 0x7f242fbfe700 (LWP 232) "rs:main Q:Reg" 0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
* 1    Thread 0x7f2479d9a8c0 (LWP 1) "rsyslogd" 0x00007f2478832a79 in pselect


thread 1

#0  0x00007f2478832a79 in pselect () from /lib64/libc.so.6
#1  0x0000000000410fad in wait_timeout (sigmask=0x7ffe8f628dd0)
    at rsyslogd.c:1924
#2  mainloop () at rsyslogd.c:1977
#3  0x000000000040e4bb in main (argc=4, argv=0x7ffe8f6292d8) at rsyslogd.c:2174

(gdb) thread 2
[Switching to thread 2 (Thread 0x7f242fbfe700 (LWP 232))]
#0  0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 ()
   from /lib64/libpthread.so.0
(gdb) bt
#0  0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 ()
   from /lib64/libpthread.so.0
#1  0x0000000000457ea7 in doIdleProcessing (
    pbInactivityTOOccured=<synthetic pointer>, pWtp=0x1dc2310, pThis=0x1dc2f80)
    at wti.c:363
#2  wtiWorker (pThis=pThis@entry=0x1dc2f80) at wti.c:438
#3  0x0000000000454f9a in wtpWorker (arg=0x1dc2f80) at wtp.c:435
#4  0x00007f2479763ea5 in start_thread () from /lib64/libpthread.so.0
#5  0x00007f247883b96d in clone () from /lib64/libc.so.6



(gdb) thread 3
[Switching to thread 3 (Thread 0x7f23f5ffb700 (LWP 39))]
#0  0x00007f2478830c3d in poll () from /lib64/libc.so.6
(gdb) bt
#0  0x00007f2478830c3d in poll () from /lib64/libc.so.6
#1  0x00007f2475aa725e in rd_kafka_transport_poll (
    rktrans=rktrans@entry=0x7f23e00043f0, tmout=tmout@entry=179)
    at rdkafka_transport.c:960
#2  0x00007f2475aa72ef in rd_kafka_transport_io_serve (rktrans=0x7f23e00043f0, 
    timeout_ms=179) at rdkafka_transport.c:792
#3  0x00007f2475a8fc5d in rd_kafka_broker_ops_io_serve (
    rkb=rkb@entry=0x7f2410010610, abs_timeout=<optimized out>)
    at rdkafka_broker.c:3380
#4  0x00007f2475a91488 in rd_kafka_broker_producer_serve (
    abs_timeout=15702691047474, rkb=0x7f2410010610) at rdkafka_broker.c:3972
#5  rd_kafka_broker_serve (rkb=rkb@entry=0x7f2410010610, 
    timeout_ms=<optimized out>, timeout_ms@entry=1000) at rdkafka_broker.c:5064
#6  0x00007f2475a91bdd in rd_kafka_broker_thread_main (
    arg=arg@entry=0x7f2410010610) at rdkafka_broker.c:5223
#7  0x00007f2475b04f77 in _thrd_wrapper_function (aArg=<optimized out>)
    at tinycthread.c:576
#8  0x00007f2479763ea5 in start_thread () from /lib64/libpthread.so.0
#9  0x00007f247883b96d in clone () from /lib64/libc.so.6

(gdb) thread 13
[Switching to thread 13 (Thread 0x7f241cdce700 (LWP 29))]
#0  0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 ()
   from /lib64/libpthread.so.0
(gdb) bt
#0  0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 ()
   from /lib64/libpthread.so.0
#1  0x00007f2475b05109 in cnd_timedwait (cond=<optimized out>, 
    mtx=<optimized out>, ts=<optimized out>) at tinycthread.c:462
#2  0x00007f2475b054bd in cnd_timedwait_abs (cnd=cnd@entry=0x7f24100072c8, 
    mtx=mtx@entry=0x7f24100072a0, tspec=tspec@entry=0x7f241cdcd800)
    at tinycthread_extra.c:103
#3  0x00007f2475aadb6b in rd_kafka_q_pop_serve (rkq=0x7f24100072a0, 
    timeout_us=<optimized out>, version=version@entry=0, 
    cb_type=cb_type@entry=RD_KAFKA_Q_CB_RETURN, callback=callback@entry=0x0, 
    opaque=opaque@entry=0x0) at rdkafka_queue.c:404
#4  0x00007f2475aadc60 in rd_kafka_q_pop (rkq=<optimized out>, 
    timeout_us=<optimized out>, version=version@entry=0) at rdkafka_queue.c:428
#5  0x00007f2475a8fb7f in rd_kafka_broker_ops_serve (
    rkb=rkb@entry=0x7f2410006660, timeout_us=<optimized out>)
    at rdkafka_broker.c:3337
#6  0x00007f2475a8fc6f in rd_kafka_broker_ops_io_serve (
    rkb=rkb@entry=0x7f2410006660, abs_timeout=<optimized out>, 
    abs_timeout@entry=15702690994101) at rdkafka_broker.c:3388
#7  0x00007f2475a916d7 in rd_kafka_broker_internal_serve (
    abs_timeout=15702690994101, rkb=0x7f2410006660) at rdkafka_broker.c:3559
#8  rd_kafka_broker_serve (rkb=rkb@entry=0x7f2410006660, 
    timeout_ms=<optimized out>, timeout_ms@entry=1000) at rdkafka_broker.c:5062
	---Type <return> to continue, or q <return> to quit---bt
#9  0x00007f2475a91cc3 in rd_kafka_broker_thread_main (
    arg=arg@entry=0x7f2410006660) at rdkafka_broker.c:5193
#10 0x00007f2475b04f77 in _thrd_wrapper_function (aArg=<optimized out>)
    at tinycthread.c:576
#11 0x00007f2479763ea5 in start_thread () from /lib64/libpthread.so.0
#12 0x00007f247883b96d in clone () from /lib64/libc.so.6


(gdb) thread 14
[Switching to thread 14 (Thread 0x7f241d5cf700 (LWP 28))]
#0  0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 ()
   from /lib64/libpthread.so.0
(gdb) bt
#0  0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 ()
   from /lib64/libpthread.so.0
#1  0x00007f2475b05109 in cnd_timedwait (cond=<optimized out>, 
    mtx=<optimized out>, ts=<optimized out>) at tinycthread.c:462
#2  0x00007f2475b054bd in cnd_timedwait_abs (cnd=cnd@entry=0x7f2410006018, 
    mtx=mtx@entry=0x7f2410005ff0, tspec=tspec@entry=0x7f241d5ceb60)
    at tinycthread_extra.c:103
#3  0x00007f2475aadf6e in rd_kafka_q_serve (rkq=0x7f2410005ff0, 
    timeout_ms=<optimized out>, max_cnt=max_cnt@entry=0, 
    cb_type=cb_type@entry=RD_KAFKA_Q_CB_CALLBACK, callback=callback@entry=0x0, 
    opaque=opaque@entry=0x0) at rdkafka_queue.c:474
#4  0x00007f2475a739ec in rd_kafka_thread_main (arg=arg@entry=0x7f2410004f80)
    at rdkafka.c:2003
#5  0x00007f2475b04f77 in _thrd_wrapper_function (aArg=<optimized out>)
    at tinycthread.c:576
#6  0x00007f2479763ea5 in start_thread () from /lib64/libpthread.so.0
#7  0x00007f247883b96d in clone () from /lib64/libc.so.6


(gdb) thread 15
[Switching to thread 15 (Thread 0x7f241ddd0700 (LWP 27))]
#0  0x000000000045858b in qDeqLinkedList (pThis=0x1c87950, 
    ppMsg=0x7f241ddcfab8) at queue.c:744
744             *ppMsg = pEntry->pMsg;
(gdb) bt
#0  0x000000000045858b in qDeqLinkedList (pThis=0x1c87950, 
    ppMsg=0x7f241ddcfab8) at queue.c:744
#1  0x000000000045b265 in qqueueDeq (ppMsg=0x7f241ddcfab8, pThis=0x1c87950)
    at queue.c:1195
#2  DequeueConsumableElements (pSkippedMsgs=0x7f241ddcfb2c, 
    piRemainingQueueSize=<synthetic pointer>, pWti=0x1cc1b50, pThis=0x1c87950)
    at queue.c:1838
#3  DequeueConsumable (pSkippedMsgs=0x7f241ddcfb2c, pWti=0x1cc1b50, 
    pThis=0x1c87950) at queue.c:1913
#4  DequeueForConsumer (pThis=pThis@entry=0x1c87950, 
    pWti=pWti@entry=0x1cc1b50, pSkippedMsgs=pSkippedMsgs@entry=0x7f241ddcfb2c)
    at queue.c:2059
#5  0x000000000045ba26 in ConsumerReg (pThis=0x1c87950, pWti=0x1cc1b50)
    at queue.c:2115
#6  0x0000000000457c01 in wtiWorker (pThis=pThis@entry=0x1cc1b50) at wti.c:428
#7  0x0000000000454f9a in wtpWorker (arg=0x1cc1b50) at wtp.c:435
#8  0x00007f2479763ea5 in start_thread () from /lib64/libpthread.so.0
#9  0x00007f247883b96d in clone () from /lib64/libc.so.6

(gdb) thread 16
[Switching to thread 16 (Thread 0x7f241e5d1700 (LWP 26))]
#0  0x00007f247976a54d in __lll_lock_wait () from /lib64/libpthread.so.0
(gdb) bt
#0  0x00007f247976a54d in __lll_lock_wait () from /lib64/libpthread.so.0
#1  0x00007f2479765e9b in _L_lock_883 () from /lib64/libpthread.so.0
#2  0x00007f2479765d68 in pthread_mutex_lock () from /lib64/libpthread.so.0
#3  0x000000000045eb43 in qqueueEnqMsg (pThis=0x1c87950, 
    flowCtlType=flowCtlType@entry=eFLOWCTL_NO_DELAY, pMsg=0x7f23c000b7d0)
    at queue.c:3196
#4  0x000000000046ab11 in doSubmitToActionQ (pAction=0x1c86bd0, 
    pWti=0x1dc24a0, pMsg=0x7f23c000b7d0) at ../action.c:1826
#5  0x0000000000462305 in execAct (stmt=0x1c854a0, pWti=0x1dc24a0, 
    pMsg=0x7f23c000b7d0) at ruleset.c:209
#6  scriptExec (root=<optimized out>, pMsg=pMsg@entry=0x7f23c000b7d0, 
    pWti=pWti@entry=0x1dc24a0) at ruleset.c:599
#7  0x000000000046235b in execPROPFILT (pWti=<optimized out>, 
    pMsg=<optimized out>, stmt=<optimized out>) at ruleset.c:546
#8  scriptExec (root=<optimized out>, pMsg=pMsg@entry=0x7f23c000b7d0, 
    pWti=pWti@entry=0x1dc24a0) at ruleset.c:623
#9  0x0000000000462ea5 in processBatch (pBatch=0x1dc24d8, pWti=0x1dc24a0)
    at ruleset.c:660
#10 0x000000000040ed2c in msgConsumer (notNeeded=<optimized out>, 
    pBatch=0x1dc24d8, pWti=0x1dc24a0) at rsyslogd.c:695
#11 0x000000000045bc3c in ConsumerReg (pThis=0x1dc1f50, pWti=0x1dc24a0)
    at queue.c:2145
#12 0x0000000000457c01 in wtiWorker (pThis=pThis@entry=0x1dc24a0) at wti.c:428
---Type <return> to continue, or q <return> to quit---
#13 0x0000000000454f9a in wtpWorker (arg=0x1dc24a0) at wtp.c:435
#14 0x00007f2479763ea5 in start_thread () from /lib64/libpthread.so.0
#15 0x00007f247883b96d in clone () from /lib64/libc.so.6

(gdb) thread 17
[Switching to thread 17 (Thread 0x7f242ffff700 (LWP 25))]
#0  0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 ()
   from /lib64/libpthread.so.0
(gdb) bt
#0  0x00007f2479767de2 in pthread_cond_timedwait@@GLIBC_2.3.2 ()
   from /lib64/libpthread.so.0
#1  0x00007f2475b05109 in cnd_timedwait (cond=<optimized out>, 
    mtx=<optimized out>, ts=<optimized out>) at tinycthread.c:462
#2  0x00007f2475b054bd in cnd_timedwait_abs (cnd=cnd@entry=0x1cb3e68, 
    mtx=mtx@entry=0x1cb3e40, tspec=tspec@entry=0x7f242fffec80)
    at tinycthread_extra.c:103
#3  0x00007f2475aadb6b in rd_kafka_q_pop_serve (rkq=rkq@entry=0x1cb3e40, 
    timeout_us=<optimized out>, version=version@entry=0, 
    cb_type=cb_type@entry=RD_KAFKA_Q_CB_RETURN, callback=callback@entry=0x0, 
    opaque=opaque@entry=0x0) at rdkafka_queue.c:404
#4  0x00007f2475aadc60 in rd_kafka_q_pop (rkq=rkq@entry=0x1cb3e40, 
    timeout_us=<optimized out>, version=version@entry=0) at rdkafka_queue.c:428
#5  0x00007f2475a75c51 in rd_kafka_consume0 (rk=0x1cac110, rkq=0x1cb3e40, 
    timeout_ms=timeout_ms@entry=1000) at rdkafka.c:3023
#6  0x00007f2475a75f37 in rd_kafka_consumer_poll (rk=<optimized out>, 
    timeout_ms=timeout_ms@entry=1000) at rdkafka.c:3132
#7  0x00007f2473d8dc21 in msgConsume (inst=<optimized out>) at imkafka.c:223
#8  imkafkawrkr (myself=0x7f24340008e0) at imkafka.c:898
#9  0x00007f2479763ea5 in start_thread () from /lib64/libpthread.so.0
#10 0x00007f247883b96d in clone () from /lib64/libc.so.6

(gdb) thread 18
[Switching to thread 18 (Thread 0x7f24587f8700 (LWP 24))]
#0  0x00007f24788329a3 in select () from /lib64/libc.so.6
(gdb) bt
#0  0x00007f24788329a3 in select () from /lib64/libc.so.6
#1  0x0000000000444433 in srSleep (iSeconds=iSeconds@entry=0, 
    iuSeconds=iuSeconds@entry=100000) at srutils.c:538
#2  0x00007f2473d8e22c in runInput (pThrd=<optimized out>) at imkafka.c:795
#3  0x000000000046c5e8 in thrdStarter (arg=0x1dc4100) at ../threads.c:243
#4  0x00007f2479763ea5 in start_thread () from /lib64/libpthread.so.0
#5  0x00007f247883b96d in clone () from /lib64/libc.so.6



(gdb) 
(gdb) thread 19
[Switching to thread 19 (Thread 0x7f24705b9700 (LWP 23))]
#0  0x00007f24788329a3 in select () from /lib64/libc.so.6
(gdb) bt
#0  0x00007f24788329a3 in select () from /lib64/libc.so.6
#1  0x0000000000444433 in srSleep (iSeconds=<optimized out>, 
    iuSeconds=iuSeconds@entry=0) at srutils.c:538
#2  0x00007f247643a53f in runInput (pThrd=<optimized out>) at impstats.c:567
#3  0x000000000046c5e8 in thrdStarter (arg=0x1dc3d80) at ../threads.c:243
#4  0x00007f2479763ea5 in start_thread () from /lib64/libpthread.so.0
#5  0x00007f247883b96d in clone () from /lib64/libc.so.6



(gdb) bt
#0  0x00007f2478830c3d in poll () from /lib64/libc.so.6
#1  0x00007f2475aa725e in rd_kafka_transport_poll (
    rktrans=rktrans@entry=0x7f243c0043f0, tmout=tmout@entry=866)
    at rdkafka_transport.c:960
#2  0x00007f2475aa72ef in rd_kafka_transport_io_serve (rktrans=0x7f243c0043f0, 
    timeout_ms=866) at rdkafka_transport.c:792
#3  0x00007f2475a8fc5d in rd_kafka_broker_ops_io_serve (
    rkb=rkb@entry=0x1cc0a70, abs_timeout=<optimized out>)
    at rdkafka_broker.c:3380
#4  0x00007f2475a900b8 in rd_kafka_broker_consumer_serve (
    rkb=rkb@entry=0x1cc0a70, abs_timeout=abs_timeout@entry=15702691643732)
    at rdkafka_broker.c:4961
#5  0x00007f2475a91641 in rd_kafka_broker_serve (rkb=rkb@entry=0x1cc0a70, 
    timeout_ms=<optimized out>, timeout_ms@entry=1000) at rdkafka_broker.c:5066
#6  0x00007f2475a91bdd in rd_kafka_broker_thread_main (arg=arg@entry=0x1cc0a70)
    at rdkafka_broker.c:5223
#7  0x00007f2475b04f77 in _thrd_wrapper_function (aArg=<optimized out>)
    at tinycthread.c:576
#8  0x00007f2479763ea5 in start_thread () from /lib64/libpthread.so.0
#9  0x00007f247883b96d in clone () from /lib64/libc.so.6



```



# 74. FIO

```bash
顺序写：
fio --name=sequence-write --ioengine=posixaio --rw=write --bs=4k --size=4g --numjobs=1 --runtime=60 --time_based --end_fsync=1 --filename=/dev/sdf --direct=1

fio --name=sequence-write --ioengine=posixaio --rw=write --bs=4k --size=4g --numjobs=1 --runtime=60 --time_based --end_fsync=1 --filename=/dev/sdc --direct=1

fio --name=sequence-write --ioengine=posixaio --rw=write --bs=4k --size=4g --numjobs=1 --runtime=60 --time_based --end_fsync=1 --filename=/data8/fio_test.dat --direct=1

fio --name=sequence-write --ioengine=posixaio --rw=write --bs=4k --size=4g --numjobs=1 --runtime=60 --time_based --end_fsync=1 --filename=/data8/fio_test.dat --direct=1


顺序读：
/usr/local/bin/fio -filename=/home/zhangwusheng/fio_test_read.dat -direct=1 -iodepth 1 -thread -rw=read -ioengine=psync -bs=16k -size=2G -numjobs=1 -runtime=60 -group_reporting -name=sequence-read

fio -filename=/data8/fio_test_read.dat -direct=1 -iodepth 1 -thread -rw=read -ioengine=psync -bs=16k -size=2G -numjobs=1 -runtime=60 -group_reporting -name=sequence-read

posixaio



echo `cat /proc/slabinfo |awk 'BEGIN{sum=0;}{sum=sum+$3*$4;}END{print sum/1024/1024}'` MB

```



# 75. iperf

iperf3 -p 50475 -B 113.125.219.24 -s
"GZ-GY-4L&401-J04&45U-DW-RG6220-03
GZ-GY-4L&401-J05&45U-DW-RG6220-04
GZ-GY-4L&401-J04&41U-JR-RGS5750-02"

iperf3 -c 113.125.219.24 -P 100 -p 50475 -B 150.223.254.2  -b 400M -R
[SUM]   0.00-10.00  sec  12.6 GBytes  10.8 Gbits/sec  16520             sender
[SUM]   0.00-10.00  sec  12.4 GBytes  10.6 Gbits/sec                  receiver

iperf3 -p 50475 -B 113.125.219.41 -s
"GZ-GY-4L&401-J06&45U-DW-RG6220-05
GZ-GY-4L&401-J07&45U-DW-RG6220-06
GZ-GY-4L&401-J04&41U-JR-RGS5750-02"

iperf3 -c 113.125.219.41 -P 100 -p 50475 -B 150.223.254.2  -b 400M -R

[SUM]   0.00-10.00  sec  17.1 GBytes  14.7 Gbits/sec  14723             sender
[SUM]   0.00-10.00  sec  16.9 GBytes  14.5 Gbits/sec                  receiver

iperf3 -c 113.125.219.41 -P 100 -p 50475 -B 150.223.254.2  -b 800M -R

[SUM]   0.00-10.00  sec  18.6 GBytes  16.0 Gbits/sec  12678             sender
[SUM]   0.00-10.00  sec  18.4 GBytes  15.8 Gbits/sec                  receiver

 iperf3 -p 50475 -B 113.125.219.56 -s
 "GZ-GY-4L&401-J06&45U-DW-RG6220-07
GZ-GY-4L&401-J07&45U-DW-RG6220-08
GZ-GY-4L&401-J08&41U-JR-RGS5750-03"

 iperf3 -c 113.125.219.56 -P 100 -p 50475 -B 150.223.254.2  -b 800M -R
 [SUM]   0.00-10.00  sec  12.6 GBytes  10.8 Gbits/sec  13760             sender
[SUM]   0.00-10.00  sec  12.3 GBytes  10.6 Gbits/sec                  receiver


 iperf3 -p 50475 -B 113.125.219.75 -s
GZ-GY-4L&401-J10&45U-DW-RG6220-09
GZ-GY-4L&401-J11&45U-DW-RG6220-10
GZ-GY-4L&401-J08&41U-JR-RGS5750-03
 iperf3 -c 113.125.219.75 -P 100 -p 50475 -B 150.223.254.2  -b 800M -R

 [SUM]   0.00-10.00  sec  13.8 GBytes  11.9 Gbits/sec  12763             sender
[SUM]   0.00-10.00  sec  13.6 GBytes  11.7 Gbits/sec                  receiver




  iperf3 -c 113.125.219.75 -P 100 -p 50475 -B 150.223.254.21  -b 800M -R
 Eth-Trunk12
 [SUM]   0.00-10.00  sec  14.8 GBytes  12.7 Gbits/sec  9110             sender
[SUM]   0.00-10.00  sec  14.5 GBytes  12.5 Gbits/sec                  receiver



   iperf3 -c 113.125.219.56 -P 100 -p 50475 -B 150.223.254.21  -b 1000M -R
[SUM]   0.00-10.00  sec  12.5 GBytes  10.7 Gbits/sec  23271             sender
[SUM]   0.00-10.00  sec  12.3 GBytes  10.5 Gbits/sec                  receiver



# 76. 扬州三线Kafka

```bash

ansible -i /home/zhangwusheng/etc/ansible/yangzhou.hosts kafka -m  file  -b -a "dest=/home/zhangwusheng/usr/bin  owner=zhangwusheng group=zhangwusheng state=directory recurse=yes"

ansible -i /home/zhangwusheng/etc/ansible/yangzhou.hosts kafka -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/fstab.sh   dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"

ansible -i /home/zhangwusheng/etc/ansible/yangzhou.hosts kafka -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/fstab.py   dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"

ansible -i /home/zhangwusheng/etc/ansible/yangzhou.hosts kafka -m shell  -b -a "bash /home/zhangwusheng/usr/bin/fstab.sh"
ansible -i /home/zhangwusheng/etc/ansible/yangzhou.hosts kafka -m shell  -b -a "cat /etc/fstab"

ansible -i /home/zhangwusheng/etc/ansible/yangzhou.hosts kafka -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/jdk-8u211-linux-x64.tar.gz dest=/home/zhangwusheng/usr/bin  owner=root group=root"
ansible -i /home/zhangwusheng/etc/ansible/yangzhou.hosts kafka -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/jce_policy-8.zip dest=/home/zhangwusheng/usr/bin  owner=zhangwusheng group=zhangwusheng"


ansible -i /home/zhangwusheng/etc/ansible/yangzhou.hosts kafka -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/java-env.sh   dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"

ansible -i /home/zhangwusheng/etc/ansible/yangzhou.hosts kafka -m shell  -b -a "bash /home/zhangwusheng/usr/bin/java-env.sh"

```

# 76. VIVO

```bash
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  file  -b -a "dest=/home/zhangwusheng/usr/bin  owner=zhangwusheng group=zhangwusheng state=directory recurse=yes"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  file  -b -a "dest=/home/zhangwusheng/etc/security  owner=zhangwusheng group=zhangwusheng state=directory recurse=yes"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/mkfs.vivo     dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/get_hosts_lan.sh     dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"

ansible -i /home/zhangwusheng/etc/ansible/yangzhou.hosts kafka -m  copy  -b -a "src=/home/zhangwusheng/usr/local/jmx-exporter    dest=/home/zhangwusheng/usr/local/  owner=zhangwusheng group=zhangwusheng"


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/vivo.mount     dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "mkfs.xfs /dev/sdb"
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "mkdir /data1 /data2 /data3 /data4 /data5 /data6 /data7 /data8 /data9 /data10"


nohup bash /home/zhangwusheng/usr/bin/mkfs.vivo &
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/vivo.mkfs.sh     dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts host10 -m  shell  -b -a "bash /home/zhangwusheng/usr/bin/vivo.mkfs.sh"


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts host7 -m  shell  -b -a "bash /home/zhangwusheng/usr/bin/vivo.mount"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data1"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data1" |grep 'sdb'|wc -l
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data2" |grep 'sdc'|wc -l
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data3" |grep 'sdd'|wc -l
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data4" |grep 'sde'|wc -l
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data5" |grep 'sdf'|wc -l
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data6" |grep 'sdg'|wc -l
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data7" |grep 'sdh'|wc -l
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data8" |grep 'sdi'|wc -l
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data9" |grep 'sdj'|wc -l
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "df -h /data10" |grep 'sdk'|wc -l


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/fstab.sh     dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/fstab.py     dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m shell  -b -a "bash /home/zhangwusheng/usr/bin/fstab.sh"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts host1 -m shell  -b -a "cat /etc/fstab"


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/jce_policy-8.zip dest=/home/zhangwusheng/usr/bin  owner=zhangwusheng group=zhangwusheng"
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/jdk-8u211-linux-x64.tar.gz dest=/home/zhangwusheng/usr/bin  owner=zhangwusheng group=zhangwusheng"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/java-env.sh   dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/usr/bin/ulimit.sh   dest=/home/zhangwusheng/usr/bin/  owner=zhangwusheng group=zhangwusheng"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m shell  -b -a "bash /home/zhangwusheng/usr/bin/java-env.sh"
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts host1 -m shell  -b -a "ulimit -a"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts host1 -m shell  -b -a "bash /home/zhangwusheng/usr/bin/ulimit.sh"
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts host1 -m shell  -b -a "ulimit -a"


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/etc/security/limits.d/20-nproc.conf   dest=/etc/security/limits.d  owner=root group=root"


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/etc/yum.repos.d/ambari-hdp-1.repo   dest=/etc/yum.repos.d  owner=root group=root"
ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/etc/yum.repos.d/ambari.repo   dest=/etc/yum.repos.d  owner=root group=root"

ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  copy  -b -a "src=/home/zhangwusheng/.bash_profile   dest=/home/zhangwusheng/  owner=zhangwusheng group=zhangwusheng"


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts host1 -m  shell  -b -a "yum -y install ambari-agent"


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "sed -i 's/hostname=localhost/hostname=192.168.254.40/g'  /etc/ambari-agent/conf/ambari-agent.ini  "


ansible -i /home/zhangwusheng/etc/ansible/vivo.hosts all -m  shell  -b -a "date "


#查看vendor表
mysql

select event_time,channel,vendor_code,sum(req_cnt)/300
from CDN_LOG_BASE_V01 
where event_time>=1614924000
and  channel='apkgametopdxdl.vivo.com.cn'
group by event_time,channel,vendor_code
order by 2 desc

查看本网选择电信云，选择客户，可以看到云帆或者维沃的量
查看云帆或者阿里云，可以看到异网的量

```

网关配置：

route add -net 192.168.189.0/24 gw 192.168.254.254
/etc/sysconfig/static-routes

any net  192.168.189.0/24 gw 192.168.254.254

这个可以重启的时候生效

反向的话也是一样，在那边添加：
route add -net 192.168.254.0/24 gw 192.168.189.1




redis.conf
port 16379
bind 192.168.2.40
logfile "./redis.log"
dir ./
requirepass Redis1q2w3E
#daemonize yes

cd /home/zhangwusheng/cmdb/redis
nohup ./redis-server ./redis.conf &

#mongo

cd /home/zhangwusheng/cmdb/mongodb
nohup ./bin/mongod --dbpath=/home/zhangwusheng/cmdb/mongodb/data --bind_ip=192.168.2.40 --port 17017 --pidfilepath /home/zhangwusheng/cmdb/mongodb/mongod.pid &

/home/zhangwusheng/cmdb/mongodb/bin/mongo --host 192.168.2.40 --port 17017

use admin
db.createUser({user:'root',pwd:'Redis1q2w3E',roles:['root']})
db.auth('root','Redis1q2w3E')
db.createUser({user:"cdnlog",pwd:"cdnlog",roles:[{role:"readWrite",db:"cmdb"}]})
exit

find . -name ip.py|awk '{print "\\cp ./ip.py "$1;}'

python init.py --discovery  192.168.2.27:12181 --database cmdb --redis_ip 192.168.2.40  --redis_port 16379 --redis_pass Redis1q2w3E  --mongo_ip 192.168.2.40  --mongo_port 17017 --mongo_user cdnlog  --mongo_pass cdnlog --blueking_cmdb_url  http://192.168.2.40:18083 --listen_port  18083



init.py
"cmdb_apiserver":18282

./start.sh

cmdb/cmdb_apiserver/init_db.sh
修改8080为18282



# 77.K8S

https://www.e-learn.cn/topic/3851014



```
https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

https://stackoverflow.com/questions/46360361/invalid-x509-certificate-for-kubernetes-master

rm /etc/kubernetes/pki/apiserver.*
kubeadm init phase certs all --apiserver-advertise-address=0.0.0.0 --apiserver-cert-extra-sans=39.103.135.196,39.99.228.229
docker rm -f `docker ps -q -f 'name=k8s_kube-apiserver*'`
systemctl restart kubelet


kubectl -n kube-system get cm kubeadm-config -o yaml

grep -nri 172.21.162.49 .


```



# 78.Mysql查看分区

```bash
 https://www.cnblogs.com/pejsidney/p/10074980.html
 
 
 select 
  partition_name part,  
  partition_expression expr,  
  partition_description descr,  
  table_rows  
from information_schema.partitions  where 
  table_schema = schema()  
  and table_name='t_download_file_info';  
  
  
  
```






# 44.问题：

2019-12-30

1. /etc/hosts.allow权限太大
2. /etc/hosts 配置了两个 cdnlog040，一个内网一个外网

22机器：

ssh -p 9000 192.168.254.22 "chmod +x /data1/hadoop/yarn"

机器kylin的keytab都没有改



45.生产系统操作日志：



41开通防火墙，允许

| 日期       | 主机           | 操作                                | 原因                                                         |
| ---------- | -------------- | ----------------------------------- | ------------------------------------------------------------ |
| 2020-01-10 | 192.168.254.41 | 开通防火墙，允许122.237.100.139访问 | 监控组谢绍航从我们的metricsserver拉取数据，需要开放防火墙    |
|            |                |                                     | 命令：firewall-cmd --permanent --add-rich-rule 'rule family=ipv4 source address=122.237.100.139  port port=8800 protocol=tcp accept' |
|            |                |                                     | firewall-cmd --reload;firewall-cmd --list-all                |
|            |                |                                     | metricsserver地址：http://150.223.254.41:8800/cdnlog/metrics/platform |

122.237.100.139











# **后面废弃**.仅做备留









mapreduce.task.io.sort.mb





vi ./conf/kylin_job_conf_inmem.xml

这里会不会有问题?

<property>
        <name>mapreduce.task.io.sort.mb</name>
        <value>200</value>
        <description></description>
    </property>



麒麟安装在ambari上

<https://cloud.tencent.com/developer/article/1388578>



麒麟编译:

1,JAVA_HOME切换到jdk1.8

2.去掉cdh的仓库

3.去掉forbiddenapis插件

4.kylin-it和spark引擎增加

```
scala-maven-plugin

                <artifactId>scala-maven-plugin</artifactId>
                增加:
                <configuration>
                    <source>${javaVersion}</source>
                    <target>${javaVersion}</target>
                </configuration>
```



ES编译:

JAVA_HOME必须java12





org.apache.hadoop.mapred.FileInputFormat



```
  public static final String NUM_MAPS = "mapreduce.job.maps";


//总的大小除以Map数目
long goalSize = totalSize / (numSplits == 0 ? 1 : numSplits);
//SPLIT_MINSIZE:mapreduce.input.fileinputformat.split.minsize
//minSplitSize:sequence文件是10K,默认是1
long minSize = Math.max(job.getLong(org.apache.hadoop.mapreduce.lib.input.
  FileInputFormat.SPLIT_MINSIZE, 1), minSplitSize);

  long blockSize = file.getBlockSize();
          //goalSize:文件大小除以希望的map数
          //minSize:基本可以理解为:mapreduce.input.fileinputformat.split.minsize
          //blockSize:文件块大小
          //return Math.max(minSize, Math.min(goalSize, blockSize));
          //想要控制SplitSize,必须知道总的文件大小,Map数,配置的最小的split
          //
          long splitSize = computeSplitSize(goalSize, minSize, blockSize);

```





val textFile = sc.textFile("/tmp/messages2")

textFile .count()





mv /usr/bin/spark-class /usr/bin/spark-class-nono
mv /usr/bin/sparkR /usr/bin/sparkR-nono
mv /usr/bin/spark-script-wrapper.sh /usr/bin/spark-script-wrapper.sh-nono
mv /usr/bin/spark-shell /usr/bin/spark-shell-nono
mv /usr/bin/spark-sql /usr/bin/spark-sql-nono
mv /usr/bin/spark-submit /usr/bin/spark-submit-nono





vi spark-env.sh

export JAVA_HOME=/usr/local/jdk
export HADOOP_CONF_DIR=/etc/hadoop/conf
export SPARK_LOCAL_IP=10.142.235.1
export SPARK_HOME=/data2/spark-2.3.2-bin-hadoop2.7
export SPARK_MASTER_HOST=10.142.235.1
export SPARK_MASTER_PORT=7077
export SPARK_MASTER_WEBUI_PORT=8090
export SPARK_WORKER_PORT=8077
export SPARK_WORKER_WEBUI_PORT=9090





start-master.sh

start-slave.sh spark://192.168.1.73:7077



vi /usr/hdp/current/hive-client/bin/hive.distro

  if [ $SERVICE == "cli" -o $SERVICE == "beeline" ]
  then
      $TORUN -p hive -n root "$@"
  else
      $TORUN "$@"
  fi






export HADOOP_CONF_DIR=/usr/hdp/3.0.0.0-1634/hadoop/conf && /data1/spark-2.3.2-bin-hadoop2.7/bin/spark-submit --class org.apache.kylin.common.util.SparkEntry  --conf spark.executor.instances=40  --conf spark.yarn.queue=default  --conf spark.history.fs.logDirectory=hdfs:///kylin/spark-history  --conf spark.master=spark://192.168.1.73:7077  --conf spark.hadoop.yarn.timeline-service.enabled=false  --conf spark.executor.memory=4G  --conf spark.eventLog.enabled=true  --conf spark.eventLog.dir=hdfs:///kylin/spark-history  --conf spark.yarn.executor.memoryOverhead=1024  --conf spark.driver.memory=2G  --conf spark.shuffle.service.enabled=true --jars /data1/apache-kylin-2.6.1-bin-hadoop3/lib/kylin-job-2.6.1.jar /data1/apache-kylin-2.6.1-bin-hadoop3/lib/kylin-job-2.6.1.jar -className org.apache.kylin.engine.spark.SparkFactDistinct -counterOutput hdfs://hbase105.ecloud.com:8020/kylin/kylin_metadata/kylin-78b7f47f-e097-c81a-5751-600ee781c450/kylin_sales_cube/counter -statisticssamplingpercent 100 -cubename kylin_sales_cube -hiveTable default.kylin_intermediate_kylin_sales_cube_6331c840_1026_dd87_46f5_ef6a11bf2a03 -output hdfs://hbase105.ecloud.com:8020/kylin/kylin_metadata/kylin-78b7f47f-e097-c81a-5751-600ee781c450/kylin_sales_cube/fact_distinct_columns -input hdfs://hbase105.ecloud.com:8020/kylin/kylin_metadata/kylin-78b7f47f-e097-c81a-5751-600ee781c450/kylin_intermediate_kylin_sales_cube_6331c840_1026_dd87_46f5_ef6a11bf2a03 -segmentId 6331c840-1026-dd87-46f5-ef6a11bf2a03 -metaUrl kylin_metadata@hdfs,path=hdfs://hbase105.ecloud.com:8020/kylin/kylin_metadata/kylin-78b7f47f-e097-c81a-5751-600ee781c450/kylin_sales_cube/metadata



** 启动外部shuffle

** 修改这里:不要使用yarn

--conf spark.master=spark://192.168.1.73:7077

<http://140.246.128.62:18080/?showIncomplete=false>

cat ../conf/spark-defaults.conf

spark.history.fs.logDirectory=hdfs://hbase105.ecloud.com:8020/kylin/spark-history
spark.eventLog.enabled=true
spark.eventLog.dir=hdfs://hbase105.ecloud.com:8020/kylin/spark-history



高级配置:

kylin.engine.spark-conf.spark.master  spark://192.168.1.73:7077









 cat spark-defaults.conf

spark.history.fs.logDirectory=hdfs://hbase105.ecloud.com:8020/spark2-history
spark.eventLog.enabled=true
spark.eventLog.dir=hdfs://hbase105.ecloud.com:8020/spark2-history





cat spark-env.sh

export JAVA_HOME=/usr/local/jdk
export HADOOP_CONF_DIR=/etc/hadoop/conf
export SPARK_LOCAL_IP=192.168.1.73
export SPARK_HOME=/data1/spark-2.3.2-bin-hadoop2.7
export SPARK_MASTER_HOST=192.168.1.73
export SPARK_MASTER_PORT=7077
export SPARK_MASTER_WEBUI_PORT=8090
export SPARK_WORKER_PORT=8077
export SPARK_WORKER_WEBUI_PORT=9090





./start-master.sh

 ./start-slave.sh spark://192.168.1.73:7077

./start-shuffle-service.sh.

./start-history-server.sh



<http://140.246.128.62:18080/?showIncomplete=false>

<http://140.246.128.62:8090/>

kylin.engine.spark-conf.spark.master=spark://192.168.1.73:7077
kylin.engine.spark-conf.spark.eventLog.dir=hdfs\:///spark2-history
kylin.engine.spark-conf.spark.history.fs.logDirectory=hdfs\:///spark2-history
kylin.engine.spark-conf.spark.eventLog.enabled=true



hdfs  dfs -ls  /spark2-history



```
kylin.engine.spark.additional-jars
```





在YARN上的调试:

修改  SPARK_HOME

cat /etc/profile.d/spark.sh
#export SPARK_HOME=/data1/spark-2.3.2-bin-hadoop2.7
export SPARK_HOME=/usr/hdp/3.0.0.0-1634/spark2



把spark的beeline改名为spark-beeline





/etc/profile.d/spark.sh

export SPARK_HOME=/usr/hdp/3.0.0.0-1634/spark2
export PATH=$SPARK_HOME/bin:$PATH



kylin.properties

kylin.engine.spark-conf.spark.master=yarn

mv /usr/hdp/3.0.0.0-1634/spark2/bin/beeline /usr/hdp/3.0.0.0-1634/spark2/bin/spark-beeline



设置好spark的端口

sudo -u hdfs hdfs dfs -mkdir /kylin

sudo -u hdfs hdfs dfs -chown -R root:root  /kylin



```bash
vi  /usr/hdp/current/hive-client/bin/hive.distro

if [ $SERVICE == "beeline" -o $SERVICE == "cli" ]
  then
        $TORUN -p hive -n root "$@"
  else
        $TORUN "$@"
  fi

  /data2/apache-kylin-2.6.1-bin-hadoop3/bin/find-hive-dependency.sh
  第四十行:

if [ "${client_mode}" == "beeline" ]
then
    beeline_shell=`$KYLIN_HOME/bin/get-properties.sh kylin.source.hive.beeline-shell`
    beeline_params=`bash ${KYLIN_HOME}/bin/get-properties.sh kylin.source.hive.beeline-params`
    hive_env=`${beeline_shell} ${hive_conf_properties} ${beeline_params} --outputformat=dsv -e "set;" 2>&1 | grep --text 'env:CLASSPATH' `
else
    source ${dir}/check-hive-usability.sh
    hive_env=`hive ${hive_conf_properties} --outputformat=dsv -e set 2>&1 | grep 'env:CLASSPATH'`
fi

```



wget  https://archive.cloudera.com/cm6/6.2.0/cloudera-manager-installer.bin







cd  /var/lib/ambari-server/resources/stacks/HDP/3.0/services

mkdir KYLIN

metainfo.xml

```xml
<?xml version="1.0"?>
<metainfo>
    <schemaVersion>2.0</schemaVersion>
    <services>
        <service>
            <name>KYLIN</name>
            <displayName>Apache Kylin Service</displayName>
            <comment>Apache Kylin Service Added By zws</comment>
            <version>2.6.1</version>
            <components>
                <component>
                    <name>Kylin</name>
                    <displayName>Apache Kylin</displayName>
                    <category>MASTER</category>
                    <cardinality>1</cardinality>
                    <commandScript>
                        <script>scripts/master.py</script>
                        <scriptType>PYTHON</scriptType>
                        <timeout>600</timeout>
                    </commandScript>
                </component>

            </components>
            <osSpecifics>
                <osSpecific>
                    <osFamily>any</osFamily>
                </osSpecific>
            </osSpecifics>
        </service>
    </services>
</metainfo>
```





```
mkdir -p /var/lib/ambari-server/resources/stacks/HDP/3.0/services/KYLIN/package/scripts
```





```bash
VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
```





```
/usr/hdp/${hdp.version}/hadoop/lib/hadoop-lzo-.6.0.${hdp.version}.jar:
/etc/hadoop/conf/secure: bad substitution
```



It is caused by `hdp.version` not getting substituted correctly. You have to set `hdp.version` in the file `java-opts` under `$SPARK_HOME/conf`.

And you have to set

```
spark.driver.extraJavaOptions -Dhdp.version=XXX
spark.yarn.am.extraJavaOptions -Dhdp.version=XXX
```

in `spark-defaults.conf` under `$SPARK_HOME/conf` where XXX is the version of hdp.





mapreduce.job.acl-view-job = *





    Map Join:
    
    <property>
        <name>hive.auto.convert.join.noconditionaltask.size</name>
        <value>3221225472</value>
        <description>enable map-side join</description>
    </property>







wget -c 'http://mirror.bit.edu.cn/apache/tez/0.9.1/apache-tez-0.9.1-bin.tar.gz'



wget -c 'https://repository.apache.org/content/repositories/releases/org/apache/tez/tez-ui/0.9.1/tez-ui-0.9.1.war'



cp

## 5.修改用户名和密码：

加密密码：BCrypt   KYLIN@123!

```
org.apache.kylin.rest.security.PasswordPlaceholderConfigurer
工程：kylin-server-base
```

vi  /data1/apache-kylin-2.6.1-bin-hadoop3/tomcat/webapps/kylin/WEB-INF/classes/kylinSecurity.xml



CDNADMIN/KYLIN@123!

CDNMODELER/MODELER!@123#$%

CDNANALYST/ANALYST@1234@#&







ADMIN/KYLIN@123!

MODELER/MODELER!@123#$%

ANALYST/ANALYST@1234@#&

# 卸载:

如果只是重装，不要删除配置目录，只删除数据目录，然后ambari-server reset即可。

1. 查看日志里面安装了哪些包

   cat  /var/lib/ambari-agent/data/*|grep yum|grep install

2. 删除并且清理ambari的仓库

   cd /etc/yum.repos.d

   rm -f ambari* hdp.*

   yum makecache fast

3. 列出所有的已安装的包

   yum list installed|grep HDP|awk '{print "yum remove -y "$1;}'|sort -u

   yum list installed |grep hadoop

   yum list installed |grep HDP

   yum list installed |grep ambari

   yum list installed |grep HDP|awk '{print "rpm -e "$1;}'|sort -u

4. 删除数据目录！

   rm -rf


5.







yum list installed |grep HDP

yum list installed |grep 1634

yum list installed |grep ambari

yum list installed |grep HDP|awk '{print "rpm -e "$1;}'|sort -u





rm -rf /data1/hadoop
rm -rf /data2/hadoop
rm -rf /data3/hadoop
rm -rf /data4/hadoop
rm -rf /data5/hadoop
rm -rf /data6/hadoop
rm -rf /data7/hadoop
rm -rf /data8/hadoop
rm -rf /data9/hadoop
rm -rf /data10/hadoop





ambari-agent restart



NameNodeHA

namenode主机

sudo su hdfs -l -c 'hdfs dfsadmin -safemode enter'

sudo su hdfs -l -c 'hdfs dfsadmin -saveNamespace'

sudo su hdfs -l -c 'hdfs namenode -initializeSharedEdits'

sudo su hdfs -l -c 'hdfs zkfc -formatZK'



新的主机

sudo su hdfs -l -c 'hdfs namenode -bootstrapStandby'























```
dfs.namenode.http-bind-host
0.0.0.0
```

http://36.111.140.40:17080/ambari/HDP/centos7/3.0.0.0-1634/



sudo -u hdfs hdfs dfs -chmod -R a+rw /warehouse/tablespace/managed/hive





systemctl stop ntpd

ntpdate 192.168.2.40





生产TODO:

1. 修改zk的端口,yarn和hive都要做
2. 修改日志路径
3. 增加队列
4. 上kerberos





ambari-server:

hbase.root.dir:

file:///data7/var/lib/ambari-metrics-collector/hbase



# TimelineService

 sudo -u yarn hdfs dfs -mkdir -p /ats/hbase/coprocessor

sudo -u yarn hdfs dfs -put /usr/hdp/current/hadoop-yarn-timelineserver/timelineservice/hadoop-yarn-server-timelineservice-3.1.0.3.0.0.0-1634.jar /ats/hbase/coprocessor



原来的值为:

{{yarn_timeline_jar_location}}

修改为:

/ats/hbase/coprocessor/hadoop-yarn-server-timelineservice-3.1.0.3.0.0.0-1634.jar

```
<property>
  <name>yarn.timeline-service.hbase.coprocessor.jar.hdfs.location</name>
  <value>/ats/hbase/coprocessor/hadoop-yarn-server-timelineservice-3.1.0.3.0.0.0-1634.jar</value>
</property>
```



# 设置队列



capacity-scheduler=null
yarn.scheduler.capacity.default.minimum-user-limit-percent=100
yarn.scheduler.capacity.maximum-am-resource-percent=0.2
yarn.scheduler.capacity.maximum-applications=10000
yarn.scheduler.capacity.node-locality-delay=40
yarn.scheduler.capacity.resource-calculator=org.apache.hadoop.yarn.util.resource.DefaultResourceCalculator
yarn.scheduler.capacity.root.accessible-node-labels=*
yarn.scheduler.capacity.root.acl_administer_queue=*
yarn.scheduler.capacity.root.acl_submit_applications=*
yarn.scheduler.capacity.root.capacity=100
yarn.scheduler.capacity.root.default.acl_administer_jobs=*
yarn.scheduler.capacity.root.default.acl_submit_applications=*
yarn.scheduler.capacity.root.default.capacity=10
yarn.scheduler.capacity.root.default.maximum-capacity=100
yarn.scheduler.capacity.root.default.state=RUNNING
yarn.scheduler.capacity.root.default.user-limit-factor=1

yarn.scheduler.capacity.schedule-asynchronously.enable=true
yarn.scheduler.capacity.schedule-asynchronously.maximum-threads=1
yarn.scheduler.capacity.schedule-asynchronously.scheduling-interval-ms=10

yarn.scheduler.capacity.root.queues=default,develop
yarn.scheduler.capacity.root.develop.etl.acl_administer_jobs=*
yarn.scheduler.capacity.root.develop.etl.acl_submit_applications=*
yarn.scheduler.capacity.root.develop.etl.capacity=60
yarn.scheduler.capacity.root.develop.etl.maximum-capacity=100
yarn.scheduler.capacity.root.develop.etl.state=RUNNING
yarn.scheduler.capacity.root.develop.etl.user-limit-factor=1

yarn.scheduler.capacity.root.develop.kylin.acl_administer_jobs=*
yarn.scheduler.capacity.root.develop.kylin.acl_submit_applications=*
yarn.scheduler.capacity.root.develop.kylin.capacity=40
yarn.scheduler.capacity.root.develop.kylin.maximum-capacity=80
yarn.scheduler.capacity.root.develop.kylin.state=RUNNING
yarn.scheduler.capacity.root.develop.kylin.user-limit-factor=1

yarn.scheduler.capacity.root.develop.queues=etl,kylin





# TEZUI



yarn.timeline-service.webapp.address

timeline: "http://hbase135.ecloud.com:8188",



hadoop.http.cross-origin.allowed-origins *

yarn.resourcemanager.webapp.address

rm: "http://hbase73.ecloud.com:8088",



vi configs.env

```
<property>
      <name>tez.history.logging.service.class</name>
      <value>org.apache.tez.dag.history.logging.ats.ATSHistoryLoggingService</value>
</property>
<property>
       <description>URL for where the Tez UI is hosted</description>
       <name>tez.tez-ui.history-url.base</name>
       <value>http://36.111.140.41:28288/tez-ui/</value>
</property>
```

http://36.111.140.41:28288/tez-ui/#/?rowCount=100

# GC设置:

```bash
timestamp_str=`date +'%Y%m%d%H%M'`
rm_gc_log_name="{{yarn_log_dir_prefix}}/$USER/yarn-resourcemanager-gc-${timestamp_str}.log"
rm_gc_log_enable_opts="-verbose:gc -Xloggc:$rm_gc_log_name"
rm_gc_log_rotation_opts="-XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=10 -XX:GCLogFileSize=10M"
rm_gc_log_format_opts="-XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:+PrintGCDateStamps"
rm_gc_opts="-XX:+UseG1GC -XX:MaxGCPauseMillis=100 -XX:-ResizePLAB -XX:ErrorFile={{yarn_log_dir_prefix}}/rm_err_pid%p.log"
rm_OOMHANDLER="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath={{yarn_log_dir_prefix}}/resourcemanager-heapdump.hprof.${timestamp_str}"
rm_gc_log_opts="$rm_gc_log_enable_opts $rm_gc_log_rotation_opts $rm_gc_log_format_opts ${rm_gc_opts} ${rm_OOMHANDLER}"
YARN_RESOURCEMANAGER_OPTS="${YARN_RESOURCEMANAGER_OPTS} ${rm_gc_log_opts}"


function getGcOpts()
{
   local component_name=$1
   local timestamp_str=`date +'%Y%m%d%H%M'`
   local gc_log_filename="{{yarn_log_dir_prefix}}/gc-yarn-${component_name}-${timestamp_str}.log"
   local gc_log_enable_opts="-verbose:gc -Xloggc:${gc_log_filename}"
   local gc_log_rotation_opts="-XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=10 -XX:GCLogFileSize=10M"
   local gc_log_format_opts="-XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:+PrintGCDateStamps"
   local gc_opts="-XX:+UseG1GC -XX:MaxGCPauseMillis=100 -XX:-ResizePLAB "
   local gc_error_opt="-XX:ErrorFile={{yarn_log_dir_prefix}}/gc_err_${component_name}_pid%p.log"
   local gc_oom_opt="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath={{yarn_log_dir_prefix}}/heapdump-${component_name}-${timestamp_str}.hprof."

   echo "${gc_opts} ${gc_log_enable_opts} ${gc_log_rotation_opts} ${gc_log_format_opts} ${gc_error_opt} ${gc_oom_opt}"
}



function getHBaseGcOpts()
{
   local component_name=$1
   local timestamp_str=`date +'%Y%m%d%H%M'`
   local gc_log_filename="{{yarn_log_dir_prefix}}/gc-hbase-${component_name}-${timestamp_str}_pid%p.log"
   local gc_log_enable_opts="-verbose:gc -Xloggc:${gc_log_filename}"
   local gc_log_rotation_opts="-XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=10 -XX:GCLogFileSize=10M"
   local gc_log_format_opts="-XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:+PrintGCDateStamps"
   local gc_opts="-XX:+UseG1GC -XX:MaxGCPauseMillis=100 -XX:-ResizePLAB "
   local gc_error_opt="-XX:ErrorFile={{hbase_log_dir}}/gc_err_${component_name}_pid%p.log"
   local gc_oom_opt="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath={{hbase_log_dir}}/heapdump-${component_name}-${timestamp_str}.hprof."

   echo "${gc_opts} ${gc_log_enable_opts} ${gc_log_rotation_opts} ${gc_log_format_opts} ${gc_error_opt} ${gc_oom_opt}"
}

YARN_RESOURCEMANAGER_OPTS=`getGcOpts resourcemanager`
echo $YARN_RESOURCEMANAGER_OPTS
```



目前kylin 30个container

**kylin.storage.hbase.min-region-count**

​                                                               20

​                     **kylin.source.hive.redistribute-flat-table**

​                                                               false

​                     **kylin.engine.spark-conf.spark.executor.cores**

​                                                               2

​                     **kylin.engine.spark-conf.spark.yarn.queue**

​                                                               kylin

​                     **kylin.engine.spark-conf.spark.executor.instances**

​                                                               30

占了集群的65%,大概跑满了80%,所以这里可以配置成55%

kylin setenv.sh里面启用了 12G内存



如果想要跑到3分钟以内,要40个container,65%的资源,4分钟以内需要30个container,56的资源





# 加装机器:

1.杀掉所有的进程











# 修改内网网卡:

修改内网网卡 Advanced hadoop-env:

```
export MY_LOCAL_IP=`/sbin/ifconfig|grep 192|awk '{print $2;}'`
      export HADOOP_OPTS="-Djava.net.preferIPv4Stack=true ${HADOOP_OPTS} -Dlocal.bind.address=${MY_LOCAL_IP}"

```

dfs.datanode.ipc.address    ${local.bind.address}:8010

dfs.journalnode.http-address

​          [            ](http://36.111.140.40:18080/#)           [            ](http://36.111.140.40:18080/#)                 [            ](http://36.111.140.40:18080/#)





network.negotiate-auth.trusted-uris;http://t36:50070/,http://t36





hadoop.http.authentication.simple.anonymous.allowed   true

yarn.timeline-service.http-authentication.type kerberos->simple?

#





Zookeeper的修改:

```bash
#########################################################
cat $ZOOCFG |grep -v clientPortAddress > ${ZOOCFG}.2
MY_LOCAL_IP=`hostname`
echo "clientPortAddress=${MY_LOCAL_IP}" >> ${ZOOCFG}.2
mv ${ZOOCFG}.2 ${ZOOCFG}
#########################################################
```





# 替换SPARK包:

```bash
cp /usr/hdp/3.0.0.0-1634/hadoop/lib/jackson-core-2.9.5.jar

ls /usr/hdp/3.0.0.0-1634/spark2/jars/jackson--2.6.7
 ls /usr/hdp/3.0.0.0-1634/spark2/jars/jackson--2.9.5

mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar  /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar .BAK

mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-annotations-2.6.7.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-databind-2.6.7.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-core-2.6.7.jar.BAK
cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-databind-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-annotations-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-core-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars





#看这里==============================================
ls /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-*-2.6.7*jar

for ip in `echo 27 28 40 41 42 43 44 45`
do
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar  /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-databind-2.6.7.1.jar.BAK
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-core-2.6.7.jar.BAK
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-annotations-2.6.7.jar.BAK
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-jaxb-annotations-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-module-jaxb-annotations-2.6.7.jar.BAK
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-scala_2.11-2.6.7.1.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-module-scala_2.11-2.6.7.1.jar.BAK
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-dataformat-cbor-2.6.7.jar.BAK
done


手工上传jackson-dataformat-cbor-2.9.5.jar到目录/usr/hdp/3.0.0.0-1634/spark2/jars
cd /usr/hdp/3.0.0.0-1634/spark2/jars
for ip in `echo 27 28 41 42 43 44 45`
do
	scp /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.9.5.jar 192.168.2.${ip}:/usr/hdp/3.0.0.0-1634/spark2/jars/
done


for ip in `echo 27 28 40 41 42 43 44 45`
do
ssh 192.168.2.${ip} cp /usr/hdp/3.0.0.0-1634/hbase/lib/jackson-module-scala_2.11-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
ssh 192.168.2.${ip} cp /usr/hdp/3.0.0.0-1634/hadoop-yarn/lib/jackson-module-jaxb-annotations-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
ssh 192.168.2.${ip} cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-databind-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
ssh 192.168.2.${ip} cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-annotations-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
ssh 192.168.2.${ip} cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-core-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
done


ls /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-*-2.6.7*jar

反过来:

for ip in `echo 27 28 40 41 42 43 44 45`
do
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-databind-2.6.7.1.jar.BAK  /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-core-2.6.7.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.6.7.jar
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-annotations-2.6.7.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.6.7.jar
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-jaxb-annotations-2.6.7.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-module-jaxb-annotations-2.6.7.jar
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-scala_2.11-2.6.7.1.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-module-scala_2.11-2.6.7.1.jar
ssh 192.168.2.${ip} mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.6.7.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-dataformat-cbor-2.6.7.jar


ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.9.5.jar
ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.9.5.jar
ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.9.5.jar
ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-jaxb-annotations-2.9.5.jar
ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-scala_2.11-2.9.5.jar
ssh 192.168.2.${ip} rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.9.5.jar

done
```





# 系统安全

echo 'net.ipv4.tcp_sack = 0' >> /etc/sysctl.conf;sysctl -p



# 9.ES安装

useradd es

cd /data2

tar zxvf elasticsearch-6.7.0.tar.gz

su - es



[1]: max file descriptors [32768] for elasticsearch process is too low, increase to at least [65535]
[2]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]

sysctl -w vm.max_map_count=262144

ulimit -n 65535

 vim /etc/pam.d/sshd
session    required  /usr/lib64/security/pam_limits.so

vim /etc/ssh/sshd_config





# 8.主要问题

启动ranger时，数据库使用了utf8，导致字段长度超长，减少字段长度

Zeppelin缺少了/var/run/zeppelin需要手工创建

hdfs的一个配置错误，由1改为0；



OOZIE问题：

https://stackoverflow.com/questions/49276756/ext-js-library-not-installed-correctly-in-oozie

1. Stop Oozie service from Ambari
2. Copy it to the path:  /usr/hdp/current/oozie-client/libext/
3. /usr/hdp/current/oozie-server/bin/oozie-setup.sh prepare-war
4. Start Oozie again



Atlas：

[忘记密码了看这里](https://community.hortonworks.com/questions/144519/how-to-change-default-atlas-ui-admin-password.html)

Configs-> Advanced -> Advanced atlas-env -> Admin password

导入示例数据：

/usr/hdp/current/atlas-client/bin/quick_start.py 'http://t3s3.ecloud.com:21000'

# 安装kerberos

1.安装KDC Server

```
yum install krb5-server krb5-libs krb5-workstation krb5-devel -y

rpm -qa|grep krb5
krb5-workstation-1.15.1-37.el7_6.x86_64
krb5-libs-1.15.1-37.el7_6.x86_64
krb5-devel-1.15.1-37.el7_6.x86_64
krb5-server-1.15.1-37.el7_6.x86_64

这个 -37  -8  -18都可以的
汪聘  15:41:06
以前就遇到过-19 的不行

```

2.设置HOSTS

```bash
cat /etc/hosts

192.168.1.73 cdnlog.kdc.server

```

3.修改配置文件:/etc/krb5.conf

```bash
 cat /etc/krb5.conf
# Configuration snippets may be placed in this directory as well
includedir /etc/krb5.conf.d/

[logging]
 default = FILE:/var/log/krb5libs.log
 kdc = FILE:/var/log/krb5kdc.log
 admin_server = FILE:/var/log/kadmind.log

[libdefaults]
 dns_lookup_realm = false
 ticket_lifetime = 24h
 renew_lifetime = 7d
 forwardable = true
 rdns = false
 pkinit_anchors = /etc/pki/tls/certs/ca-bundle.crt
 default_realm = CDNLOG  #修改
 default_ccache_name = KEYRING:persistent:%{uid}

[realms]
CDNLOG = {  #修改
  kdc = 192.168.1.73 #修改
  admin_server = 192.168.1.73 #修改
 }

[domain_realm]
.ecloud.com=CDNLOG #修改
ecloud.com=CDNLOG  #修改

```

4.修改文件：/var/kerberos/krb5kdc/kdc.conf

```bash
------------------------------------
 cat /var/kerberos/krb5kdc/kdc.conf
[kdcdefaults]
 kdc_ports = 88
 kdc_tcp_ports = 88

[realms]
 CDNLOG = {
  #master_key_type = aes256-cts
  acl_file = /var/kerberos/krb5kdc/kadm5.acl
  dict_file = /usr/share/dict/words
  admin_keytab = /var/kerberos/krb5kdc/kadm5.keytab
  supported_enctypes = aes256-cts:normal aes128-cts:normal des3-hmac-sha1:normal arcfour-hmac:normal camellia256-cts:normal camellia128-cts:normal des-hmac-sha1:normal des-cbc-md5:normal des-cbc-crc:normal
 }
```

 4.修改其它配置文件

```bash
 ---------------------------------------------------
 cat /var/kerberos/krb5kdc/kadm5.acl
*/admin@CDNLOG  *
```

5.创建KDC数据库

```bash
kdb5_util create  -s -r CDNLOG
kdb5_util create  -s -r CTYUNCDN.NET
密码:cdnlog@kdc!@#
```

6.启动KDC数据库并设置开机启动

```bash
systemctl restart krb5kdc
systemctl restart kadmin
systemctl enable krb5kdc.service
systemctl enable kadmin.service
```

7.创建远程管理员

```
# kadmin.local -q "addprinc admin/admin@CDNLOG"
kadmin.local -q "addprinc admin/admin@CTYUNCDN.NET"
cdnlog@kdc!@#


kadmin.local -q "addprinc kadmin/192.168.1.66@CDNLOG"

Authenticating as principal root/admin@CDNLOG with password.
WARNING: no policy specified for admin/admin@CDNLOG; defaulting to no policy
Enter password for principal "admin/admin@CDNLOG":
Re-enter password for principal "admin/admin@CDNLOG":
Principal "admin/admin@CDNLOG" created.

# kadmin.local -q "xst -norandkey admin/admin@CDNLOG"
kadmin.local -q "xst -norandkey admin/admin@CTYUNCDN.NET"
cdnlog@kdc!@#

Authenticating as principal root/admin@CDNLOG with password.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type aes256-cts-hmac-sha1-96 added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type aes128-cts-hmac-sha1-96 added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type des3-cbc-sha1 added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type arcfour-hmac added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type camellia256-cts-cmac added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type camellia128-cts-cmac added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type des-hmac-sha1 added to keytab FILE:/etc/krb5.keytab.
Entry for principal admin/admin@CDNLOG with kvno 1, encryption type des-cbc-md5 added to keytab FILE:/etc/krb5.keytab.




kadmin.local
Authenticating as principal root/admin@CDNLOG with password.
kadmin.local:  listprincs
K/M@CDNLOG
admin/admin@CDNLOG
kadmin/admin@CDNLOG
kadmin/changepw@CDNLOG
kadmin/hbase73.ecloud.com@CDNLOG
kiprop/hbase73.ecloud.com@CDNLOG
krbtgt/CDNLOG@CDNLOG

kadmin.local:  addprinc root/admin
cdnlog@kdc!@#

WARNING: no policy specified for root/admin@CDNLOG; defaulting to no policy
Enter password for principal "root/admin@CDNLOG":
Re-enter password for principal "root/admin@CDNLOG":
Principal "root/admin@CDNLOG" created.
kadmin.local:
```

8.重启服务

```bash
systemctl restart kadmin.service
systemctl restart krb5kdc.service
```

9.下载jce for jdk8

http://www.oracle.com/technetwork/java/javase/downloads/jce8-download-2133166.html

上传到/data1

scp ./jce_policy-8.zip 192.168.1.105:/data1

scp ./jce_policy-8.zip 192.168.1.135:/data1



每台机器执行:

unzip -o -j -q  /data1/jce_policy-8.zip -d $JAVA_HOME/jre/lib/security



unzip -o -j -q  /data10/soft/jce_policy-8.zip  -d $JAVA_HOME/jre/lib/security

