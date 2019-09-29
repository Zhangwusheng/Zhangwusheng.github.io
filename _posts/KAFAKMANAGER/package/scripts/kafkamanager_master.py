# -*- coding: utf-8 -*-

import sys, os, glob, pwd, grp, signal, time
from resource_management import *
from resource_management.core.logger import Logger 

class KafkaManagerMaster(Script):

    # Install Elasticsearch
    def install(self, env):
        import params
        env.set_params(params)

        # Install dependent packages: no dependencies
        #self.install_packages(env)

        # Create Group
        Logger.info( "creating group %s" % params.kafka_manager_os_group)
        try:
            grp.getgrnam(params.kafka_manager_os_group)
            Logger.info( "group %s exists" % params.kafka_manager_os_group)
        except Exception :
            Logger.info( "group not exists,creating %s " % params.kafka_manager_os_group)
            Group(params.kafka_manager_os_group,group_name=params.kafka_manager_os_group)
        Logger.info( "created group" )

        # # Create User
        Logger.info( "creating user %s" % params.kafka_manager_os_user )
        try:
            pwd.getpwnam(params.kafka_manager_os_user)
            Logger.info( "user %s exists" % params.kafka_manager_os_user)
        except Exception :
            Logger.info( "user not exists,creating user %s " % params.kafka_manager_os_user)
            # groups=params.kafka_manager_os_group.split(","),
            # groups=[params.kafka_manager_os_group],
            User(params.kafka_manager_os_user,username=params.kafka_manager_os_user,
                 gid=params.kafka_manager_os_group,
                 groups=params.kafka_manager_os_group.split(","),
                 ignore_failures=True
                 )
        Logger.info( "created User" )    

        # Create directories
        # Logger.info( "creating  Directory " )
        Logger.info( "creating Directory, basedir=%s,log_dir=%s" % (params.kafka_manager_base_dir, params.kafkamanager_log_dir))
        Directory([params.kafka_manager_base_dir, params.kafkamanager_log_dir],
                  mode=0755,
                  cd_access='a',
                  owner=params.kafka_manager_os_user,
                  group=params.kafka_manager_os_group,
                  create_parents=True
                  )
        Logger.info("Directory created...")
        # print "created  Directory" 

        # Create install log
        Logger.info( "creating install log File "+ params.kafkamanager_install_log_file )
        File(params.kafkamanager_install_log_file,
             mode=0644,
             owner=params.kafka_manager_os_user,
             group=params.kafka_manager_os_group,
             content='test'
             )
        Logger.info(  "created  File" )

        # Download Elasticsearch
        cmd = format("cd {kafka_manager_base_dir}; wget {kafka_manager_download_url} -O kafkamanager.tar.gz -a {kafkamanager_install_log_file}")
        Execute(cmd, user=params.kafka_manager_os_user)

        # Install Elasticsearch
        cmd = format("cd {kafka_manager_base_dir}; tar -xf kafkamanager.tar.gz --strip-components=1")
        Execute(cmd, user=params.kafka_manager_os_user)

        # Ensure all files owned by elasticsearch user
        cmd = format("chown -R {kafka_manager_os_user}:{kafka_manager_os_group} {kafka_manager_base_dir}")
        Execute(cmd)

        # Remove Elasticsearch installation file
        cmd = format("cd {kafka_manager_base_dir}; rm -fr kafkamanager.tar.gz")
        Execute(cmd, user=params.kafka_manager_os_user)

        Execute('echo "KafkaManager install complete"')
        Logger.info( "KafkaManager install complete" )

    # Configure Elasticsearch
    def configure(self, env):
        import params
        env.set_params(params)
        #generate configuration
        configurations = params.config['configurations']['kafkamanager-config']
        File(format("{kafka_manager_conf_dir}/application.conf"),
             content=Template("application.conf.j2", configurations=configurations),
             owner=params.kafka_manager_os_user,
             group=params.kafka_manager_os_group
             )

        # File(format("{kafka_manager_conf_dir}/application.conf"),
        #      content=Template("application.conf.j2", configurations=configurations),
        #      owner=params.kafka_manager_os_user,
        #      group=params.kafk_amanager_os_group
        #      )

        # env_configurations = params.config['configurations']['elasticsearch-env']
        # File(format("{es_master_conf_dir}/jvm.options"),
        #      content=Template("elasticsearch.jvm.options.j2", configurations=env_configurations),
        #      owner=params.kafka_manager_os_user,
        #      group=params.kafk_amanager_os_group
        #      )

        cmd = format("chown -R {kafka_manager_os_user}:{kafka_manager_os_group} {kafka_manager_base_dir}")
        Execute(cmd)

        # Make sure pid directory exist
        # Directory([params.es_master_pid_dir],
        #           mode=0755,
        #           cd_access='a',
        #           owner=params.es_user,
        #           group=params.es_group,
        #           create_parents=True
        #           )

        Execute('echo "Configuration complete"')
        Logger.info( "Configuration complete" )

    def stop(self, env):
        import params
        env.set_params(params)

        # Stop Elasticsearch
        """
            Kill the process by pid file, then check the process is running or not. If the process is still running after the kill
            command, it will try to kill with -9 option (hard kill)
            """
        pid_file = params.kafka_manager_pid_file
        pid = os.popen('cat {pid_file}'.format(pid_file=pid_file)).read()

        process_id_exists_command = format("ls {pid_file} >/dev/null 2>&1 && ps -p {pid} >/dev/null 2>&1")

        kill_cmd = format("kill {pid}")
        Execute(kill_cmd,
                not_if=format("! ({process_id_exists_command})"))
        wait_time = 5

        hard_kill_cmd = format("kill -9 {pid}")
        Execute(hard_kill_cmd,
                not_if=format(
                    "! ({process_id_exists_command}) || ( sleep {wait_time} && ! ({process_id_exists_command}) )"),
                ignore_failures=True)
        try:
            Execute(format("! ({process_id_exists_command})"),
                    tries=20,
                    try_sleep=3,
                    )
        except:
            # show_logs(params.es_master_log_dir, params.es_user)
            raise

        File(pid_file,
             action="delete"
             )

    def start(self, env):
        import params
        env.set_params(params)

        # Configure Elasticsearch
        self.configure(env)

        # Start Cmd:/bin/kafka-manager -Dconfig.file=/data2/kafka-manager-2.0.0.2/conf/application.conf 
        # -Dhttp.port=19090  -Dapplication.home=/data2/kafka-manager/kafka-manager-2.0.0.2
        cmd = format("nohup {kafka_manager_base_dir}/bin/kafka-manager  -Dconfig.file={kafka_manager_conf_dir}/application.conf -Dhttp.port={kafka_manager_http_port} -Dapplication.home={kafka_manager_base_dir} &")
        Logger.info("cmd="+cmd)
        Execute(cmd, user=params.kafka_manager_os_user)

    def status(self, env):
        import status_params
        env.set_params(status_params)

        # Use built-in method to check status using pidfile
        check_process_status(status_params.kafka_manager_pid_file)


if __name__ == "__main__":
    KafkaManagerMaster().execute()