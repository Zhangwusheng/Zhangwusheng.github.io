# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Elasticsearch  service params
"""

from resource_management import *

config = Script.get_config()

kafka_manager_base_dir = config['configurations']['kafkamanager-env']['kafkamanager.base.dir']
kafka_manager_pid_file = format("{kafka_manager_base_dir}/RUNNING_PID")

