#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Client Trigger
  Created: 07/02/17
"""

import sys
import os
import time
import signal

from multiprocessing import Pipe, Process
from threading import Thread
from twisted.internet import reactor

from .. import client
from . import _base

action_get_help_for = 'get_help_for'
action_get_modules = 'get_modules'
action_execute = 'execute'
action_state = 'state'
action_shutdown = 'shutdown'


    
#----------------------------------------------------------------------
def get_client_proxy(platform_host, platform_port, id=None, **config):
    """"""
    p1, p2 = Pipe()
    rp1, rp2 = Pipe()
    
    trigger = ClientTrigger(p2, rp1, platform_host, platform_port, id, **config)
    
    #
    # prepare process and set daemon
    #
    trigger_process = Process(target=trigger.start)
    trigger_process.daemon = True
    trigger_process.start()
    
    return ClientProxy(p1, rp2, trigger_process)
    

########################################################################
class ClientProxy(_base.ProxyBase):
    """"""

    #---------------------------------------------------------------------
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
        
    #----------------------------------------------------------------------
    def _send(self, data):
        """"""
        self._pipe.send(data)
        
    #----------------------------------------------------------------------
    def _receiving_result(self):
        """"""
        while True:
            if self._result_pipe.poll():
                data = self._result_pipe.recv()
                self.on_result_received(data)
    
    #----------------------------------------------------------------------
    def on_result_received(self, result_dict):
        """"""
        for i in self._list_result_callbacks:
            result_dict = i(result_dict)
    
    #----------------------------------------------------------------------
    def execute(self, module_name, params, offline=False, task_id=None):
        """"""
        func = action_execute
        _params = {'module_name':module_name,
                  'params':params,
                  'offline':offline,
                  'task_id':task_id}
        
        data = (func, _params)
        
        self._send(data)
        
        return self._receive_data()
        
    #----------------------------------------------------------------------
    def get_available_modules(self):
        """"""
        func = action_get_modules
        params = {}
        
        data = (func, params)
        
        self._send(data)
        
        return self._receive_data()
        
    #----------------------------------------------------------------------
    def get_help_for_module(self, module_name):
        """"""
        func = action_get_help_for
        params = {'module_name':module_name}
        
        data = (func, params)
        
        self._send(data)
        
        return self._receive_data()
    
    #----------------------------------------------------------------------
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
        
    #----------------------------------------------------------------------
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
    
    #----------------------------------------------------------------------
    def regist_result_callback(self, callback):
        """"""
        assert callable(callback)
        
        self._list_result_callbacks.append(callback)


########################################################################
class ClientTrigger(_base.Trigger):
    """"""

    #---------------------------------------------------------------------
    def __init__(self, pipe, result_pipe, platform_host, platform_port, 
                 id=None, **config):
        """Constructor"""
        self.platform_host = platform_host
        self.platform_port = platform_port
        self.id = id
        self.config = config
        
        self._pipe = pipe
        self._result_pipe = result_pipe
    
    #----------------------------------------------------------------------
    def _recieving(self):
        """"""
        while True:
            if self._pipe.poll():
                data = self._pipe.recv()
                self._pipe.send(self.on_data_received(data))
    
    #----------------------------------------------------------------------
    def on_data_received(self, data):
        """"""
        func = data[0]
        params = data[1]
        if func == action_execute:
            return client.execute(**params)
        elif func == action_get_help_for:
            return client.get_help_for_module(**params)
        elif func == action_get_modules:
            return client.get_available_modules()
        elif func == action_state:
            return client.get_state()
        elif func == action_shutdown:
            try:
                return client.shutdown()
            except:
                return None
    
    #----------------------------------------------------------------------
    def on_result_received(self, result_dict):
        """"""
        print('[trigger] result is send back')
        self._result_pipe.send(result_dict)
    
    #----------------------------------------------------------------------
    def start(self):
        """"""
        
        client.twisted_start_client(self.platform_host,
                                    self.platform_port,
                                    async=True,
                                    id=self.id,
                                    update_client_state=True,
                                    **self.config)
        
        client.regist_common_result_callback(self.on_result_received)

        #
        # prepare receiving data
        #
        client.call_in_thread(self._recieving)
        
        client.mainloop_start()
        
        