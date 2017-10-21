import os
from configparser import ConfigParser
from functools import reduce
from itertools import starmap

from cliff.command import Command

CONFIG_DIR_NAME = '.kaggle-cli'
CONFIG_FILE_NAME = 'config'
DATA_OPTIONS = set(['username', 'password', 'competition', 'zip'])


def get_config(config_path):
    if os.path.isfile(config_path):
        config = ConfigParser(allow_no_value=True)
        try:
            config_file = open(config_path)
            config.read_file(config_file)
            return config
        except IOError:
            pass


def get_config_candidates(curdir):
    prevdir = ''
    while curdir != prevdir:
        if curdir != os.path.expanduser('~'):
            config_path = os.path.join(
                curdir, CONFIG_DIR_NAME, CONFIG_FILE_NAME
            )
            config = get_config(config_path)
            if config:
                yield config
        prevdir = curdir
        curdir = os.path.dirname(curdir)  # derive parent dir

    config_path = os.path.join(
        os.path.expanduser('~'), CONFIG_DIR_NAME, CONFIG_FILE_NAME
    )
    config = get_config(config_path)
    if config:
        yield config


def merge_dicts(x, y={}):
    z = x.copy()
    z.update(y)
    return z


def get_working_config(configs):
    return reduce(
        lambda working_config, config:
            merge_dicts(config, working_config),
        map(lambda config: dict(config['user']), configs),
        {}
    )


def get_inline_config(parsed_args):
    parsed_arg_dict = vars(parsed_args)
    return dict(
        (k, parsed_arg_dict[k])
        for k in parsed_arg_dict if parsed_arg_dict[k]
    )


def get_final_config(parsed_args):
    return merge_dicts(
        get_working_config(get_config_candidates(os.getcwd())),
        get_inline_config(parsed_args)
    )


class Config(Command):
    'Set config.'

    def __init__(self, app, app_args, **kargs):
        super(self.__class__, self).__init__(app, app_args, **kargs)

    def get_parser(self, prog_name):
        parser = super(Config, self).get_parser(prog_name)

        parser.add_argument('-u', '--username', help='username')
        parser.add_argument('-p', '--password', help='password')
        parser.add_argument('-c', '--competition', help='competition')
        parser.add_argument('-z', '--zip', help='zip the submission file before uploading?', action='store_true')
        parser.add_argument(
            '-g',
            '--global',
            action='store_true',
            help='is it a global config?'
        )

        return parser

    def take_action(self, parsed_args):
        parsed_arg_dict = vars(parsed_args)

        if DATA_OPTIONS & set(
                filter(lambda x: parsed_arg_dict[x], parsed_arg_dict)
        ):
            if parsed_arg_dict['global']:
                config_dir = os.path.join(
                    os.path.expanduser('~'), CONFIG_DIR_NAME
                )
            else:
                config_dir = os.path.join(os.getcwd(), CONFIG_DIR_NAME)

            if not os.path.isdir(config_dir):
                os.mkdir(config_dir, 0o700)

            config = ConfigParser(allow_no_value=True)
            config_path = os.path.join(config_dir, CONFIG_FILE_NAME)

            if os.path.isfile(config_path):
                with open(config_path, 'r') as config_file:
                    config.read_file(config_file)
            else:
                with open(config_path, 'w') as config_file:
                    os.chmod(config_path, 0o700)

            if not config.has_section('user'):
                config.add_section('user')

            if parsed_arg_dict['username']:
                config.set('user', 'username', parsed_arg_dict['username'])

            if parsed_arg_dict['password']:
                config.set('user', 'password', parsed_arg_dict['password'])

            if parsed_arg_dict['competition']:
                config.set(
                    'user', 'competition',
                    parsed_arg_dict['competition']
                )

            if parsed_arg_dict['zip']:
                config.set('user', 'zip', 'yes')
            else:
                config.set('user', 'zip', 'no')

            with open(config_path, 'w') as config_file:
                config.write(config_file)
        else:
            print('Working config:')
            print(list(starmap(
                lambda k, v: (k, '********') if k == 'password' else (k, v),
                get_working_config(
                    get_config_candidates(os.getcwd())
                ).items())
            ))
