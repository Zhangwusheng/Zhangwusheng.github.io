---
layout:     post
title:     yum下载
subtitle:    "\"yum下载但是不安装软件\""
date:       2018-09-20
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - linux
    - yum
---
# How to use yum to download a package without installing it

 [原文在此](https://access.redhat.com/solutions/10154)

## Environment

- Red Hat Enterprise Linux (RHEL) 7
- Red Hat Enterprise Linux 6
- Red Hat Enterprise Linux 5

## Issue

- How do I use yum to download a package without installing it?

## Resolution

There are two ways to download a package without installing it.

One is using the "downloadonly" plugin for yum, the other is using "yumdownloader" utility.

### Downloadonly plugin for yum

1. Install the package including "downloadonly" plugin:

   ```
   (RHEL5)
   # yum install yum-downloadonly
   
   (RHEL6)
   # yum install yum-plugin-downloadonly
   ```

2. Run `yum` command with "--downloadonly" option as follows:


   ```
   # yum install --downloadonly --downloaddir=<directory> <package>
   ```

3. Confirm the RPM files are available in the specified download directory.

**Note:**

- Before using the plugin, check */etc/yum/pluginconf.d/downloadonly.conf* to confirm that this plugin is "enabled=1"
- This is applicable for "yum install/yum update" and not for "yum groupinstall". Use "yum groupinfo" to identify packages within a specific group.
- If only the package name is specified, the latest available package is downloaded (such as *sshd*). Otherwise, you can specify the full package name and version (such as *httpd-2.2.3-22.el5*).
- If you do not use the --downloaddir option, files are saved by default in */var/cache/yum/* in *rhel-{arch}-channel/packages*
- If desired, you can download multiple packages on the same command.
- You still need to re-download the repodata if the repodata expires before you re-use the cache. By default it takes two hours to expire.

### Yumdownloader

If downloading a installed package, "yumdownloader" is useful.

1. Install the yum-utils package:

   ```
   # yum install yum-utils
   ```

2. Run the command followed by the desired package:

   ```
   # yumdownloader <package>
   ```

**Note:**

- The package is saved in the current working directly by default; use the --destdir option to specify an alternate location.
- Be sure to add --resolve if you need to download dependencies.




This solution is part of Red Hat’s fast-track publication program, providing a huge library of solutions that Red Hat engineers have created while supporting our customers. To give you the knowledge you need the instant it becomes available, these articles may be presented in a raw and unedited form.