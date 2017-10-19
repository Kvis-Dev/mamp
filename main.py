import sys, os
import argparse
import shutil
import getpass
import re
import argparse

from common.config import ROOT, HOME, USER, SERVER_ROOT
from common.libs import STATUS_NOT_RUNNING, STATUS_BAD_RUNNING, STATUS_OK, Php70, Nginx, Mysql, ExternalServicePhp
from helpers import exec, tpl, copytree, ask
from distutils.dir_util import copy_tree

import color_print
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('action', help='action to run. Can be one of: [status]')

SERVICES = [Nginx(), Php70(), Mysql()]


def create_paths():
    for s in SERVICES:
        s.create_paths()
        s.copy_configs()

def check_installs():
    if not os.geteuid() == 0:
        print("need sudo to run this script, please, rerun with:\nsudo python3 {}".format(sys.argv[0]))
        sys.exit(1)

    checks, _ = exec("which brew".format(USER))
    if len(checks) == 0:
        print('Can not proceed without brew, visit https://brew.sh/ to install brew')
        sys.exit(2)

    checks, _ = exec("sudo -u {} brew list".format(USER))

    if 'nginx' not in checks:
        print('Can not proceed without nginx, run:\nbrew install nginx')
        sys.exit(3)

    if 'php70' not in checks:
        print('Can not proceed without php70, run:\nbrew install php70')
        sys.exit(3)


def status():

    for s in SERVICES:
        status_service = s.status()

        if status_service == STATUS_OK:
            color_print.green('{}  OK'.format(str(s)))
        if status_service == STATUS_BAD_RUNNING:
            color_print.orange('{} started with wrong config'.format(str(s)))
        if status_service == STATUS_NOT_RUNNING:
            color_print.red('{} not running'.format(str(s)))

def start():
    for s in SERVICES:
        status_service = s.status()
        if status_service == STATUS_BAD_RUNNING:
            color_print.blue('Service {} started from wrong config, restarting'.format(str(s)))
            s.stop()
            s.start()
        if status_service == STATUS_NOT_RUNNING:
            color_print.blue('Starting {}'.format(str(s)))
            s.start()

def stop():
    for s in SERVICES:
        status_service = s.status()
        if status_service == STATUS_OK:
            color_print.blue('Stopping {}'.format(str(s)))
            s.stop()
        if status_service == STATUS_BAD_RUNNING:
            color_print.blue('Service {} started from wrong config, stopping'.format(str(s)))
            s.stop()
            s.start()


def wizard():
    print("This wizard created to help you create config for your website in under a minute")
    print("Please, be patient")

    php_ver = []
    for s in SERVICES:
        if isinstance(s, ExternalServicePhp):
            php_ver.append(s.get_version())
    # print(php_ver)

    while True:
        server_name = input("Server name (e.g. facebook.local):\n")
        re_res = re.match("^(([a-z0-9]\-*[a-z0-9]*){1,63}\.?){1,255}$", server_name)
        print(re_res)
        if re_res:
            print('Ok')
            break
        else:
            print('This server name seems bad')

    while True:
        docroot = input("Website root (e.g. ~/www/facebook-src):\n")

        fullpath = os.path.expanduser(docroot)

        if not os.path.isdir(fullpath):
            print("WARNING!!!\n\nPath {} is not a directory!")

            if not ask('Try again?'):
                break
        else:
            break

    while True:
        php_version = input("PHP version:\nAvailable versions:{}\n".format(', '.join(php_ver)))
        if php_version in php_ver:
            break
    php_port = php_version.replace('.', '')

    template = """
server {{ 
    listen 80;
    server_name {server_name};
    set $domain_path "{docroot}";
    root $domain_path;
    index index.php index.html index.htm;
    location / {{
        try_files $uri $uri/ /index.php$is_args$args;
    }}
    location ~ \.php$ {{
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $domain_path$fastcgi_script_name;
        fastcgi_pass 127.0.0.1:90{port};
        try_files $uri =404;
        fastcgi_read_timeout 300;
    }}
}}""".format(server_name=server_name, docroot=fullpath, port=php_port)
    print("\n\n\n", template, "\n\n\n")
    if ask("Is this a correct config?"):
        fin_file = "{}/etc/nginx/sites-enabled/{}".format(SERVER_ROOT,server_name)
        if os.path.exists(fin_file):
            i = 1
            while not os.path.exists("{}_{}".format(fin_file, i)):
                i += 1
            fin_file = "{}/etc/nginx/sites-enabled/{}_{}".format(SERVER_ROOT,server_name,i)

        with open(fin_file, 'w') as f:
            f.write(template)

        print("You might want to restart server")

if __name__ =='__main__':
    check_installs()
    create_paths()

    arguments = parser.parse_args()

    if arguments.action == 'status':
        status()

    if arguments.action == 'start':
        start()

    if arguments.action == 'restart':
        stop()
        print()
        start()

    if arguments.action == 'stop':
        stop()

    if arguments.action == 'wizard':
        wizard()