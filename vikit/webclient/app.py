#!/usr/bin/env python
# coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: App
  Created: 07/02/17
"""

from flask import Flask
from celery import Celery, platforms

client_app = Flask(__name__)
client_app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
client_app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(client_app.name, broker=client_app.config['CELERY_BROKER_URL'])
platforms.C_FORCE_ROOT = True
celery.conf.update(client_app.config)

from . import actions
