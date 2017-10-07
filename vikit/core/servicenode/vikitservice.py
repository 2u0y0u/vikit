#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Vikit Service
  Created: 06/16/17
"""

import os
import types

from ..basic import result
from ..basic import mod
from ..basic import vikitbase
from ..vikitdatas import vikitservicedesc
from ..actions import welcome_action, task_action

##
## define state
##
#state_START = 'start'

## action: start_error INITING->ERROR
## action: runtime_error WORKING->ERROR
#state_ERROR = 'error'

## action: start START->INITING
#state_INITING = 'initing'

## action: start_finish INITING->WORKING
#state_WORKING = 'working'

## action finish WORKING->END
## action error_to_die ERROR->END
#state_END = 'end'

#_all_states = [state_END, 
               #state_ERROR,
               #state_INITING,
               #state_START,
               #state_WORKING]

#
# task_state
#
task_RUNNING = 'pending'
task_FINISHED = 'finished'


_CURRENT_PATH_ = os.path.dirname(__file__)
_CURRENT_MODS_PATH_ = os.path.join(_CURRENT_PATH_, '../../mods/')

########################################################################
class VikitServiceConfig(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, min_threads=5, max_threads=20, debug=False,
                 loop_interval=0.2, adjust_interval=3, diviation_ms=100,
                 default_mod_paths=[_CURRENT_MODS_PATH_,]):
        """Constructor"""

        #
        # set mod/factory attrs
        #
        self.min_threads = min_threads
        self.max_threads = max_threads
        self.debug = debug
        self.loop_interval = loop_interval
        self.adjust_interval = adjust_interval
        self.diviation_ms = diviation_ms

        #
        # paths
        # 
        assert isinstance(default_mod_paths, (list, tuple))
        self.default_mod_paths = default_mod_paths


########################################################################
class VikitService(vikitbase.VikitBase):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, id, config=None):
        """Constructor"""
        self._id = id
        
        #
        # config
        #
        self.config = config if config else VikitServiceConfig()
        assert isinstance(self.config, VikitServiceConfig)

    
        #
        # config mod factory
        #
        self._mod_factory = mod.ModFactory(self.config.min_threads,
                                           self.config.max_threads,
                                           self.config.debug,
                                           self.config.loop_interval,
                                           self.config.adjust_interval,
                                           self.config.diviation_ms) 
        
        #
        # record task_state(running or state)
        # record client_record
        # record task_from_id
        # record
        #
        self._dict_task_state = {}
        self._dict_task_from_client_id = {}
        self._dict_client_record = {}
        self._list_offline_tasks = []
        
        #
        # result callback chains
        #
        self._list_callback_chains = []
        
        #
        # regist result callback
        #
        self.regist_result_callback(self.send_result_back)
    
    #
    # basic property
    #
    @property
    def id(self):
        """"""
        return self._id
    
    #
    # core operation functions
    #
    def load_mod(self, module_name):
        """"""
        #
        # load mod from module name
        #
        # load mod plugins firstly
        import sys
        sys.path.extend(self.config.default_mod_paths)
        from vikit.mods.config import PLUGINS_DIR
        sys.path.append(PLUGINS_DIR+'beebeeto')
        sys.path.append(PLUGINS_DIR+'bugscan')
        sys.path.append(PLUGINS_DIR+'pocsuite')
        #sys.path.append(PLUGINS_DIR+'tangscan')
        #sys.path.append(PLUGINS_DIR+'kspoc')
        #sys.path.append(PLUGINS_DIR+'tangscan/tangscan')
        # load poc dir
        from vikit.mods.config import POCS_DIR
        sys.path.append(POCS_DIR+'beebeeto')
        sys.path.append(POCS_DIR+'bugscan')
        sys.path.append(POCS_DIR+'pocsuite')
        #sys.path.append(POCS_DIR+'tangscan')
        #sys.path.append(POCS_DIR+'kspoc')
        obj = __import__(module_name)
        
        assert isinstance(obj, types.ModuleType)
        self._mod = self._mod_factory.build_standard_mod_from_module(obj)
        self._mod.regist_result_callback(self.on_task_finished, False)
    
    def execute_task(self, task_id, params):
        """"""
        assert isinstance(self._mod, mod.ModStandard)
        #
        # execute by mod
        #
        self._mod.execute(params, task_id)
        self._dict_task_state[task_id] = task_RUNNING
    
    #----------------------------------------------------------------------
    def join(self):
        """"""
        self._mod.join()
    
    #----------------------------------------------------------------------
    def quit(self):
        """"""
        self._mod.close()
    
    #----------------------------------------------------------------------
    def send_result_back(self, result_dict):
        """"""
        _tid = result_dict.get('task_id')
        
        
        _from = self._dict_task_from_client_id.get(_tid)
        
        _sender = self.get_sender(_from)

        if _sender:
            #
            # build ResponseResultAction
            #
            rspresultaction = task_action.VikitResponseResultAction(result_dict)
            
            _sender.send(rspresultaction)
            
            #
            # offline tag send to platform
            #
            if _tid in self._list_offline_tasks:
                return result_dict
            else:
                return None
        else:
            return result_dict
        
    #
    # core callback functions
    #   1. result callback
    #   2. received action obj callback
    #
    #----------------------------------------------------------------------
    def on_task_finished(self, result_obj):
        """"""
        assert isinstance(result_obj, result.Result)
        self._dict_task_state[result_obj._dict_obj['task_id']] = task_FINISHED
        
        #
        # call registed callback chains
        #
        _r = result_obj._dict_obj
        for i in self._list_callback_chains:
            if i[1]:
                try:
                    _r = i[0](_r)
                except Exception as e:
                    i[1](e)
            else:
                _r = i[0](_r)
        
    
    #
    # core callback 
    #
    #----------------------------------------------------------------------
    def on_received_obj(self, obj, *v, **kw):
        """"""
        #print('[*] service got obj: {}'.format(obj))
        from_id = kw.get('from_id')
        if from_id not in self._dict_client_record:
            if isinstance(obj, welcome_action.VikitWelcomeAction):
                self.handle_welcome_obj(obj, **kw)
        else:
            if isinstance(obj, task_action.VikitExecuteTaskAction):
                self.handle_executetaskaction_obj(obj, from_id)

            if isinstance(obj, task_action.VikitRequestTaskStatusAction):
                self.handle_request_task_status(obj)
                
            else:
                print('[!] Sorry No Handler For This Request')
    
    #----------------------------------------------------------------------
    def on_connection_lost(self, *v, **kw):
        """"""
        _from_id = kw.get('from_id')
        
        if self._dict_record_sender.has_key(_from_id):
            del self._dict_record_sender[_from_id]
        
        if self._dict_client_record.has_key(_from_id):
            del self._dict_client_record[_from_id]

        _tasks = filter(lambda x: _from_id == x, self._dict_task_from_client_id.keys())
        
        for i in _tasks:
            del self._dict_task_from_client_id[i]
            del self._dict_task_state[i]
        
    
    #----------------------------------------------------------------------
    def on_received_error_action(self, obj, *v, **kw):
        """"""
        
    
    #----------------------------------------------------------------------
    def on_connection_made(self, *v, **kw):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def handle_welcome_obj(self, obj, **kw):
        """"""
        #
        # record ordinary attrs
        #
        if not self._dict_client_record.has_key(obj.id):
            self._dict_client_record[obj.id] = {}

        self._dict_client_record[obj.id].update(kw)       
        

    
    #----------------------------------------------------------------------
    def handle_executetaskaction_obj(self, obj, from_id):
        """"""
        #raise NotImplemented()
        assert isinstance(obj, task_action.VikitExecuteTaskAction)
        
        #
        # record sender_id
        #
        self._dict_task_from_client_id[obj.id] = from_id
        if obj.offline:
            self._list_offline_tasks.append(obj.id)
        
        #
        # record params
        #
        self.execute_task(obj.id, obj.params)
        
        #
        # send feed back
        #
        _sender = self.get_sender(from_id)
        _sender.send(task_action.ACKVikitExecuteTaskAction(obj.id))
        
        return
    
    #----------------------------------------------------------------------
    def handle_request_task_status(self, obj, *v, **kw):
        """"""
        assert isinstance(obj, task_action.VikitRequestTaskStatus)
        
        _task_id = obj.id
        
        
    
    #
    # utils
    #
    #----------------------------------------------------------------------
    def regist_result_callback(self, callback, excption_callback=None):
        """"""
        assert callable(callback), 'not a callable obj'
        if excption_callback:
            assert callable(excption_callback), 'not a callable obj'
            
        self._list_callback_chains.append((callback, excption_callback))
        return 
        
    #----------------------------------------------------------------------
    def get_mod_info(self):
        """"""
        return self._mod.get_mod_info()
    
    #----------------------------------------------------------------------
    def get_info(self):
        """"""
        _ret = vikitservicedesc.VikitServiceDesc(id=self.id, 
                                                 mod_info=self.get_mod_info())
        return _ret.get_dict()
    
    
    
    