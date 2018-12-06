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



wget -c 'http://public-repo-1.hortonworks.com/ambari/centos7/2.x/updates/2.7.0.0/ambari-2.7.0.0-centos7.tar.gz'

wget -c 'http://public-repo-1.hortonworks.com/HDP/centos7/3.x/updates/3.0.0.0/HDP-3.0.0.0-centos7-rpm.tar.gz'
wget -c 'http://public-repo-1.hortonworks.com/HDP-UTILS-1.1.0.22/repos/centos7/HDP-UTILS-1.1.0.22-centos7.tar.gz'
wget -c 'http://public-repo-1.hortonworks.com/HDP-GPL/centos7/3.x/updates/3.0.0.0/HDP-GPL-3.0.0.0-centos7-gpl.tar.gz'


wget http://www.boutell.com/rinetd/http/rinetd.tar.gz

# 2.环境准备

**注意一定要上来先停掉防火墙，否则很容易出现网络问题！！**



| IP            | 用途                                     |
| ------------- | ---------------------------------------- |
| 192.168.0.47  | 跳板机，安装httpserver，配置ambari本地源 |
| 192.168.0.193 | Namenode，ZooKeeper,DataNode             |
| 192.168.0.110 | NameNode，ZooKeeper,DataNode             |
| 192.168.0.201 | DataNode，ZooKeeper                      |



- 下载jdk-8u161-linux-x64.tar.gz

```shell
tar zxvf jdk-8u161-linux-x64.tar.gz -C /usr/local/
ln -fs /usr/local/jdk1.8.0_161 /usr/local/jdk
```

- 设置环境变量：

```
#每台机器执行
cat /etc/profile.d/java.sh 
export JAVA_HOME=/usr/local/jdk
export PATH=$JAVA_HOME/bin:$PATH
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

```

- 设置hostname

```
  #每台机器执行，每台机器hostname都不一样
  hostname XXXX
  vi  /etc/hostname
```

-   设置hosts文件


```
  #每台机器执行
  # cat /etc/hosts
  
  192.168.0.47   t3m1.ecloud.com t3m1
  192.168.0.193  t3m2.ecloud.com t3m2
  192.168.0.110  t3s1.ecloud.com t3s1
  192.168.0.201  t3s3.ecloud.com t3s3
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

禁用IPV6

vi /etc/sysctl.conf 
net.ipv6.conf.all.disable_ipv6=1
net.ipv6.conf.default.disable_ipv6=1
sysctl  -p

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
cd /data/zhangwusheng/HDP-3.0.0/

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



yum install ambari-server

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

```

# 6.安装配置部署HDP集群

secucrt做了端口映射，把本机的8080 映射到了 192.168.0.47的8080

http://localhost:8080/#/login

admin/admin

本地仓库地址：

http://192.168.0.47/ambari/HDP/centos7/3.0.0.0-1634

http://192.168.0.47/ambari/HDP-GPL/centos7/3.0.0.0-1634

http://192.168.0.47/ambari/HDP-UTILS/centos7/1.1.0.22



第二步：

![1537716187931](/img/ambari-1537716187931.png)



第三步：

![1537716424901](/img/ambari-1537716424901.png)



第四步：



![1537717128168](/img/ambari-4-1537717128168.png)



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