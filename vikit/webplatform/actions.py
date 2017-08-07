#!/usr/bin/env python
# coding:utf-8
"""
  Author:  Conan0xff
  Purpose: Define Actions
  Created: 07/29/17
"""

import json

from .app import client_app

from ..api.trigger import get_platform_proxy

from flask import render_template, request, jsonify
from flask import session, redirect, url_for, make_response
from flask import g

proxy = None


@client_app.route('/start')
def start():
    """"""
    global proxy

    if proxy == None:
        proxy = get_platform_proxy(7000)
        # proxy.regist_result_callback(on_result_feedback)
    return 'success' if proxy != None else 'fail'


@client_app.route('/shutdown')
def shutdown():
    """"""
    global proxy

    proxy.shutdown()
    # return '<h1>Success</h1>'
    return "closed"


@client_app.route('/add-default-service')
def add_default_service():
    module_name = request.args.get('module_name')
    port = int(request.args.get('port'))
    global proxy
    proxy.add_default_service(module_name, port)
    return 'add success'



@client_app.route('/available-service-nodes')
def get_available_service_nodes():
    """"""
    global proxy
    return json.dumps(proxy.get_available_service_nodes())


@client_app.route('/available-service-nodes-info')
def get_available_service_nodes_info():
    global proxy
    return json.dumps(proxy.get_service_nodes_info())


@client_app.route('/get-node-info/<node_id>')
def get_service_node_info(node_id):
    global proxy
    return json.dumps(proxy.get_service_node_info_by_id(node_id))


@client_app.route('/available-services')
def get_available_services():
    """"""
    global proxy
    return json.dumps(proxy.get_available_services())


@client_app.route('/available-services-info')
def get_available_services_info():
    global proxy
    return json.dumps(proxy.get_available_services_info())


@client_app.route('/get-service-info/<service_id>')
def get_service_info(service_id):
    global proxy
    return json.dumps(proxy.get_service_info_by_id(service_id))


# common route
@client_app.route('/', methods=['GET'])
def main():
    """"""
    return render_template('main.html')
    # return render_template('main.html')
