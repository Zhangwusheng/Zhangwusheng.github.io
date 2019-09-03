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

# 2.环境准备

**注意一定要上来先停掉防火墙，否则很容易出现莫名其妙的问题！！**



| IP            | 用途                                     |
| ------------- | ---------------------------------------- |
| 192.168.0.47  | 跳板机，安装httpserver，配置ambari本地源 |
| 192.168.0.193 | Namenode，ZooKeeper,DataNode             |
| 192.168.0.110 | NameNode，ZooKeeper,DataNode             |
| 192.168.0.201 | DataNode，ZooKeeper                      |

-   变量设置

```bash
#jdk安装软件所在目录
JAVA_SOFT=/data1/HDP-3.1
#HDP所在目录
HDP_SOFT=/data1/HDP-3.1
#所有机器IP列表,最后一位
HOSTS="36 66 160"

```

-   关闭防火墙

```
#每台机器执行
systemctl disable firewalld
systemctl stop firewalld
```

-   挂载磁盘

```bash
#每台机器执行，可以手动执行
mkfs.ext4 /dev/vdb 
mkdir /data1;
mount /dev/vdb /data1

#开机自动挂载fstab
#!/bin/bash

cat > /home/zhangwusheng/disk.awk<<EOF
{
if(\$2 ~ /sdb/){printf("UUID=%s  /data1  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sdc/){printf("UUID=%s  /data2  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sdd/){printf("UUID=%s  /data3  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sde/){printf("UUID=%s  /data4  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sdf/){printf("UUID=%s  /data5  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sdg/){printf("UUID=%s  /data6  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sdh/){printf("UUID=%s  /data7  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sdi/){printf("UUID=%s  /data8  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sdj/){printf("UUID=%s  /data9  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sdk/){printf("UUID=%s  /data10  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sdl/){printf("UUID=%s  /ssd1  ext4 defaults  0 0\\n",\$1);}
else if(\$2 ~ /sdm/){printf("UUID=%s  /ssd2  ext4 defaults  0 0\\n",\$1);}
}
EOF


ls -lart /dev/disk/by-uuid/|grep -e 'sd[bcdefghijklm]'|awk '{print $9" "$11;}'|awk -f /home/zhangwusheng/disk.awk > /home/zhangwusheng/etc_fstab.3

cat /etc/fstab|grep -v '/data'|grep -v '/ssd' > /home/zhangwusheng/etc_fstab.2
cat /home/zhangwusheng/etc_fstab.3 >> /home/zhangwusheng/etc_fstab.2
mv /etc/fstab /etc/fstab.`date +%s`
mv /home/zhangwusheng/etc_fstab.2 /etc/fstab

```

- 安装JDK

```bash
#每台机器执行
tar zxvf ${JAVA_SOFT}/jdk-8u161-linux-x64.tar.gz -C /usr/local/
rm -f /usr/local/jdk
ln -fs /usr/local/jdk1.8.0_161 /usr/local/jdk
```

- 设置JDK环境变量：

```bash
#每台机器执行
cat /etc/profile.d/java.sh 
echo 'export JAVA_HOME=/usr/local/jdk' > /etc/profile.d/java.sh
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile.d/java.sh
source /etc/profile.d/java.sh
```

- 设置ulimit：

```bash
#每台机器执行
echo '* soft nofile 65536' >> /etc/security/limits.conf
echo '* hard nofile 65536' >> /etc/security/limits.conf
echo '* soft nproc 131072' >> /etc/security/limits.conf
echo '* hard nproc 131072' >> /etc/security/limits.conf
echo '* soft core unlimited' >> /etc/security/limits.conf
cat /etc/security/limits.conf

#或者自动执行
cat /etc/security/limits.conf|grep -v nofile|grep -v nproc|grep -v 'soft core' > /home/zhangwusheng/limits.conf2
echo '* soft nofile 65536' >> /home/zhangwusheng/limits.conf2
echo '* hard nofile 65536' >> /home/zhangwusheng/limits.conf2
echo '* soft nproc 131072' >> /home/zhangwusheng/limits.conf2
echo '* hard nproc 131072' >> /home/zhangwusheng/limits.conf2
echo '* soft core unlimited' >> /home/zhangwusheng/limits.conf2

mv /etc/security/limits.conf /etc/security/limits.conf.`date +%s`
mv -f /home/zhangwusheng/limits.conf2 /etc/security/limits.conf

```
- 设置core文件：
```bash
mkdir -p /data2/core_files
echo '/data2/core_files/core-%e-%p-%t' > /proc/sys/kernel/core_pattern

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


- 设置hostname

```bash
#每台机器执行，每台机器hostname都不一样，这里根据IP设置HostName
HOST_PREFIX=hbase
HOST_POSTFIX="ecloud.com"
hostip=`ifconfig|grep 192|awk '{print $2;}'|awk -vhost=${HOST_PREFIX} -vdomain="${HOST_POSTFIX}" -F'.' '{print $4;}'`
echo "hostname ${HOST_PREFIX}${hostip}.${HOST_POSTFIX}"|bash
echo "${HOST_PREFIX}${hostip}.${HOST_POSTFIX}" > /etc/hostname
cat /etc/hostname
```

-   设置hosts文件


```bash
#每台机器执行
HOST_PREFIX=hbase
HOST_POSTFIX="ecloud.com"
grep -v ecloud  /etc/hosts  > /etc/hosts2 
for ip in `echo ${HOSTS}`
do	
 echo "192.168.1.${ip}  ${HOST_PREFIX}${ip}.${HOST_POSTFIX}" >> /etc/hosts2
done
mv -f /etc/hosts2 /etc/hosts
cat /etc/hosts
```


- 设置ssh免密登录

```bash
#从Ambari主机免密登录到其他三台机器
ssh-keygen -t rsa 
ssh-copy-id hbase36.ecloud.com
ssh-copy-id hbase66.ecloud.com
ssh-copy-id hbase160.ecloud.com
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

- 禁用IPV6


```bash
#这样幂等
echo 1> /proc/sys/net/ipv6/conf/all/disable_ipv6 
echo 1> /proc/sys/net/ipv6/conf/default/disable_ipv6 
#或者这样也行
grep -v 'net.ipv6.conf.all.disable_ipv6=1' /etc/sysctl.conf > /etc/sysctl.conf2
grep -v 'net.ipv6.conf.default.disable_ipv6=1' /etc/sysctl.conf2 > /etc/sysctl.conf3
mv /etc/sysctl.conf3 /etc/sysctl.conf
sysctl  -p
```

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

#不能ssh-copy-id的时候手工编辑这个文件，把pub文件拷贝过来
vi /root/.ssh/authorized_keys
#一定要修改权限
chmod 644 /root/.ssh/authorized_keys

```



# 3.配置YUM离线源

***Amber-Server服务器执行，自己选择一台机器作为AmbariServer***

- 安装httpd并且修改端口

```bash
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
baseurl=http://192.168.1.36:18181/ambari/ambari/centos7/2.7.3.0-139/
gpgcheck=0
EOF

#检查是否正确
yum repolist
#yum clean all
#yum makecache

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

- 修改配置

  vi /var/lib/pgsql/data/pg_hba.conf

  host    all   hive   10.142.235.1/24         md5

- 重启服务

  systemctl restart postgresql

- 增加权限

  su postgres

  psql

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
```
> kerberos有版本要求 -37  -8  -18都可以，但是以前就遇到过-19 的不行（汪聘）

每台机器安装jce

```bash
https://www.oracle.com/technetwork/java/javase/downloads/jce-all-download-5170447.html
C:\work\Source\
unzip -o -j -q /data1/jce_policy-8.zip -d $JAVA_HOME/jre/lib/security/
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

 see https://www.jianshu.com/p/54cd2a659698
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

```



## 5.创建KDC数据库

```bash
kdb5_util create  -s -r CTYUN.NET
密码:cdnlog@kdc!@#
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

#ktadd host/hbase36.ecloud.com

首先在40master上添加如下两个账号;

addprinc kadmin/cdnlog036.ctyun.net

addprinc kadmin/cdnlog039.ctyun.net

addprinc kiprop/cdnlog036.ctyun.net

addprinc kiprop/cdnlog039.ctyun.net

cdnlog@kdc!@#

master上：

```bash
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



## 11.KDC保活

vi /usr/lib/systemd/system/krb5kdc.service 

[Service]
Restart=on-abnormal

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

下载jce



jdk8









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



# 12.Kylin安装

## 1.增加kylin用户

```bash
groupadd cdnlog
useradd kylin -g cdnlog
usermod -G hadoop kylin
echo 'kylin   ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers
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



## 10.使用经验

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

# 13.集群参数优化

TODO，参照现有集群

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

- 创建全新的Kafka环境

```
NEW_ZK_DIR="kafka-test-auth3"
/usr/hdp/current/zookeeper-client/bin/zkCli.sh -server ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181 create /${NEW_ZK_DIR} "data-of-${NEW_ZK_DIR}"
```



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

#调试
topicName=DebugTopic
ZK_CONN="cdnlog040.ctyun.net:12181/cdnlog-first"
#建立topic
/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper ${ZK_CONN}  --topic ${topicName}    --partitions 1 --replication-factor 3
#授权
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN} --add --allow-principal User:${topicName} --topic ${topicName}   --producer

#验证权限
/usr/hdp/current/kafka-broker/bin/kafka-acls.sh -authorizer-properties zookeeper.connect=${ZK_CONN} --list  --topic ${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=${ZK_CONN}  --add --allow-principal User:${topicName} --topic ${topicName}   --consumer --group grp-${topicName}

/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list cdnlog003.ctyun.net:5044  --topic DebugTopic --producer-property security.protocol=SASL_PLAINTEXT --producer-property sasl.mechanism=PLAIN

#修改好consumer的kafka_client_jaas_conf，然后修改好consumer.properties 
/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --bootstrap-server cdnlog003.ctyun.net:5044  --topic DebugTopic --consumer-property security.protocol=SASL_PLAINTEXT --consumer-property  sasl.mechanism=PLAIN  --from-beginning --group grp-DebugTopic 


```







# 18.KafkaManager

1.下载

https://github.com/yahoo/kafka-manager/releases

2.解压

cd  /c/Work/Source/kafka-manager-2.0.0.2

./sbt

生成配置包

3.配置application.conf的zk

kafka-manager.zkhosts="ctl-nm-hhht-yxxya6-ceph-008.ctyuncdn.net:12181,ctl-nm-hhht-yxxya6-ceph-009.ctyuncdn.net:12181/kafka-manager"

zk上需要建立/kafka-manager目录

4.启动

```
nohup /data2/kafka-manager-2.0.0.2/bin/kafka-manager -Dconfig.file=/data2/kafka-manager-2.0.0.2/conf/application.conf -Dhttp.port=19090  -Dapplication.home=/data2/kafka-manager/kafka-manager-2.0.0.2 &
```

5.新增配置；

zookeeper hosts：

cdnlog041.ctyun.net:12181,cdnlog042.ctyun.net:12181/cdnlog-first

version: 2.0.0

Security Protocol: SASL_PLAINTEXT

SASL Mechanism :PLAIN

SASL JAAS Config:org.apache.kafka.common.security.plain.PlainLoginModule required  username="admin" password="CtYiofnwk@269Mn" ; 

# 19.Kafaka配置？

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



vi kafka-run-class.sh 

最后面开始执行程序时增加：

#zws added
bash $base_dir/bin/ctg-kafka-rack.sh

cp /etc/hadoop/3.1.0.0-78/0/topology_script.py  /usr/hdp/current/kafka-broker/conf/kafka-topology_script.py

cp /etc/hadoop/3.1.0.0-78/0/topology_mappings.data  /usr/hdp/current/kafka-broker/conf/kafka_topology_mappings.data

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



18.生产手记：

kafka: 5044  JMX：5090

# 20.KDC主从

todo：

1.定期备份kdc数据库

2.增加一台免密机器



参见10.10小节

# 21.卸载:

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

   rm -rf  XXXX 



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
```

## 6.修改火狐配置：

1. 地址栏输入： about:config

2.  network.negotiate-auth.trusted-uris设置为 cdnlog040.ctyun.net（多个主机以,分割）

   network.auth.use-sspi设置为false





































































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





部署flink：

```bash
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

























# **后面废弃**.仅做备留

--------------------------------------

7. 修改find-hive-dependency.sh

37和42行增加: --outputformat=dsv



```bash

vi /usr/hdp/3.0.0.0-1634/hive/bin/hive.distro

if [ "$TORUN" = "" ] ; then
  echo "Service $SERVICE not found"
  echo "Available Services: $SERVICE_LIST"
  exit 7
else
  set -- "${SERVICE_ARGS[$@]}"
  if [ $SERVICE == "beeline" -o $SERVICE == "cli" ]
  then
    $TORUN -p hive -n kylin "$@"
  else
    $TORUN "$@"
  fi

  $TORUN "$@"
fi
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

