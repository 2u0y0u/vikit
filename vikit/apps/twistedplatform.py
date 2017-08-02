#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Twisted Platform
  Created: 06/23/17
"""

from scouter.sop import FSM
from twisted.internet import reactor

from . import interfaces
from ..core.utils import singleton
from ..core.utils import getuuid

from . import _config
from ..core.platform import vikitplatform
from ..core.launch import twistedlaunch
from ..core.eventemitter import twistedemitter


PlatformConfig = _config.PlatformConfig

#
# define states
#
state_START = 'start'
# listen a address
state_LISTENING = 'listening'
# cannot listen correctly
state_ERROR = 'error'
state_END = 'end'

# start -> listening
action_STARTUP = 'action_startup'
# start -> error
action_STARTUP_ERROR = 'action_startuperror'
# listening -> error
action_RUNTIME_ERROR = 'action_runtimeerror'
# listening -> end
action_SHUTDOWN = 'action_shutdown' # normal user action
# error -> end
action_DIE = 'action_die' # unexpected action


########################################################################
class TwistedPlatform(interfaces.AppInterfaces, singleton.Singleton):
    """"""
    
    _fsm = FSM(state_START, state_END,
              [state_END, state_ERROR, 
               state_LISTENING, state_START])
    
    #
    # define action
    #
    _fsm.create_action(action_STARTUP, state_START, state_LISTENING)
    _fsm.create_action(action_STARTUP_ERROR, state_START, state_ERROR)
    _fsm.create_action(action_RUNTIME_ERROR, state_LISTENING, state_ERROR)
    _fsm.create_action(action_SHUTDOWN, state_LISTENING, state_END)
    _fsm.create_action(action_DIE, state_ERROR, state_END)
    
    
    #
    # private action
    #
    _list_default_service = []
    _dict_pending_actions = {}
    

    #----------------------------------------------------------------------
    def __init__(self, id=None, config=None):
        """Constructor"""
        #
        # basic attrs
        #
        self._id = id if id else getuuid()
        
        self.config = config if config else _config.PlatformConfig
        assert isinstance(config, _config.PlatformConfig)
        
        #
        # build
        #
        self.platform_entity = vikitplatform.VikitPlatform(self.id)
        # set connector
        self.__connector = twistedlaunch.TwistdLauncher(self.entity)
        
        #
        # set platform_emitter and regist neccessary callback
        #
        self.__platform_emitter = twistedemitter.TwistedPlatformEventEmitter(self.__connector)
        self.__platform_emitter.regist_on_service_node_connected(self.on_service_node_connected)
        self.__platform_emitter.regist_on_error_action_happend(self.on_error_action_happend)
        self.__platform_emitter.regist_on_received_success_action(self.on_received_success_action)
        
    
    @property
    def id(self):
        """"""
        return self._id
    
    @property
    def entity(self):
        """"""
        return self.platform_entity
        
    @property
    def state(self):
        """"""
        return self._fsm.state
    
    @_fsm.onstate(state_START)
    def start(self):
        """"""
        try:
            self.__connector.serve(self.config.port, 
                                   self.config.net_if,
                                   self.config.cryptor,
                                   self.config.ack_timeout,
                                   self.config.retry_times)
            self._fsm.action(action_STARTUP)
        except:
            self._fsm.action(action_STARTUP_ERROR)
        
    @_fsm.onstate(state_LISTENING)
    def shutdown(self):
        """"""
        #
        # cleaning resource
        #
        self.__platform_emitter.shutdown()
        self._fsm.action(action_SHUTDOWN)
        
        #
        # end mainloop
        #
        if reactor.running:
            reactor.stop()
        
    def mainloop_start(self):
        """"""
        reactor.run()
        print('[twisted-platform] exit main loop!')
    
    #----------------------------------------------------------------------
    def mainloop_stop(self):
        """"""
        if not reactor.running:
            reactor.stop()
    
    #
    # inspects
    #
    #----------------------------------------------------------------------
    def get_service_nodes(self):
        """"""
        return self.platform_entity._dict_service_node_recorder.keys()
    
    #----------------------------------------------------------------------
    def get_services(self):
        """"""
        #print 'into twistedplatform get_services func'
        #print self.platform_entity._dict_service_infos
        return self.platform_entity._dict_service_infos.keys()
    
    #----------------------------------------------------------------------
    def get_service_nodes_info(self):
        """"""
        return self.platform_entity._dict_service_node_recorder
    
    #----------------------------------------------------------------------
    def get_service_node_info_by_id(self, service_node_id):
        """"""
        return self.platform_entity._dict_service_node_recorder.get(service_node_id)
    
    #----------------------------------------------------------------------
    def get_services_info(self):
        """"""
        return self.platform_entity._dict_service_infos
    
    #----------------------------------------------------------------------
    def get_service_info_by_id(self, service_id):
        """"""
        return self.platform_entity._dict_service_infos.get(service_id)
    
    
        
    
    #
    # active action!
    #
    @_fsm.onstate(state_START, state_LISTENING)
    def add_default_service(self, module_name, port):
        """"""
        #print 'into add'
        self._list_default_service.append((module_name, port))
        #print self._list_default_service
        
    @_fsm.onstate(state_LISTENING)
    def start_service(self, service_node_id, module_name,
                      service_port, service_net_interface=''):
        """"""
        _service_id = getuuid()
        
        config = {"service_node_id":service_node_id,
                  'service_id':_service_id,
                  'module_name':module_name,
                  'launcher_config':{'port':service_port,
                                     'net_if':service_net_interface}}
        
        self.__platform_emitter.start_service(**config)
    
    #
    # passive action (callback)
    #
    def on_service_node_connected(self, service_node_id):
        """"""
        #
        # start default service
        #
        for i in self._list_default_service:
            _module_name = i[0]
            _port = i[1]
            
            self.start_service(service_node_id, module_name=_module_name, 
                               service_port=_port)
    
    #----------------------------------------------------------------------
    def on_error_action_happend(self, action):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def on_received_success_action(self, action):
        """"""
        pass