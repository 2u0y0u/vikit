#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Mod Define
  Created: 05/17/17
"""

from __future__ import unicode_literals

try:
    import Queue as queue
except ImportError:
    import queue
import time
import types
import os
import warnings
import traceback
import threading

from codecs import open
from g3ar import ThreadPoolX

from ..dbm import kvpersist
from . import result as vikitresult
from . import modinput
from . import utils

import sys
from vikit.mods.config import PLUGINS_DIR
sys.path.append(PLUGINS_DIR)
reload(sys)
sys.setdefaultencoding('utf8')
#
# DEFINE PRIVATE VAR
#
_CURRENT_PATH = os.path.dirname(__file__)
_DEFAULT_DATAS_PATH_R = '../datas/'
_DEFAULT_DATAS_PATH = os.path.join(_CURRENT_PATH, _DEFAULT_DATAS_PATH_R)

_DEFAULT_MODSBUFFER_PATH_R = '../modsbuffer/'
_DEFAULT_MODSBUFFER_PATH = os.path.join(_CURRENT_PATH, _DEFAULT_MODSBUFFER_PATH_R)


#
# define keywords
#
NAME = 'NAME' # mod name

AUTHOR = 'AUTHOR' # mod author 
DESCRIPTION = 'DESCRIPTION' # mod description
RESULT_DESC = 'RESULT_DESC' # return of the result

# demands
INPUT = 'DEMANDS' 
INPUT_DEMANDS = 'DEMANDS'
INPUT_CHECK_FUNC = 'INPUT_CHECK_FUNC'

# core function
EXPORT_FUNC = 'EXPORT_FUNC'

# search interface: def search(key)
SEARCH_FUNC = 'SEARCH_FUNC'

# db interface
DATA_DIR = 'DATA_DIR'
PERSISTENCE_FUNC = 'PERSISTENCE_FUNC'
DELETE_FROM_DB_FUNC = 'DELETE_FROM_DB_FUNC'

BUILD_IN_VAR = [NAME,
                AUTHOR,
                DESCRIPTION,
                INPUT,
                INPUT_DEMANDS,
                EXPORT_FUNC, 
                SEARCH_FUNC,
                DATA_DIR,
                PERSISTENCE_FUNC,
                #QUERY_FUNC,
                RESULT_DESC,
                INPUT_CHECK_FUNC]

_MOD_ATTRS = ['min_threads', 'max_threads', 'debug',
              'loop_interval', 'adjust_interval', 'diviation_ms']

########################################################################
class Mod(object):
    """"""
    
    #----------------------------------------------------------------------
    def init(self):
        """"""
        pass
    

########################################################################
class ModBase(Mod):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, name, min_threads=5, max_threads=20, debug=False,
                 loop_interval=0.2, adjust_interval=3, diviation_ms=100):
        """Constructor"""
        Mod.__init__(self)
        
        self._name = name
        
        #
        # initial pool
        #
        self._min = min_threads
        self._max = max_threads
        self.pool = ThreadPoolX(min_threads=self._min, max_threads=self._max,
                                 name=name, debug=debug, loop_interval=loop_interval,
                                 adjuest_interval=adjust_interval, 
                                 diviation_ms=diviation_ms )
        
        
        #
        # set result recv and callback
        #
        self._result_queue = queue.Queue()
        self.pool.add_callbacks(callback=self._feed_result)
        
        self._core_func = None
        
        self.pool.start()
        
        #
        # userdefine regist result callback
        #
        self._userdefine_result_callback = None
        self._flat_in2queue = True
    
    #----------------------------------------------------------------------
    def __del__(self):
        """"""
        self.pool.quit()
        
    
    #----------------------------------------------------------------------
    def _feed_result(self, result):
        """"""
        if self._userdefine_result_callback:
            self._userdefine_result_callback(result)
        
        #print('CALLBACK IS CALLED!')
        self._result_queue.put(result)
        return result

    #----------------------------------------------------------------------
    def regist_result_callback(self, callback, add_in_queue=True):
        """"""
        if add_in_queue:
            self._flat_in2queue = True
        else:
            self._flat_in2queue = False
        
        assert callable(callback)
        self._userdefine_result_callback = callback
        
    
    #----------------------------------------------------------------------
    def execute(self, modinput_dict, task_id=None):
        """"""
        assert isinstance(modinput_dict, dict)
        modinput_dict = self.hook_check_params(modinput_dict)
        self.pool.feed(target=self._exec, vargs=(task_id, modinput_dict, ))
    
    #----------------------------------------------------------------------
    def hook_check_params(self, params):
        """"""
        return params
    
    #----------------------------------------------------------------------
    def _exec(self, task_id, modinput_dict):
        """"""
        exception_data = None
        try:
            _r = self._core_func(**modinput_dict)
        except Exception as e:
            _result = traceback.format_exc()
            _r = {}
            exception_data = _result
            
        _result = {'start_time':time.time(),
                   'task_id': task_id,
                   'from':str(self._core_func),
                   'payload':modinput_dict,
                   'result':_r,
                   'exception':exception_data}
        
        result = vikitresult.Result(_result)
        return result
    
    @property
    def result_queue(self):
        """"""
        return self._result_queue
    
    @property
    def pool_status(self):
        """"""
        return self.pool.dumped_status()
    
    #----------------------------------------------------------------------
    def join(self):
        """"""
        self.pool.join()
    
    #----------------------------------------------------------------------
    def close(self):
        """"""
        self.pool.quit()


########################################################################
class ModBasic(ModBase):
    """"""

    #----------------------------------------------------------------------
    def from_function(self, func):
        """"""
        assert callable(func), 'func is not a callable function or method.'
        self._core_func = func
    
    #----------------------------------------------------------------------
    def from_module(self, module_obj):
        """"""
        assert hasattr(module_obj, 'EXPORT_FUNC')
        
        self._core_func = getattr(module_obj, 'EXPORT_FUNC')
        

########################################################################
class ModFunction(ModBase):
    """"""

    #----------------------------------------------------------------------
    def from_function(self, func):
        """"""
        assert callable(func), 'func is not a callable function or method.'
        self._core_func = func

########################################################################
class ModStandard(ModBase):
    """"""
    
    #----------------------------------------------------------------------
    def __del__(self):
        """"""
        self.pool.quit()
        self.KVP.close()
    
    #----------------------------------------------------------------------
    def init(self):
        """"""
        pass

    #----------------------------------------------------------------------
    def init_db(self):
        """"""
        #
        # create kvp
        #
        self.KVP = kvpersist.KVPersister(self.default_datadir(self.NAME))
        
    
    #----------------------------------------------------------------------
    def default_datadir(self, name):
        """"""
        #
        # default bdb
        #
        _dir = os.path.join(_DEFAULT_DATAS_PATH, name + '.kvp')
        if os.path.exists(_DEFAULT_DATAS_PATH):
            pass
        else:
            os.mkdir(_DEFAULT_DATAS_PATH)
        
        
        
        return _dir
    
    #
    # define standard mod obj, containing description/author/demands
    #
    #----------------------------------------------------------------------
    def from_module(self, module_obj):
        """"""
        assert isinstance(module_obj, types.ModuleType)
        from vikit.mods.poc_adaptor import Poc_Adaptor
        module_type='vikit'
        #detect the module_obj's type,check if it is a poc
        if hasattr(module_obj,'MyPoc'):
            module_type='beebeeto'
        elif hasattr(module_obj,'TestPOC'):
            module_type='pocsuite'
        elif hasattr(module_obj,'TangScan'):
            module_type='tangscan'
        elif hasattr(module_obj,'main'):
            module_type='kspoc'
        elif hasattr(module_obj,'audit'):
            module_type='bugscan'
        else:
            pass

        if module_type=='vikit':
            #
            # process name/author/description/data_dir
            #
            if hasattr(module_obj, NAME):
                self.NAME = getattr(module_obj, NAME)
            else:
                self.NAME = self._name

            if hasattr(module_obj, AUTHOR):
                self.AUTHOR = getattr(module_obj, AUTHOR)
            else:
                self.AUTHOR = 'vikit'

            if hasattr(module_obj, DESCRIPTION):
                self.DESCRIPTION = getattr(module_obj, DESCRIPTION)
            else:
                self.DESCRIPTION = 'No Description For module'

            if hasattr(module_obj, DATA_DIR):
                self.DATA_DIR = getattr(module_obj, DATA_DIR)
            else:
                self.DATA_DIR = _DEFAULT_DATAS_PATH


            #
            # process result_desc/export_func/
            #
            RESULT_DESC='RESULT_DESC'
            assert hasattr(module_obj, RESULT_DESC)
            self.RESULT_DESC = getattr(module_obj, RESULT_DESC)

            assert hasattr(module_obj, EXPORT_FUNC)
            assert callable(getattr(module_obj, EXPORT_FUNC))
            self._core_func = getattr(module_obj, EXPORT_FUNC)
            self.EXPORT_FUNC = getattr(module_obj, EXPORT_FUNC)

            assert hasattr(module_obj, INPUT)
            self.DEMANDS = tuple(getattr(module_obj, INPUT))


            #
            # default callable functions: INPUT_CHECK_FUNC/SEARCH_FUNC
            #                             /PERSISTENCE_FUNC/QUERY_FUNC
            if hasattr(module_obj, INPUT_CHECK_FUNC):
                _ = getattr(module_obj, INPUT_CHECK_FUNC)
                assert callable(_)
                self.INPUT_CHECK_FUNC = _
            else:
                self.INPUT_CHECK_FUNC = self._check_input

            if hasattr(module_obj, SEARCH_FUNC):
                _ = getattr(module_obj, SEARCH_FUNC)
                assert callable(_)
                self.SEARCH_FUNC = _
            else:
                self.SEARCH_FUNC = self._search_func

            if hasattr(module_obj, PERSISTENCE_FUNC):
                _ = getattr(module_obj, PERSISTENCE_FUNC)
                assert callable(_)
                self.PERSISTENCE_FUNC = _
            else:
                self.PERSISTENCE_FUNC = self._persistence_func

            if hasattr(module_obj, DELETE_FROM_DB_FUNC):
                _ = getattr(module_obj, DELETE_FROM_DB_FUNC)
                assert callable(_)
                self.DELETE_FROM_DB_FUNC = _
            else:
                self.DELETE_FROM_DB_FUNC = self._delete_func

            _cdb = True
            if self.PERSISTENCE_FUNC == self._persistence_func and \
               self.SEARCH_FUNC == self._search_func and \
               self.DELETE_FROM_DB_FUNC == self._delete_func:
                pass
            elif self.PERSISTENCE_FUNC != self._persistence_func and \
                 self.SEARCH_FUNC != self._search_func and \
                 self.DELETE_FROM_DB_FUNC != self._delete_func:
                _cdb = False
            else:
                warnings.warn('db define should set ' + \
                   'PERSISTENCE_FUNC, SEARCH_FUNC and DELETE_FROM_DB_FUNC at the same time')
                pass

            #
            # initial db
            #
            if _cdb:
                self.init_db()
            else:
                pass

            modenv = vars(module_obj)
            for i in BUILD_IN_VAR:
                modenv[i] = getattr(self, i)
        else:
            #
            # process name/author/description/data_dir
            #
            poc_adaptor=Poc_Adaptor(module_type,module_obj)

            self.NAME=Poc_Adaptor.operator.get(module_type)().get_vul_info(module_obj)['name']
            if Poc_Adaptor.operator.get(module_type)().get_vul_info(module_obj).has_key('author'):
                self.AUTHOR =Poc_Adaptor.operator.get(module_type)().get_vul_info(module_obj)['author']
            else:
                self.AUTHOR='vikit'

            if Poc_Adaptor.operator.get(module_type)().get_vul_info(module_obj).has_key('desc'):
                self.DESCRIPTION = Poc_Adaptor.operator.get(module_type)().get_vul_info(module_obj)['desc']
            else:
                self.DESCRIPTION='no description'

            self.DATA_DIR = _DEFAULT_DATAS_PATH

            #
            # process result_desc/export_func/
            #
            RESULT_DESC = 'this description is about result from '+module_type
            self.RESULT_DESC = RESULT_DESC

            self._core_func = poc_adaptor.poc_verify
            self.EXPORT_FUNC = poc_adaptor.poc_verify

            from vikit.core.basic.modinput import TargetDemand, PayloadDemand, ParamDemand
            from vikit.core.basic import target, payload, param
            self.DEMANDS = tuple([TargetDemand('target', target.TYPE_URL),
                       PayloadDemand('payload', payload.TYPE_TEXT),
                       ParamDemand('param1', param.TYPE_BOOL),
                       ParamDemand('param2', param.TYPE_STR)])

            #
            # default callable functions: INPUT_CHECK_FUNC/SEARCH_FUNC
            #                             /PERSISTENCE_FUNC/QUERY_FUNC
            if hasattr(module_obj, INPUT_CHECK_FUNC):
                _ = getattr(module_obj, INPUT_CHECK_FUNC)
                assert callable(_)
                self.INPUT_CHECK_FUNC = _
            else:
                self.INPUT_CHECK_FUNC = self._check_input

            if hasattr(module_obj, SEARCH_FUNC):
                _ = getattr(module_obj, SEARCH_FUNC)
                assert callable(_)
                self.SEARCH_FUNC = _
            else:
                self.SEARCH_FUNC = self._search_func

            if hasattr(module_obj, PERSISTENCE_FUNC):
                _ = getattr(module_obj, PERSISTENCE_FUNC)
                assert callable(_)
                self.PERSISTENCE_FUNC = _
            else:
                self.PERSISTENCE_FUNC = self._persistence_func

            if hasattr(module_obj, DELETE_FROM_DB_FUNC):
                _ = getattr(module_obj, DELETE_FROM_DB_FUNC)
                assert callable(_)
                self.DELETE_FROM_DB_FUNC = _
            else:
                self.DELETE_FROM_DB_FUNC = self._delete_func

            _cdb = True
            if self.PERSISTENCE_FUNC == self._persistence_func and \
                            self.SEARCH_FUNC == self._search_func and \
                            self.DELETE_FROM_DB_FUNC == self._delete_func:
                pass
            elif self.PERSISTENCE_FUNC != self._persistence_func and \
                            self.SEARCH_FUNC != self._search_func and \
                            self.DELETE_FROM_DB_FUNC != self._delete_func:
                _cdb = False
            else:
                warnings.warn('db define should set ' + \
                              'PERSISTENCE_FUNC, SEARCH_FUNC and DELETE_FROM_DB_FUNC at the same time')
                pass

            #
            # initial db
            #
            if _cdb:
                self.init_db()
            else:
                pass

            modenv = vars(module_obj)
            for i in BUILD_IN_VAR:
                modenv[i] = getattr(self, i)

    
    #----------------------------------------------------------------------
    def _delete_func(self, key):
        """"""
        return self.KVP.delete(key)
            
    #----------------------------------------------------------------------
    def _persistence_func(self, key, value):
        """"""
        return self.KVP.set(key, value)
    
    #----------------------------------------------------------------------
    def _search_func(self, key):
        """"""
        return self.KVP.get(key)
    
    #----------------------------------------------------------------------
    def hook_check_params(self, params):
        """"""
        try:
            self.INPUT_CHECK_FUNC(**params)
        except:
            warnings.warn('user define input_check_func error! ' + \
                          'execute default check function!')
            self._check_input(**params)
        
        return params
    
    #----------------------------------------------------------------------
    def _check_input(self, **params):
        """"""
        self._inputchecker = modinput.ModInput(*self.DEMANDS)
    
        self._inputchecker.check_from_dict(params, stricted=True)
    
    #----------------------------------------------------------------------
    def get_mod_info(self):
        """"""
        _infos = {}
        for i in BUILD_IN_VAR:
            if not hasattr(self, i):
                pass
            else:
                _infos[i] = str(getattr(self, i))
        
        return _infos
        


########################################################################
class ModFactory(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, min_threads=5, max_threads=20, debug=True,
                 loop_interval=0.2, adjust_interval=3, diviation_ms=100):
        """Constructor"""
        
        assert int(max_threads) > int(min_threads)
        
        self.min_threads = int(min_threads)
        self.max_threads = int(max_threads)
        
        self.debug = debug
        
        self.loop_interval = loop_interval
        self.adjust_interval = adjust_interval
        self.diviation_ms = diviation_ms
        
    #----------------------------------------------------------------------  
    def mod_args(self, **kwargs):
        """"""
        #
        # init
        #
        _r = {}
        for i in _MOD_ATTRS:
            _r[i] = getattr(self, i)
        
        for kv in kwargs.iteritems():
            k = kv[0]
            v = kv[1]
            
            if _r.has_key(k):
                _r[k] = v
            else:
                pass
        
        return _r
    
    
    #
    # create empty mod 
    #
    #----------------------------------------------------------------------
    def get_basic_mod(self, **kw):
        """"""
        return ModBasic(name=utils.uuidhex(), **self.mod_args(**kw))
    
    #----------------------------------------------------------------------
    def get_function_mod(self, **kw):
        """"""
        return ModFunction(name=utils.uuidhex(), **self.mod_args(**kw))
        
    #----------------------------------------------------------------------
    def get_standard_mod(self, **kw):
        """"""
        return ModStandard(name=utils.uuidhex(), **self.mod_args(**kw))
        
    
    #----------------------------------------------------------------------
    def build_standard_mod_from_module(self, module_obj, **mod_args):
        """"""
        _ = self.get_standard_mod(**mod_args)

        try:
            _.from_module(module_obj)
        except Exception as e:
            raise e
    
        return _    
    
    #----------------------------------------------------------------------
    def build_basic_mod_from_function(self, target_func, **mod_args):
        """"""
        _ = self.get_function_mod(**mod_args)
        
        try:
            _.from_function(target_func)
        except Exception as e:
            raise e
        
        return _
    
    #----------------------------------------------------------------------
    def build_basic_from_module(self, module_obj, **mod_args):
        """"""
        _ = self.get_basic_mod(**mod_args)
        
        try:
            _.from_module(module_obj)
        except Exception as e:
            raise e 
        
        return _
        
        