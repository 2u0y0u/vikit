#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Define VikitBase
  Created: 06/17/17
"""

import time
import queue
from abc import ABCMeta, abstractmethod

from ..vikitlogger import get_netio_logger

logger = get_netio_logger()

########################################################################
class _CacheSender():
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """"""
        self.queue = queue.Queue()
    
    #----------------------------------------------------------------------
    def send(self, obj):
        """"""
        self.queue.put(obj)
        
    
    

########################################################################
class VikitBase(object):
    """"""
    
    __metaclass__ = ABCMeta
    
    disable_default_connectionMade = False
    
    _dict_record_sender = {}
    
    #----------------------------------------------------------------------
    def get_cache_sender(self):
        """"""
        if not hasattr(self, '_cache_sender'):
            self._cache_sender = _CacheSender()
        else:
            pass
        
        return self._cache_sender
        

    #
    # result callback
    #
    @abstractmethod
    def on_received_obj(self):
        """"""
        pass
    
    @abstractmethod
    def on_connection_made(self, *vargs, **kw):
        """"""
        pass
    
    @abstractmethod
    def on_connection_lost(self, *vargs, **kw):
        """"""
        pass
    
    @abstractmethod
    def on_received_error_action(self, *v, **kw): #on_error_happend
        """"""
        pass
    
    def on_received_success_action(self):
        """"""
        pass
    
    #
    # sender
    #
    #@abstractmethod
    def get_sender(self, id=None):
        """"""
        if id:
            return self._dict_record_sender.get(id, self.get_cache_sender())
        else:
            return self._dict_record_sender.get('*', self.get_cache_sender())
    
    #@abstractmethod
    def regist_sender(self, sender, id=None):
        """"""
        if id is None:
            id = '*'
            
        if self._dict_record_sender.has_key(id):
            pass
        else:
            self._dict_record_sender[id] = sender
            
    #
    # connected?
    #
    @property
    def connected(self):
        """"""
        if hasattr(self, '_connected'):
            pass
        else:
            setattr(self, '_connected', False)
        
        return getattr(self, '_connected')
    
    @connected.setter
    def connected(self, value):
        """"""
        self._connected = value
        