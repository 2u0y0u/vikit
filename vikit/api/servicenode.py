#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: ServiceNodeAPI
  Created: 07/02/17
"""

from vikit.apps import twistedservicenode


#----------------------------------------------------------------------
def start_servicenode(id=None, platform_host='127.0.0.1', 
                      platform_port=7000, async=False,
                      **config):
    """"""
    config = twistedservicenode.ServiceNodeConfig(platform_host='127.0.0.1',
                                                  platform_port=7000, **config)
    
    sn = twistedservicenode.TwistedServiceNode(id=id, config=config)
    sn.start()
    
    if async:
        pass
    else:
        sn.mainloop_start()
