#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: 
  Created: 07/02/17
"""

from .app import client_app


#----------------------------------------------------------------------
def run():
    """"""
    client_app.run('127.0.0.1', 80, debug=True)
    
