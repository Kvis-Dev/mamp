import os
import re

from helpers import exec, tpl
from common.config import SERVER_ROOT, ROOT
from distutils.dir_util import copy_tree


STATUS_OK = 2
STATUS_NOT_RUNNING = 1
STATUS_BAD_RUNNING = 3

class ExternalService:
    def status(self): raise NotImplementedError
    def start(self): raise NotImplementedError
    def stop(self): raise NotImplementedError
    def copy_configs(self): raise NotImplementedError
    def get_is_installed(self): raise NotImplementedError
    def create_paths(self): raise NotImplementedError


class ExternalServicePhp(ExternalService):
    def get_version(self):
        raise NotImplementedError


class ExternalServiceWebserver(ExternalService):
    def get_version(self):
        raise NotImplementedError


class Apache2(ExternalServiceWebserver):
    def __str__(self):
        return 'apache2'

    def status(self):
        status, _= exec('sudo pgrep -lf apache2')

        for l in status:
            if 'httpd -k start' in l:
                return STATUS_OK

    def start(self):
        exec("sudo apachectl start -f /usr/local/apache2/conf/httpd.conf")

    def stop(self):
        exec("sudo apachectl stop")


    def copy_configs(self):
        pass


    def get_is_installed(self):
        out, _ = exec('readlink `which apachectl`')

    def create_paths(self):
        pass


class Nginx(ExternalServiceWebserver):
    def __str__(self):
        return 'nginx'

    def copy_configs(self):
        copy_tree("{}/configs/nginx".format(ROOT), "{}/etc/nginx".format(SERVER_ROOT))


    def create_paths(self):
        paths = ('etc/nginx/sites-enabled', 'etc/nginx/sites-available')

        for p in paths:
            if not os.path.isdir(os.path.join(SERVER_ROOT, p)):
                os.makedirs(os.path.join(SERVER_ROOT, p))
            os.chmod(os.path.join(SERVER_ROOT, p), 0o777)

    def stop(self):
        exec('sudo nginx -s stop; sudo killall nginx')

    def start(self):
        nginx_start_cmd = "sudo nginx -c {}/etc/nginx/nginx.conf".format(SERVER_ROOT)
        self.append_etc_hosts()
        exec(nginx_start_cmd)

    def status(self):
        out, err = exec("sudo pgrep -lf nginx")
        # print(out, err)
        if len(out) == 0:
            return STATUS_NOT_RUNNING
        for l in out:
            if "{}/etc/nginx/nginx.conf".format(SERVER_ROOT) in l:
                return STATUS_OK

        return STATUS_BAD_RUNNING

    def append_etc_hosts(self):
        s_names = set()
        for root, dirs, files in os.walk("{}/etc/nginx/sites-enabled".format(SERVER_ROOT), topdown=False):
            for name in files:
                try:
                    with open(os.path.join(root, name), 'r') as f:
                        lines = [l.strip() for l in f.read().split(';')]
                        for line in lines:
                            if line.startswith('server_name'):
                                for s in line[11:].split(' '):
                                    s_names.add(s)

                except UnicodeDecodeError as e:
                    pass

        server_names = {s for s in s_names if s}

        hosts = set()
        with open('/etc/hosts', 'r') as f:
            for line in f.readlines():
                before_sh = line.strip().split('#')[0]
                host = list(filter(len, re.split(r"\s", before_sh)))
                if len(host) == 2:
                    hosts.add(host[1])

        to_add = server_names - hosts

        with open('/etc/hosts', 'a') as f:
            for line in to_add:
                f.write("\n127.0.0.1 {}".format(line))


class Php70(ExternalServicePhp):
    def __str__(self):
        return 'php 7.0'
        
    def get_version(self):
        return '7.0'

    def create_paths(self):
        paths = ('etc/php/7.0/fpm', )

        for p in paths:
            if not os.path.isdir(os.path.join(SERVER_ROOT, p)):
                os.makedirs(os.path.join(SERVER_ROOT, p))
            os.chmod(os.path.join(SERVER_ROOT, p), 0o777)

    def copy_configs(self):
        copy_tree("{}/configs/php".format(ROOT), "{}/etc/php".format(SERVER_ROOT))

        for root, dirs, files in os.walk("{}/etc/php".format(SERVER_ROOT), topdown=False):
            for name in files:
                try:
                    with open(os.path.join(root, name), 'r+') as f:
                        cont = f.read()

                        f.seek(0)
                        f.write(tpl(cont, {"SERVER_ROOT": SERVER_ROOT}))
                        f.truncate()
                except UnicodeDecodeError as e:
                    pass

    def status(self):
        out, err = exec("sudo pgrep -lf php-fpm")
        ok_line = "php-fpm -y {}/etc/php/7.0/php-fpm.conf -c {}/etc/php/7.0/php.ini".format(SERVER_ROOT,SERVER_ROOT)

        if len(out) == 0:
            return STATUS_NOT_RUNNING
        for l in out:
            if ok_line in l:
                return STATUS_OK

        return STATUS_BAD_RUNNING

    def start(self):
        php_70_start_command = "sudo /usr/local/opt/php70/sbin/php-fpm -y {}/etc/php/7.0/php-fpm.conf -c {}/etc/php/7.0/php.ini".format(SERVER_ROOT, SERVER_ROOT)
        exec(php_70_start_command)

    def stop(self):
        exec('sudo killall php-fpm')

    def get_is_installed(self): 
        return True  # TODO: rewrite


class Mysql(ExternalService):
    def __str__(self):
        return 'mysql'

    def status(self):
        o, _ = exec('sudo brew services list')
        
        for l in o:
            if 'mysql' in l:
                if 'started' in l:
                    return STATUS_OK
                else:
                    return STATUS_NOT_RUNNING

        return STATUS_NOT_RUNNING

    def start(self):
        exec('sudo brew services start mysql')

    def stop(self):
        exec('sudo brew services stop mysql')

    def copy_configs(self): pass
    def get_is_installed(self): return True
    def create_paths(self): pass



