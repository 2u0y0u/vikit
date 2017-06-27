#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Define VikitBase
  Created: 06/17/17
"""

import time
from abc import ABCMeta, abstractmethod

from ..vikitlogger import get_netio_logger

logger = get_netio_logger()

########################################################################
class VikitBase(object):
    """"""
    
    __metaclass__ = ABCMeta
    
    disable_default_connectionMade = False
    
    _dict_record_sender = {}

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
    def get_sender(self, id, default=None, timeout=10):
        """"""
        end = time.time() + timeout
        
        logger.debug('[vikit_entity] getting sender!')
        while (not self.connected) and end > time.time() :
            pass
        logger.debug('[vikit_entity] got sender')
        
        return self._dict_record_sender.get(id, default)
    
    #@abstractmethod
    def regist_sender(self, sender, id=None):
        """"""
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
        