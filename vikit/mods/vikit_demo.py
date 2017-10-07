#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Mod
  Created: 05/21/17
"""

import time

from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
from vikit.core.basic import target, payload, param


NAME = 'vikit_demo'

AUTHOR = 'vikit'

DESCRIPTION = 'description about a demo'

RESULT_DESC = '''this description is about result!'''

DEMANDS = [TargetDemand('target', target.TYPE_URL),
           PayloadDemand('payload', payload.TYPE_TEXT),
           ParamDemand('param1', param.TYPE_BOOL),
           ParamDemand('param2', param.TYPE_STR)]

#----------------------------------------------------------------------
def test(target, payload, config):
    """"""
    #print('start execute mod: demo')
    time.sleep(3)
    #print('execute successfully!')

    PERSISTENCE_FUNC('target',target)
    print
    print
    print
    print('I HAVE RETURN RESULT')
    print
    print
    print

    return target, payload, config, 'http://villanaadsfch.top'

EXPORT_FUNC = test
