#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: App
  Created: 07/02/17
"""

from flask import Flask

client_app = Flask(__name__)
client_app.config['SECRET_KEY'] = 'conan2151234512'
from . import actions


