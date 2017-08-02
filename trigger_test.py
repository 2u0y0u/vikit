#!/usr/bin/env python
# coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: 
  Created: 07/02/17
"""
import time

import unittest
from vikit.api.trigger import get_client_proxy, get_platform_proxy
from vikit.api.client import state_CONNECTED
from vikit.api.servicenode import start_servicenode

# triger platform test
def print_service_and_node(result_dict):
    print('[triger]: got service and service_node:')
    print result_dict
    return result_dict


ptriger = get_platform_proxy(7000)
# ptriger.regist_result_callback(print_service_and_node)
#start_servicenode()
print ptriger.add_default_service('demo', 7001)
#whn servicenode connect to platform it will be available
service_nodes = ptriger.get_available_service_nodes()
print service_nodes
services = ptriger.get_available_services()
print services
service_nodes_info = ptriger.get_service_nodes_info()
print service_nodes_info
service_info = ptriger.get_services_info()
print service_info
ptriger.shutdown()

# triger client test
# ----------------------------------------------------------------------
def print_task_id(result_dict):
    """"""
    print('[trigger]: got a task! ID:{}'.format(result_dict.get('task_id')))
    return result_dict


ctrigger = get_client_proxy(platform_host='39.108.169.134', platform_port=7000,
                            id=None)
ctrigger.regist_result_callback(print_task_id)

while not ctrigger.state == state_CONNECTED:
    pass

modules = ctrigger.get_available_modules()
print(ctrigger.get_help_for_module('demo'))

print('submit task')
ctrigger.execute('demo', {"target": 'http://tbis.me',
                          'payload': 'adfa',
                          'config': {'param1': True,
                                     'param2': 'asdfasd'}},
                 offline=True)

ctrigger.execute('demo', {"target": 'http://tbis.me',
                          'payload': 'adfa',
                          'config': {'param1': True,
                                     'param2': 'asdfasd'}},
                 True)

print('submit task success')

print('sleeping 10 seconds')
time.sleep(10)
ctrigger.shutdown()
exit()
