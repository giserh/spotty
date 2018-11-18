from argparse import ArgumentParser, Namespace
import subprocess
from spotty.commands.abstract_config_command import AbstractConfigCommand
from spotty.helpers.config import get_instance_config
from spotty.commands.writers.abstract_output_writrer import AbstractOutputWriter
from spotty.providers.instance_factory import InstanceFactory


class SshCommand(AbstractConfigCommand):

    name = 'ssh'
    description = 'Connect to the running Docker container or to the instance itself'

    def configure(self, parser: ArgumentParser):
        super().configure(parser)
        parser.add_argument('-H', '--host-os', action='store_true', help='Connect to the host OS instead of the Docker '
                                                                         'container')
        parser.add_argument('-s', '--session-name', type=str, default=None, help='tmux session name')

    def _run(self, project_dir: str, config: dict, args: Namespace, output: AbstractOutputWriter):
        project_name = config['project']['name']
        instance_config = get_instance_config(config['instances'], args.instance_name)

        instance = InstanceFactory.get_instance(project_name, instance_config)

        # connect to the instance
        host = '%s@%s' % (instance.ssh_user, instance.ip_address)
        ssh_command = ['ssh', '-i', instance.ssh_key_path, '-o', 'StrictHostKeyChecking no', '-t', host]

        if args.host_os:
            # connect to the host OS
            session_name = args.session_name if args.session_name else 'spotty-ssh-host-os'
            remote_cmd = ['tmux', 'new', '-s', session_name, '-A']
        else:
            # connect to the container
            session_name = args.session_name if args.session_name else 'spotty-ssh-container'
            remote_cmd = ['tmux', 'new', '-s', session_name, '-A', 'sudo', '/scripts/container_bash.sh']

        remote_cmd = subprocess.list2cmdline(remote_cmd)

        # connect to the instance
        ssh_command = get_ssh_command(project_name, region, ip_address, remote_cmd, local_ssh_port)
        subprocess.call(ssh_command)
