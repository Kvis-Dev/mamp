import subprocess
import os
import shutil

def exec(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return list([l for l in out.decode('utf8').split('\n') if l]), list([l for l in err.decode('utf8').split('\n') if l])


def tpl(tpl_str, dict_of_replacement):
    tpl_str_in = str(tpl_str)
    # print(list(enumerate(dict_of_replacement)))
    for k in dict_of_replacement:
        tpl_str_in = tpl_str_in.replace('[[{}]]'.format(k), dict_of_replacement[k])
    return tpl_str_in


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def ask(question, default=True):
    while True:
        answer = input("{}[{}]\n".format(question.strip(), 'Y/n' if default else 'y/N'))
        if answer.lower() in ['yes', 'y']:
            return True
        elif answer.strip() == '':
            return default
        elif answer.lower() in ['no', 'n']:
            return False
