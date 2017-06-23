#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Twisted Emitter
  Created: 06/17/17
"""

from twisted.internet import task, reactor

from . import emitterbase
from ..platform import vikitplatform
from ..servicenode import vikitservicenode, vikitservice
from ..vikitclient import vikitclient, vikitagentpool
from ..launch.twistedlaunch import TwistdLauncher
from ..launch import twistedbase
from ..actions import servicenode_actions, heartbeat_action, task_action

########################################################################
class TwistedPlatformEventEmitter(emitterbase.EmitterBase):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, launcher):
        """Constructor"""
        emitterbase.EmitterBase.__init__(self, launcher)
        
        self.platform = self.launcher.entity
        assert isinstance(self.platform, vikitplatform.VikitPlatform)
    
    #
    # stop / start service
    #
    #----------------------------------------------------------------------
    def start_service(self, service_node_id, service_id,
                      module_name, launcher_config):
        """"""
        assert self.launcher.entity.has_service_node(service_node_id)
        
        #
        # build action
        #
        _start_service_action = servicenode_actions.StartServiceAction(service_id=service_id,
                                                                       module_name=module_name,
                                                                       launcher_type=TwistdLauncher,
                                                                       launcher_config=launcher_config)
        
        #
        # get conn
        #
        _conn = self.platform.get_sender(service_node_id)
        assert isinstance(_conn, twistedbase.VikitTwistedProtocol)
        
        #
        # send it
        #
        _conn.send(_start_service_action)
    
    #----------------------------------------------------------------------
    def stop_service(self, service_id):
        """"""
        
        #
        # build action
        #
        _stop_service_action = servicenode_actions.StopServiceAction(
                                                                    service_id)
        
        #
        # get conn
        #
        _infos = self.platform.get_service_info()
        #print _infos
        if _infos.has_key(service_id):
            _serviceinfos = _infos.get(service_id)
            node_id = _serviceinfos.get('service_node_id')
            if node_id:
                _conn = self.platform.get_sender(node_id)
                _conn.send(_stop_service_action)
            else:
                print('[platform] no such service node id for service_id:{}.'.format(service_id))
        else:
            print('[platform] no such service id:{}'.format(service_id))
    
    #----------------------------------------------------------------------
    def get_service_info(self):
        """"""
        return self.platform.get_service_info()
    
    #----------------------------------------------------------------------
    def shutdown(self):
        """"""
        #
        # shutdown socket
        #
        self.launcher.connector.stopListening()
        
        #
        # shutdown reactor
        #
        reactor.stop()
        
        
        #self.launcher.connector.shutdown()
    
    #----------------------------------------------------------------------
    def regist_on_service_node_connected(self, callback):
        """"""
        assert callable(callback)
        
        self.platform.regist_on_service_node_connected(callback)
    
    #----------------------------------------------------------------------
    def regist_on_error_action_happend(self, callback):
        """"""
        assert callable(callback)
        
        self.platform.regist_on_error_action_happend(callback)

########################################################################
class TwistedServiceNodeEventEmitter(emitterbase.EmitterBase):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, connector):
        """Constructor"""
        emitterbase.EmitterBase.__init__(self, connector)
        
        self.servicenode = connector.entity
        assert isinstance(self.servicenode, vikitservicenode.VikitServiceNode) 
        
        self._loopingcall_heartbeat = task.LoopingCall(self._send_heartbeat)
        
        #
        # auto regist
        #
        self._regist_start_heartbeat_callback()
        self._regist_stop_heartbeat_callback()
        
    
    #----------------------------------------------------------------------
    def _regist_start_heartbeat_callback(self):
        """"""
        self.servicenode.regist_start_heartbeat_callback(self._start_heartbeat)
        return
    
    #----------------------------------------------------------------------
    def _regist_stop_heartbeat_callback(self):
        """"""
        self.servicenode.regist_stop_heartbeat_callback(self._stop_heartbeat)
    
    #----------------------------------------------------------------------
    def _start_heartbeat(self, interval):
        """"""
        if self._loopingcall_heartbeat.running:
            self._loopingcall_heartbeat.stop()
            self._loopingcall_heartbeat.start(interval, True)
        else:
            self._loopingcall_heartbeat.start(interval, True)
    
        return 
    
    #----------------------------------------------------------------------
    def _stop_heartbeat(self):
        """"""
        if self._loopingcall_heartbeat.running:
            self._loopingcall_heartbeat.stop()
            
        return
        
    
    #----------------------------------------------------------------------
    def _send_heartbeat(self):
        """"""
        #print('[>>>>>>>>>>>>>>>>] hb')
        self.servicenode._send_heartbeat()
    
    #----------------------------------------------------------------------
    def shutdown(self):
        """"""
        self.launcher.connector.disconnect()
        #self.launcher.connector.stop()
        reactor.stop()
        

########################################################################
class TwistedClientEventEmitter(emitterbase.EmitterBase):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, connector):
        """Constructor"""
        emitterbase.EmitterBase.__init__(self, connector)
        
        #assert isinstance(self.launcher.entity, vikitclient.VikitClient)
        self.client = connector.entity
        assert isinstance(self.client, vikitclient.VikitClient)
        
        self.client.regist_execute_callback(self._send_executeaction)
    

    
    #----------------------------------------------------------------------
    def execute(self, task_id, params):
        """"""
        self.client.execute_task(task_id, params)
        
    #----------------------------------------------------------------------
    def _send_executeaction(self, task_id, params):
        """"""
        #conn = self.get_sender()
        
        #
        # build execute action
        #
        taskaction = task_action.VikitExecuteTaskAction(task_id, params)
        
        conn = self.client.get_sender(self.client.service_id)
        conn.send(taskaction)
        
        return task_id, params
        
    

########################################################################
class TwistedServiceEventEmitter(emitterbase.EmitterBase):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, connector):
        """Constructor"""
        emitterbase.EmitterBase.__init__(self, connector)
        
        self.service = connector.entity
        assert isinstance(self.service, vikitservice.VikitService)
        
        self.service.regist_result_callback(callback)
        
########################################################################
class TwistdClientAgentPoolEmitter(emitterbase.EmitterBase):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, connector, default_update_interval=10):
        """Constructor"""
        emitterbase.EmitterBase.__init__(self, connector)
        
        self.agentpool = connector.entity
        assert isinstance(self.agentpool, vikitagentpool.VikitClientAgentPool)
        
        #
        # update services loopingcall setting
        #
        self._loopingcall_start_update_services = \
            task.LoopingCall(self.agentpool.update_services_list)
        
        self._interval = default_update_interval
        
    
    #----------------------------------------------------------------------
    def get_service(self):
        """"""
        return self.agentpool.get_service()

    #----------------------------------------------------------------------
    def start_update_services(self, interval=None):
        """"""
        if self._loopingcall_start_update_services.running:
            if interval == self._interval:
                self._loopingcall_start_update_services.stop()
                self._loopingcall_start_update_services.start(self._interval)
        else:
            if interval:
                self._loopingcall_start_update_services.start(interval)
            else:
                self._loopingcall_start_update_services.start(self._interval)
        
        
    #----------------------------------------------------------------------
    def execute(self, module_name, task_id, params, service_id=None):
        """"""
        return self.agentpool.execute(module_name, task_id, params, service_id)
        
    
        
    
    
        
        
        
    
    