#!/usr/bin/env python
# coding:utf-8
"""
  Author:  Conan0xff
  Purpose: Platform Trigger
  Created: 07/29/17
"""

import sys
import os
import time
import signal

from multiprocessing import Pipe, Process
from threading import Thread
from twisted.internet import reactor

from .. import platform
from . import _base

action_start = 'start'
action_shutdown = 'shutdown'
action_add_default_service = 'add_default_service'
action_get_available_service_nodes = 'get_available_service_nodes'
action_get_service_nodes_info = 'get_available_service_nodes_info'
action_get_available_services = 'get_available_services'
action_get_available_services_info = 'get_available_services_info'
action_get_service_node_info_by_id='get_service_node_info_by_id'
action_get_service_info_by_id='get_service_info_by_id'
action_state = 'state'


def get_platform_proxy(platform_port, id=None, **config):
    p1, p2 = Pipe()
    rp1, rp2 = Pipe()

    trigger = PlatformTrigger(p2, rp1, platform_port, id, **config)

    #
    # prepare process and set daemon
    #
    trigger_process = Process(target=trigger.start)
    trigger_process.daemon = True
    trigger_process.start()

    return PlatformProxy(p1, rp2, trigger_process)


class PlatformProxy(_base.ProxyBase):

    def __init__(self, pipe, result_pipe, process):
        """Constructor"""

        self._pipe = pipe
        self._process = process

        self._result_pipe = result_pipe

        self._list_result_callbacks = []

        #
        # start the 
        #
        self._thread_receive_result = Thread(target=self._receiving_result,
                                             name='receiving-result')
        self._thread_receive_result.daemon = True
        self._thread_receive_result.start()

        self._count_of_extra_data = 0

    def _send(self, data):
        """"""
        self._pipe.send(data)

    def _receiving_result(self):
        """"""
        while True:
            if self._result_pipe.poll():
                data = self._result_pipe.recv()
                self.on_result_received(data)

    def on_result_received(self, result_dict):
        """"""
        for i in self._list_result_callbacks:
            result_dict = i(result_dict)

    def add_default_service(self, module_name, port):
        func = action_add_default_service
        _params = {
            'module_name': module_name,
            'port': port
        }
        data = (func, _params)
        self._send(data)
        return self._receive_data()

    def get_available_service_nodes(self):
        func = action_get_available_service_nodes
        _params = {
        }
        data = (func, _params)
        self._send(data)
        return self._receive_data()

    def get_service_node_info_by_id(self,service_node_id):
        func = action_get_service_node_info_by_id
        _params = {
            'service_node_id':service_node_id
        }
        data = (func, _params)
        self._send(data)
        return self._receive_data()


    def get_available_services(self):
        func =action_get_available_services
        _params = {
        }
        data = (func, _params)
        self._send(data)
        return self._receive_data()

    def get_service_info_by_id(self,service_id):
        func =action_get_service_info_by_id
        _params = {
            'service_id':service_id
        }
        data = (func, _params)
        self._send(data)
        return self._receive_data()

    def get_available_services_info(self):
        func = action_get_available_services_info
        _params = {
        }
        data = (func, _params)
        self._send(data)
        return self._receive_data()

    def get_service_nodes_info(self):
        func =action_get_service_nodes_info
        _params = {
        }
        data = (func, _params)
        self._send(data)
        return self._receive_data()

    def shutdown(self):
        """"""
        func = action_shutdown
        params = {}

        data = (func, params)

        self._send(data)

        _ret = self._receive_data()

        try:
            pid = self._process.pid
            os.kill(pid, signal.SIGKILL)
        except:
            pass

        return _ret

    @property
    def state(self):
        """"""
        func = action_state
        params = {}

        data = (func, params)

        self._send(data)

        return self._receive_data()

    def _receive_data(self, timeout=3, default=None):
        """"""
        _future = int(time.time()) + 3
        while _future > int(time.time()):
            if self._pipe.poll():
                _ret = self._pipe.recv()
                if self._count_of_extra_data == 0:
                    return _ret
                else:
                    self._count_of_extra_data = self._count_of_extra_data - 1

        self._count_of_extra_data = self._count_of_extra_data + 1
        return default

    def regist_result_callback(self, callback):
        """"""
        assert callable(callback)

        self._list_result_callbacks.append(callback)


class PlatformTrigger(_base.Trigger):
    def __init__(self, pipe, result_pipe, platform_port,
                 id=None, **config):
        """Constructor"""
        self.platform_port = platform_port
        self.id = id
        self.config = config

        self._pipe = pipe
        self._result_pipe = result_pipe

    def _recieving(self):
        """"""
        while True:
            if self._pipe.poll():
                data = self._pipe.recv()
                self._pipe.send(self.on_data_received(data))

    def on_data_received(self, data):
        """"""
        func = data[0]
        params = data[1]
        if func == action_add_default_service:
            return platform.add_default_service(**params)
        elif func == action_get_available_service_nodes:
            return platform.get_available_service_nodes()
        elif func == action_get_available_services:
            return platform.get_available_services()
        elif func == action_get_service_nodes_info:
            return platform.get_service_nodes_info()
        elif func == action_get_available_services_info:
            return platform.get_services_info()
        elif func == action_get_service_node_info_by_id:
            return platform.get_service_node_info_by_id(**params)
        elif func == action_get_service_info_by_id:
            return platform.get_service_info_by_id(**params)
        elif func == action_shutdown:
            try:
                return None #platform.shutdown()
            except:
                return None

    def on_result_received(self, result_dict):
        print('[trigger] result is send back')
        self._result_pipe.send(result_dict)

    def start(self):
        platform.twisted_start_platform(self.platform_port,
                                    async=True,
                                    **self.config)

        #platform.regist_common_result_callback(self.on_result_received)

        #
        # prepare receiving data
        #
        platform.call_in_thread(self._recieving)

        platform.mainloop_start()
