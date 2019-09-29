# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
kafkamanager Params configurations
"""

# from resource_management.libraries.functions.version import format_hdp_stack_version, compare_versions
from resource_management import *
import status_params
import os

config = Script.get_config()


ambari_server_hostname = config['clusterHostInfo']['ambari_server_host'][0]
java64_home = config['hostLevelParams']['java_home']

hostname = config['hostname']


# kafkamanager env
kafka_manager_os_user = config['configurations']['kafkamanager-env']['kafkamanager.user']
kafka_manager_os_group = config['configurations']['kafkamanager-env']['kafkamanager.group']
kafka_manager_download_url = config['configurations']['kafkamanager-env']['kafkamanager.download.url']
kafka_manager_base_dir = config['configurations']['kafkamanager-env']['kafkamanager.base.dir']
kafka_manager_conf_dir = kafka_manager_base_dir + '/conf'
# kafka_manager_pid_dir = config['configurations']['kafkamanager-env']['kafkamanager.pid.dir'] 
kafka_manager_pid_file = format("{kafka_manager_base_dir}/RUNNING_PID")

#kafkamanager config
kafka_manager_http_port = config['configurations']['kafkamanager-config']['kafkamanager.http.port']
kafka_manager_zkhosts = config['configurations']['kafkamanager-config']['kafka-manager.zkhosts']

kafka_manager_basic_authentication_enabled = config['configurations']['kafkamanager-config']['basicAuthentication.enabled']
if kafka_manager_basic_authentication_enabled is True:
    kafka_manager_basic_authentication_enabled = "true"
else:
    kafka_manager_basic_authentication_enabled = "false"

kafka_manager_basic_authentication_user = config['configurations']['kafkamanager-config']['basicAuthentication.username']
kafka_manager_basic_authentication_password = config['configurations']['kafkamanager-config']['basicAuthentication.password']

#kafkamanager log
kafkamanager_log_dir = kafka_manager_base_dir + '/logs'
kafkamanager_install_log_file = kafkamanager_log_dir + '/kafkamanager-install.log'

