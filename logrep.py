import argparse
import sys
from fabric.api import settings, run

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


class InvalidConfig(Exception):
    pass


def readconf():
    config = ConfigParser()
    config.read('config.ini')
    servers = []
    for section in config.sections():
        server = {}
        try:
            server['host'] = section
            server['user'] = config[section]['user']
            server['key_filename'] = config[section]['key_filename']
        except KeyError:
            raise InvalidConfig()
        servers.append(server)
    return servers


def get_logs(pattern, files):
    # Get servers list from config file
    try:
        servers = readconf()
    except InvalidConfig:
        return 'Invalid configuration'

    # Start running input command on logs over ssh
    logs = []
    for server in servers:
        with settings(hosts_string=server['host'], 
                      user=server['user'], 
                      key_filename=server['key_filename']):
            command = "grep '{pattern}' {files}" % {'pattern':pattern, 'files':files}
            log = run(command)
            logs.append(log)
    
    return ("\n").join(logs)

        
def get_parser():
    parser = argparse.ArgumentParser(
        description='aggregate logs from multiple servers')
    parser.add_argument('pattern', metavar='PATTERN', type=str,
                        help='Pattern to search for')
    parser.add_argument('files', metavar='FILES', type=str,
                        help='list of files to search separated by whitespace')
    return parser


def main():
    parser = get_parser()
    args = vars(parser.parse_args())
    pattern = args['pattern']
    files = args['files']

    if sys.version < '3':
        print(get_logs(pattern, files).encode('uts-8', 'ignore'))
    else:
        print(get_logs(pattern, files))


if __name__ == '__main__':
    main()
