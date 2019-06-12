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

[Ambari官方文档](https://docs.hortonworks.com/HDPDocuments/Ambari-2.7.0.0/bk_ambari-installation/content/setting_up_a_local_repository_with_temporary_internet_access.html)

[网上的一片博客](https://www.cnblogs.com/zhang-ke/p/8944240.html)

# 1.下载离线安装包

see [ambari2.7.0.0](https://docs.hortonworks.com/HDPDocuments/Ambari-2.7.0.0/bk_ambari-installation/content/ambari_repositories.html) && [hdp-3.0.0](https://docs.hortonworks.com/HDPDocuments/Ambari-2.7.0.0/bk_ambari-installation/content/hdp_30_repositories.html)

ambari-2.7.0.0

wget -c 'http://public-repo-1.hortonworks.com/ambari/centos7/2.x/updates/2.7.0.0/ambari-2.7.0.0-centos7.tar.gz'

wget -c 'http://public-repo-1.hortonworks.com/HDP/centos7/3.x/updates/3.0.0.0/HDP-3.0.0.0-centos7-rpm.tar.gz'
wget -c 'http://public-repo-1.hortonworks.com/HDP-UTILS-1.1.0.22/repos/centos7/HDP-UTILS-1.1.0.22-centos7.tar.gz'
wget -c 'http://public-repo-1.hortonworks.com/HDP-GPL/centos7/3.x/updates/3.0.0.0/HDP-GPL-3.0.0.0-centos7-gpl.tar.gz'

wget http://www.boutell.com/rinetd/http/rinetd.tar.gz



ambari-2.7.3.0

https://docs.hortonworks.com/HDPDocuments/Ambari-2.7.3.0/bk_ambari-installation/content/hdp_31_repositories.html



http://public-repo-1.hortonworks.com/ambari/centos7/2.x/updates/2.7.3.0/ambari-2.7.3.0-centos7.tar.gz

http://public-repo-1.hortonworks.com/HDP/centos7/3.x/updates/3.1.0.0/HDP-3.1.0.0-centos7-rpm.tar.gz

http://public-repo-1.hortonworks.com/HDP-UTILS-1.1.0.22/repos/centos7/HDP-UTILS-1.1.0.22-centos7.tar.gz

http://public-repo-1.hortonworks.com/HDP-GPL/centos7/3.x/updates/3.1.0.0/HDP-GPL-3.1.0.0-centos7-gpl.tar.gz



# 2.环境准备

**注意一定要上来先停掉防火墙，否则很容易出现网络问题！！**



| IP            | 用途                                     |
| ------------- | ---------------------------------------- |
| 192.168.0.47  | 跳板机，安装httpserver，配置ambari本地源 |
| 192.168.0.193 | Namenode，ZooKeeper,DataNode             |
| 192.168.0.110 | NameNode，ZooKeeper,DataNode             |
| 192.168.0.201 | DataNode，ZooKeeper                      |



 mkfs.ext4 /dev/vdb 

mkdir /data1;mount /dev/vdb /data1

- 下载jdk-8u161-linux-x64.tar.gz

```shell
tar zxvf /data1/jdk-8u161-linux-x64.tar.gz -C /usr/local/
ln -fs /usr/local/jdk1.8.0_161 /usr/local/jdk
```

- 设置环境变量：

```
#每台机器执行
cat /etc/profile.d/java.sh 
echo 'export JAVA_HOME=/usr/local/jdk' > /etc/profile.d/java.sh
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile.d/java.sh
source /etc/profile.d/java.sh
```

- 设置ulimit：

```
#每台机器执行
cat /etc/security/limits.conf
# End of file
* soft nofile 65536
* hard nofile 65536
* soft nproc 131072
* hard nproc 131072

echo '* soft nofile 65536' >> /etc/security/limits.conf
echo '* hard nofile 65536' >> /etc/security/limits.conf
echo '* soft nproc 131072' >> /etc/security/limits.conf
echo '* hard nproc 131072' >> /etc/security/limits.conf
echo '* soft core unlimited' >> /etc/security/limits.conf

mkdir -p /data2/core_files
echo '/data2/core_files/core-%e-%p-%t' > /proc/sys/kernel/core_pattern

```

- 设置hostname

```
  #每台机器执行，每台机器hostname都不一样
  hostname XXXX
  vi  /etc/hostname
  
  echo hbase171 > /etc/hostname
```

-   设置hosts文件


```
  #每台机器执行
  # cat /etc/hosts
  
  192.168.0.47   t3m1.ecloud.com t3m1
  192.168.0.193  t3m2.ecloud.com t3m2
  192.168.0.110  t3s1.ecloud.com t3s1
  192.168.0.201  t3s3.ecloud.com t3s3
  
  
  
  192.168.1.73  hbase73.ecloud.com hbase73
  192.168.1.105  hbase105.ecloud.com hbase105
  192.168.1.135  hbase135.ecloud.com hbase135
  
  
  echo '192.168.1.177  hbase177.ecloud.com hbase177' >> /etc/hosts
  echo '192.168.1.197  hbase197.ecloud.com hbase197' >> /etc/hosts
  echo '192.168.1.246  hbase246.ecloud.com hbase246' >> /etc/hosts
  
  sed -i -e 's/t197/hbase197/g' -e 's/t246/hbase246/g' -e  's/t177/hbase177/g' /etc/hosts 
```

-   关闭防火墙

```
#每台机器执行
systemctl disable firewalld
systemctl stop firewalld
```

- 设置ssh免密登录

```
#从跳板机免密登录到其他三台机器
ssh-keygen -t rsa  
ssh-copy-id t3m2
ssh-copy-id t3s1
ssh-copy-id t3s3
```

-   ntp服务

```
#跳板机做ntpserver
yum -y install ntp

#其实这里不改也行
vi /etc/ntp.conf
restrict 192.168.0.193 mask 255.255.255.0
restrict 192.168.0.110 mask 255.255.255.0
restrict 192.168.0.201 mask 255.255.255.0

systemctl start ntpd.service 
systemctl enable ntpd.service 

#首先同步跳板机的时间
ntpdate 0.centos.pool.ntp.org
```

可以不设置。

```
#在其他三台节点上执行，以跳板机的为准
crontab -e
0-59/10 * * * * /usr/sbin/ntpdate t3m1
```

上面这一步为必须设置的步骤。

临时关闭selinux

```
sestatus
setenforce 0
getenforce


临时关闭：
[root@localhost ~]# getenforce
Enforcing
[root@localhost ~]# setenforce 0
[root@localhost ~]# getenforce
Permissive

永久关闭：
[root@localhost ~]# vim /etc/sysconfig/selinux
SELINUX=enforcing 改为 SELINUX=disabled

```

- 禁用IPV6


```bash
echo 'net.ipv6.conf.all.disable_ipv6=1' >> /etc/sysctl.conf 
echo 'net.ipv6.conf.default.disable_ipv6=1' >> /etc/sysctl.conf 
sysctl  -p
```

- ssh设置


```bash
mkdir /root/.ssh;chmod 600 /root/.ssh

允许ROOT ssh

vi /etc/ssh/sshd_config

#PermitRootLogin no
PermitRootLogin yes



systemctl restart sshd

修改:

vi /etc/hosts.allow

sshd:36.111.140.40:allow

vi /root/.ssh/authorized_keys

chmod 644 /root/.ssh/authorized_keys

```

- 修改core文件

  

  ```bash
  3、core文件的设置
       1)/proc/sys/kernel/core_uses_pid可以控制core文件的问价名是否添加PID作为扩展，文件的内容为1，
             标识添加PID作为扩展，生成的core文件格式为core.XXXX;为0则表示生成的core文件统一命名为
            core；可通过一下命令修改此文件：
             echo "1" > /proc/sys/kernel/core_uses_pid
       2）core文件的保存位置和文件名格式
           echo "/corefile/core-%e-%p-%t" > core_pattern，可以将core文件统一生成到/corefile目录
            下，产生的文件名为core-命令名-pid-时间戳
             以下是参数列表:
             %p - insert pid into filename 添加pid
             %u - insert current uid into filename 添加当前uid
             %g - insert current gid into filename 添加当前gid
             %s - insert signal that caused the coredump into the filename 添加导致产生core的信号
             %t - insert UNIX time that the coredump occurred into filename 添加core文件生成的unix时间
            %h - insert hostname where the coredump happened into filename 添加主机名
             %e - insert coredumping executable name into filename 添加命令名
             
             
             
             
             
     mkdir -p /data1/core_files
     echo '/data1/core_files/core-%e-%p-%t' > /proc/sys/kernel/core_pattern
  ```

  









# 3.离线YUM源配置

跳板机服务器执行：

```
yum -y install httpd


修改默认端口
vi /etc/httpd/conf/httpd.conf 
Listen 80
改为：
Listen 8181

systemctl restart httpd 
检查启动情况：
netstat -anp|grep 8181

cd /var/www/html/

mkdir -p /var/www/html/ambari
cd /data1/HDP-3.0.0/

tar zxvf ambari-2.7.0.0-centos7.tar.gz -C /var/www/html/ambari
tar zxvf HDP-3.0.0.0-centos7-rpm.tar.gz  -C /var/www/html/ambari
tar zxvf HDP-UTILS-1.1.0.22-centos7.tar.gz -C  /var/www/html/ambari
tar zxvf HDP-GPL-3.0.0.0-centos7-gpl.tar.gz -C /var/www/html/ambari

#访问192.168.0.47/ambari看看能否访问

yum install yum-utils createrepo yum-plugin-priorities -y

cp /var/www/html/ambari/ambari/centos7/2.7.0.0-897/ambari.repo /etc/yum.repos.d/

vi /etc/yum.repos.d/ambari.repo 
#修改baseurl和gpgcheck
[ambari-2.7.0.0]
name=HDP Version - ambari-2.7.0.0
baseurl=http://192.168.0.47/ambari/ambari/centos7/2.7.0.0-897/
gpgcheck=0

cp /var/www/html/ambari/HDP/centos7/3.0.0.0-1634/hdp.repo /etc/yum.repos.d/

vi /etc/yum.repos.d/hdp.repo 
[HDP-3.0.0.0]
name=HDP Version - HDP-3.0.0.0
baseurl=http://192.168.0.47/ambari/HDP/centos7/3.0.0.0-1634
gpgcheck=0
[HDP-UTILS-1.1.0.22]
name=HDP-UTILS Version - HDP-UTILS-1.1.0.22
baseurl=http://192.168.0.47/ambari/HDP-UTILS/centos7/1.1.0.22
gpgcheck=0

vi /etc/yum.repos.d/hdp.gpl.repo 

baseurl=http://192.168.0.47/ambari/HDP-GPL/centos7/3.0.0.0-1634
gpgcheck=0


--------------------------------------------
vi /etc/yum.repos.d/ambari.repo 

[ambari-2.7.0.0]
name=HDP Version - ambari-2.7.0.0
baseurl=http://192.168.1.4:8081/ambari/ambari/centos7/2.7.0.0-897/
gpgcheck=0

[HDP-3.0.0.0]
name=HDP Version - HDP-3.0.0.0
baseurl=http://192.168.1.4:8081/ambari/HDP/centos7/3.0.0.0-1634
gpgcheck=0

[HDP-UTILS-1.1.0.22]
name=HDP-UTILS Version - HDP-UTILS-1.1.0.22
baseurl=http://192.168.1.4:8081/ambari/HDP-UTILS/centos7/1.1.0.22
gpgcheck=0

[HDP-GPL-3.0.0.0]
name=HDP GPL Version - HDP-3.0.0.0
baseurl=http://192.168.1.4:8081/ambari/HDP-GPL/centos7/3.0.0.0-1634
gpgcheck=0


sed -i 's/192.168.1.4:8081/192.168.1.177:8081/g' /etc/yum.repos.d/ambari.repo 

vi替换
:%s/
--------------------------------------------------

--------------------------------------------
[ambari-2.7.3.0]
name=HDP Version - ambari-2.7.3.0
baseurl=http://192.168.1.171:17280/ambari/ambari/centos7/2.7.3.0-139/
gpgcheck=0

[HDP-3.1.0.0]
name=HDP Version - HDP-3.1.0.0
baseurl=http://192.168.1.171:17280/ambari/HDP/centos7/3.1.0.0-78/
gpgcheck=0
[HDP-UTILS-1.1.0.22]
name=HDP-UTILS Version - HDP-UTILS-1.1.0.22
baseurl=http://192.168.1.171:17280/ambari/HDP-UTILS/centos7/1.1.0.22/
gpgcheck=0

[HDP-GPL-3.1.0.0]
name=HDP GPL Version - HDP-3.0.0.0
baseurl=http://192.168.1.171:17280/ambari/HDP-GPL/centos7/3.1.0.0-78/
gpgcheck=0
--------------------------------------------------



#clean这一步我觉得没有必要
yum clean all
yum makecache
yum repolist

出问题的话可以这样子：
rm -rf /var/lib/rpm/__db*



scp /etc/yum.repos.d/hdp.repo t3m2:/etc/yum.repos.d
scp /etc/yum.repos.d/ambari.repo t3m2:/etc/yum.repos.d
scp /etc/yum.repos.d/hdp.gpl.repo t3m2:/etc/yum.repos.d
ssh t3m2 yum makecache
ssh t3m2 yum repolist

scp /etc/yum.repos.d/hdp.repo t3s1:/etc/yum.repos.d
scp /etc/yum.repos.d/ambari.repo t3s1:/etc/yum.repos.d
scp /etc/yum.repos.d/hdp.gpl.repo t3s1:/etc/yum.repos.d
ssh t3s1 yum makecache
ssh t3s1 yum repolist

scp /etc/yum.repos.d/hdp.repo t3s3:/etc/yum.repos.d
scp /etc/yum.repos.d/ambari.repo t3s3:/etc/yum.repos.d
scp /etc/yum.repos.d/hdp.gpl.repo t3s3:/etc/yum.repos.d
ssh t3s3 yum makecache
ssh t3s3 yum repolist



yum install -y ambari-server

vi /etc/sysctl.conf 
net.ipv6.conf.all.disable_ipv6=1
net.ipv6.conf.default.disable_ipv6=1
sysctl  -p
```




# 4.安装mysql

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
CREATE USER 'ambari'@'%' IDENTIFIED BY 'ambari'; 
GRANT ALL PRIVILEGES ON *.* TO 'ambari'@'%';  

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

## Hive使用Postgresql:

vi /var/lib/pgsql/data/pg_hba.conf

host    all   hive   10.142.235.1/24         md5

systemctl restart postgresql

su postgres

psql

create user hive with password 'hive';

create database hive owner hive;
grant all privileges on database hive to hive;



create user root with password 'hive';

grant all privileges on database hive to root;

create user kylin with password 'hive';

grant all privileges on database hive to kylin ;

\q

ambari-server setup --jdbc-db=postgres --jdbc-driver=/usr/lib/ambari-server/postgresql-42.2.2.jar

jdbc:postgresql://hbase177.ecloud.com:5432/hive

org.postgresql.Driver



ambari-server setup --jdbc-db=postgres --jdbc-driver=/usr/lib/ambari-server/postgresql-42.2.2.jar



# 5.设置ambari-server并启动

```
ambari-server setup

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


ambari-server setup --jdbc-db=mysql --jdbc-driver=/usr/share/java/mysql-connector-java.jar


ambari-server start

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

vi /etc/ambari-server/conf/ambari.properties 
echo 'client.api.port=8081' >> /etc/ambari-server/conf/ambari.properties 
```

# 6.安装配置部署HDP集群

secucrt做了端口映射，把本机的8080 映射到了 192.168.0.47的8080

http://localhost:8080/#/login

admin/admin

本地仓库地址：

http://192.168.0.47/ambari/HDP/centos7/3.0.0.0-1634

http://192.168.0.47/ambari/HDP-GPL/centos7/3.0.0.0-1634

http://192.168.0.47/ambari/HDP-UTILS/centos7/1.1.0.22





http://192.168.1.73:8081/ambari/HDP/centos7/3.0.0.0-1634

http://192.168.1.73:8081/ambari/HDP-GPL/centos7/3.0.0.0-1634

http://192.168.1.73:8081/ambari/HDP-UTILS/centos7/1.1.0.22



第二步：

![1537716187931](/img/ambari-1537716187931.png)



第三步：

![1537716424901](/img/ambari-1537716424901.png)



第四步：



![1537717128168](/img/ambari-4-1537717128168.png)



这里可能需要修改:

vi  /etc/ambari-agent/conf/ambari-agent.ini

[server]
hostname=192.168.2.40


第五步：选择服务



![1537717293865](/img/ambari-5-1537717293865.png)





第六步：

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





# 7.主要问题

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









# 8.Kerberos安装

在KDC服务器安装

为了做KDC主备,我在几台机器上都安装了

yum -y install krb5-server krb5-devel

yum -y install krb5-workstation



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



每台机器都需要:
[root@hbase171 yum.repos.d]# cat /var/kerberos/krb5kdc/kdc.conf
[kdcdefaults]
 kdc_ports = 10088
 kdc_tcp_ports = 10088

[realms]
#change here
 ECLOUD.COM = {
  #master_key_type = aes256-cts
  acl_file = /var/kerberos/krb5kdc/kadm5.acl
  dict_file = /usr/share/dict/words
  admin_keytab = /var/kerberos/krb5kdc/kadm5.keytab
  supported_enctypes = aes256-cts:normal aes128-cts:normal des3-hmac-sha1:normal arcfour-hmac:normal camellia256-cts:normal camellia128-cts:normal des-hmac-sha1:normal des-cbc-md5:normal des-cbc-crc:normal
 }
 
 
 
 
 [root@hbase171 yum.repos.d]# cat /var/kerberos/krb5kdc/kadm5.acl
 #change here
*/admin@ECLOUD.COM     *



kdb5_util create -s -r ECLOUD.COM

[root@hbase171 3.1.0.0-78]#kdb5_util create -s -r ECLOUD.COM
Loading random data
Initializing database '/var/kerberos/krb5kdc/principal' for realm 'ECLOUD.COM',
master key name 'K/M@ECLOUD.COM'
You will be prompted for the database Master Password.
It is important that you NOT FORGET this password.
Enter KDC database master key: kerberos
Re-enter KDC database master key to verify: kerberos



[root@hbase171 3.1.0.0-78]#systemctl start krb5kdc
[root@hbase171 3.1.0.0-78]# systemctl enable  krb5kdc
Created symlink from /etc/systemd/system/multi-user.target.wants/krb5kdc.service to /usr/lib/systemd/system/krb5kdc.service.

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





[root@hbase106 ~]# cat /var/kerberos/krb5kdc/kdc.conf
[kdcdefaults]
 kdc_ports = 10088
 kdc_tcp_ports = 10088

[realms]
 ECLOUD.COM = {
  #master_key_type = aes256-cts
  acl_file = /var/kerberos/krb5kdc/kadm5.acl
  dict_file = /usr/share/dict/words
  admin_keytab = /var/kerberos/krb5kdc/kadm5.keytab
  supported_enctypes = aes256-cts:normal aes128-cts:normal des3-hmac-sha1:normal arcfour-hmac:normal camellia256-cts:normal camellia128-cts:normal des-hmac-sha1:normal des-cbc-md5:normal des-cbc-crc:normal
 }
 
 
 
[root@hbase106 ~]#  systemctl enadble kadmin.service
```

下载jce

https://www.oracle.com/technetwork/java/javase/downloads/jce-all-download-5170447.html

jdk8





unzip -o -j -q /data1/jce_policy-8.zip -d $JAVA_HOME/jre/lib/security/















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



# 10.Kylin安装

## 1.增加用户

```bash
groupadd cdnlog
useradd kylin -g cdnlog
```



## 2.设置环境变量

```bash
##Standalone版本
export KYLIN_HOME=/data1/apache-kylin-2.6.1-bin-hadoop3
export HADOOP_HOME=/usr/hdp/3.0.0.0-1634/hadoop
export SPARK_HOME=/data1/spark-2.3.2-bin-hadoop2.7
export PATH=$PATH:$SPARK_HOME/bin

##HDP版本
echo 'export SPARK_HOME=/usr/hdp/3.0.0.0-1634/spark2' > /etc/profile.d/spark.sh
echo 'export PATH=$PATH:$SPARK_HOME/bin' >> /etc/profile.d/spark.sh
mv /usr/hdp/3.0.0.0-1634/spark2/bin/beeline /usr/hdp/3.0.0.0-1634/spark2/bin/spark-beeline
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

## 4.修复Tomacat

```bash
cd /data1/apache-kylin-2.6.1-bin-hadoop3/tomcat/webapps
mkdir kylin
unzip  ../kylin.war 

上传 F:\Soft\HDP\Kylin
commons-configuration-1.6-zws-added.jar

```

https://blog.csdn.net/qq_42606051/article/details/82713476





$KYLIN_HOME/bin/check-env.sh



$KYLIN_HOME/bin/kylin.sh start



<http://140.246.128.62:7070/kylin/models>



修改hive脚本



```bash


vi  /usr/hdp/current/hive-client/bin/hive.distro 

$TORUN -p hive -n root "$@"

export spark_home=/usr/hdp/3.0.0.0-1634/spark2

 find -L $spark_home/jars -name '*.jar' ! -name '*slf4j*' ! -name '*calcite*' ! -name '*doc*' ! -name '*test*' ! -name '*sources*' ''-printf '%p:' | sed 's/:​$//'|awk -F':' '{for(i=1;i<=NF;i++){print $i;}}'



````





hive3问题:

spark问题

mr问题:

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




## 1.修改hive脚本

```bash
vi  /usr/hdp/current/hive-client/bin/hive.distro 

if [ $SERVICE == "beeline" -o $SERVICE == "cli" ]
then
    $TORUN -p hive -n root "$@"
else
    $TORUN "$@"
fi
  
############ /data2/apache-kylin-2.6.1-bin-hadoop3/bin/find-hive-dependency.sh
############  第四十行:
  
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

## 2.修改Kylin配置



#这里会影响清理Hbase的时间

kylin.storage.hbase.min-region-count=40

kylin.engine.spark.min-partition=200

kylin.engine.spark-conf.spark.master=yarn
kylin.engine.spark-conf.spark.eventLog.enabled=true
kylin.engine.spark-conf.spark.eventLog.dir=hdfs\:///spark2-history
kylin.engine.spark-conf.spark.history.fs.logDirectory=hdfs\:///spark2-history
kylin.engine.spark-conf.spark.executor.cores=2
kylin.engine.spark-conf.spark.executor.memory=18G
kylin.engine.spark-conf.spark.executor.instances=40

kylin.engine.spark-conf.spark.network.timeout=10000000 





## 3.修复Tomcat

copy spark的common configuration 1.6 jar包

并且修改 监听ipv4端口

<Connector port="80" maxHttpHeaderSize="8192" address="0.0.0.0"
               maxThreads="150" minSpareThreads="25" maxSpareThreads="75"
               enableLookups="false" redirectPort="8443" acceptCount="100"
               connectionTimeout="20000" disableUploadTimeout="true" />
--------------------- 


## 4.调整Hadoop参数

<1792,注意不要ArrayOutofIndex

5.



设置环境变量

cat /etc/profile.d//spark.sh 
#export SPARK_HOME=/data2/spark-2.3.2-bin-hadoop2.7
export SPARK_HOME=/usr/hdp/3.0.0.0-1634/spark2
export PATH=$SPARK_HOME/bin:$PATH



sudo -u hdfs hdfs dfs -mkdir /kylin

sudo -u hdfs hdfs dfs -chown -R root:root /kylin





调整分区个数:

kylin.engine.spark.min-partition=200

减少删除hbase的时间



## 

表删除测试;



hbase org.apache.hadoop.hbase.PerformanceEvaluation --nomapred
--rows=1000000 --presplit=10
sequentialWrite 1 





```
dfs.namenode.servicerpc-address.mycluster.nn1
```







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



cd /etc/yum.repos.d

rm -f ambari* hdp.*

yum makecache fast



yum list installed|grep HDP|awk '{print "yum remove -y "$1;}'|sort -u





yum list installed |grep hadoop



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

sudo su hdfs -l -c 'hdfs dfsadmin -safemode enter'

sudo su hdfs -l -c 'hdfs dfsadmin -saveNamespace'

sudo su hdfs -l -c 'hdfs namenode -initializeSharedEdits'

sudo su hdfs -l -c 'hdfs zkfc -formatZK'



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

# 安装kerberos



## HDP3.0 Ambari的几个坑:

1.yarn dns默认端口 hadoop自己是5353,安装的时候变成了53,导致启动yarndns的机器在运行kadmin时出问题
2.kerberos 一定要使用域名,不能使用IP
3.kerberos一定要他管理krb5.conf,不能清除那个选项,使用自己的配置文件





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



krb5-config --version



![1557912194106](/img/ambari-install-kerberos.png)







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

ls /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.6.7*jar

mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar  /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar .BAK

mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-annotations-2.6.7.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-databind-2.6.7.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-core-2.6.7.jar.BAK
cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-databind-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-annotations-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-core-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars



mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar  /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-databind-2.6.7.1.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-core-2.6.7.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-annotations-2.6.7.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-jaxb-annotations-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-module-jaxb-annotations-2.6.7.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-module-scala_2.11-2.6.7.1.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-module-scala_2.11-2.6.7.1.jar.BAK
mv /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.6.7.jar /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-dataformat-cbor-2.6.7.jar.BAK


手工上传jackson-dataformat-cbor-2.9.5.jar
cd /usr/hdp/3.0.0.0-1634/spark2/jars
scp /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.9.5.jar 192.168.1.66:/usr/hdp/3.0.0.0-1634/spark2/jars/
scp /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-dataformat-cbor-2.9.5.jar 192.168.1.66:/usr/hdp/3.0.0.0-1634/spark2/jars/


cp /usr/hdp/3.0.0.0-1634/hbase/lib/jackson-module-scala_2.11-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
cp /usr/hdp/3.0.0.0-1634/hadoop-yarn/lib/jackson-module-jaxb-annotations-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-databind-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-annotations-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars
cp /usr/hdp/3.0.0.0-1634/hadoop/client/jackson-core-2.9.5.jar /usr/hdp/3.0.0.0-1634/spark2/jars


ls /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-*-2.6.7*jar

反过来:
mv /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-databind-2.6.7.1.jar.BAK  /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.6.7.1.jar
mv /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-core-2.6.7.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.6.7.jar
mv /usr/hdp/3.0.0.0-1634/spark2/jars/../jackson-annotations-2.6.7.jar.BAK /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.6.7.jar

rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-databind-2.9.5.jar
rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-annotations-2.9.5.jar
rm -f /usr/hdp/3.0.0.0-1634/spark2/jars/jackson-core-2.9.5.jar

```





