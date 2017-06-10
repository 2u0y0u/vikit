#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Platform
  Created: 05/22/17
"""

from . import actions

########################################################################
class Platform(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, name, host, port):
        """Constructor"""
        
        self._name = name
        
        self._host = host
        self._port = port
        
        #
        # conn pool
        #
        self._conn_pool = {}
        self._state_pool = {}
        
    @property
    def name(self):
        """"""
        return self._name
    
    #----------------------------------------------------------------------
    def get_service(self, service_id):
        """"""
        
    #----------------------------------------------------------------------
    def show_service(self):
        """"""
    
    #----------------------------------------------------------------------
    def dump_service_status(self, service_id):
        """"""
    
    #----------------------------------------------------------------------
    def stop_service(self, service_id):
        """"""
        #
        # send stop action
        #
        actions.StopService(service_id)
    
    #
    # add bind and remove bind
    #
    #----------------------------------------------------------------------
    def add_bind(self, service_id, conn):
        """"""
        if self._conn_pool.has_key(service_id):
            raise AssertionError('repeat service id!')
        else:
            self._conn_pool[service_id] = conn
    
    #----------------------------------------------------------------------
    def remove_bind(self, service_id):
        """"""
        if self._conn_pool.has_key(service_id):
            del self._conn_pool[service_id]
        else:
            pass
        

    #----------------------------------------------------------------------
    def update_heartbeat(self, obj):
        """"""
        assert isinstance(obj, actions.Hearbeat)

        #
        # update state by heartbeat
        #
#
# define twisted protocal
#

from twisted.internet.protocol import Protocol, Factory

from .serializer import Serializer
from . import actions

########################################################################
class PlatformTwistedConn(Protocol):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self, platform, crytor=None):
        """"""
        
        assert isinstance(platform, Platform)
        self._platform = platform
        self._cryptor = crytor
        
        self.serlzr = Serializer(self._cryptor)
        
        self.STATE = 'init'
    
    #----------------------------------------------------------------------
    def connectionMade(self):
        """"""
        self.send(actions.Welcome(self._platform.name))
    
    #----------------------------------------------------------------------
    def connectionLost(self, reason=''):
        """"""
        self._platform.remove_bind(self._sid)
    
    #----------------------------------------------------------------------
    def dataReceived(self, data):
        """"""
        
        obj = self.serlzr.unserialize(data)
        
        self._handle_obj(obj)
    
    #----------------------------------------------------------------------
    def _handle_obj(self, obj):
        """"""
        print obj
        if self.STATE == 'init':
            if isinstance(obj, actions.Welcome):
                #
                # welcome 
                #
                self.STATE = 'working'
                
                #
                # add bind and record sid
                #
                self._platform.add_bind(obj.sid, self)
                self._sid = obj.sid
            
        if self.STATE == 'working':
            if isinstance(obj, actions.Hearbeat):
                #
                # update heartbeat
                #
                self._platform.update_heartbeat(obj)
            elif isinstance(obj, actions.StopServiceACK):
                #
                # receive ack for stop service
                #
                self._platform.remove_bind(obj.sid)
        
    
    #----------------------------------------------------------------------
    def send(self, obj):
        """"""
        #
        # send to peer service
        #
        text = self.serlzr.serialize(obj)
        self.transport.write(text)
    

########################################################################
class PlatformTwistedConnFactory(Factory):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, platform, cryptor=None, *vargs, **kwargs):
        """Constructor"""
        #
        # pass in attrs
        #
        self.cryptor = cryptor
        self.platform = platform
    
    #----------------------------------------------------------------------
    def buildProtocol(self, addr):
        """"""
        return PlatformTwistedConn(self.platform, self.cryptor)
        
    
    