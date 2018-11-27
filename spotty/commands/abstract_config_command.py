from abc import abstractmethod
import yaml
import os
from argparse import Namespace, ArgumentParser
from spotty.config.project_config import ProjectConfig
from spotty.providers.abstract_instance_manager import AbstractInstanceManager
from spotty.providers.instance_manager_factory import InstanceManagerFactory
from yaml.scanner import ScannerError
from spotty.commands.abstract_command import AbstractCommand
from spotty.commands.writers.abstract_output_writrer import AbstractOutputWriter
from spotty.config.validation import validate_basic_config


class AbstractConfigCommand(AbstractCommand):

    @abstractmethod
    def _run(self, instance_manager: AbstractInstanceManager, args: Namespace, output: AbstractOutputWriter):
        raise NotImplementedError

    def configure(self, parser: ArgumentParser):
        super().configure(parser)
        parser.add_argument('-c', '--config', type=str, default=None, help='Path to the configuration file')
        parser.add_argument('instance_name', metavar='INSTANCE_NAME', nargs='?', type=str, help='Instance name')

    def run(self, args: Namespace, output: AbstractOutputWriter):
        # get project directory
        config_path = args.config
        if not config_path:
            config_path = 'spotty.yaml'

        if os.path.isabs(config_path):
            config_abs_path = config_path
        else:
            config_abs_path = os.path.abspath(os.path.join(os.getcwd(), config_path))

        if not os.path.exists(config_abs_path):
            raise ValueError('Configuration file "%s" not found.' % config_path)

        project_dir = os.path.dirname(config_abs_path)
        project_config = ProjectConfig(self._load_config(config_abs_path), project_dir)
        instance_config = project_config.get_instance_config(args.instance_name)
        instance_manager = InstanceManagerFactory.get_instance(instance_config, project_config)

        # run the command
        self._run(instance_manager, args, output)

    @staticmethod
    def _load_config(config_path: str):
        """Returns project configuration."""
        config = None
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                try:
                    config = yaml.load(f)
                except ScannerError as e:
                    raise ValueError(str(e))

        return config
