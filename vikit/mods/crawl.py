#!/usr/bin/env python
#coding:utf-8
"""
  Author:   Conan
  Purpose: Crawl
  Created: 07/20/17
"""

import time

from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
from vikit.core.basic import target, payload, param
from vikit.mod_tools.crawler.site_crawler import Crawler

NAME = 'crawl'

AUTHOR = 'Conan'

DESCRIPTION = 'crawl a site'

RESULT_DESC = '''return depth and urls'''

DEMANDS = [TargetDemand('target', target.TYPE_URL),
           PayloadDemand('payload', payload.TYPE_TEXT),
           ParamDemand('param1', param.TYPE_BOOL),
           ParamDemand('param2', param.TYPE_STR)]

#----------------------------------------------------------------------
def test(target, payload, config):
    """"""
    crawler=Crawler(start_url=target,mode='process',thread_max=5)
    result_queue=crawler.async_run(depth=2) 
    result_ret=''
    while True:
        try:
            result = result_queue.get(timeout=40)
        except:
            break
        if result['tag'] == 'current_depth_result':
            pass
        if result['tag'] == 'final_result':
            result_ret=str(result['url_table'])

    PERSISTENCE_FUNC('target',target)
    print
    print
    print
    print('I HAVE RETURN RESULT')
    print
    print
    print
    return result_ret


EXPORT_FUNC = test
