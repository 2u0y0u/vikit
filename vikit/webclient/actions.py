#!/usr/bin/env python
# coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Define Actions
  Created: 07/02/17
"""

import json

from .app import client_app

from ..api.trigger import get_client_proxy

from flask import render_template, request, jsonify
from flask import session, redirect, url_for, make_response
from flask import g

proxy = None


@client_app.route('/start')
def start():
    """"""
    global proxy

    if proxy==None:
        proxy = get_client_proxy('39.108.169.134', 7000)
        proxy.regist_result_callback(on_result_feedback)
    return 'success' if proxy != None else 'fail'


@client_app.route('/shutdown')
def shutdown():
    """"""
    global proxy

    proxy.shutdown()
    #return '<h1>Success</h1>'
    return "closed" 

@client_app.route('/available-modules')
def get_available_module():
    """"""
    global proxy
    proxy.get_available_modules()
    return json.dumps(proxy.get_available_modules())


@client_app.route('/help/<module_name>')
def help(module_name):
    """"""
    global proxy
    _ret = proxy.get_help_for_module(module_name)
    return json.dumps(_ret)


# common route
@client_app.route('/', methods=['GET'])
def main():
    """"""
    return render_template('main.html')


@client_app.route('/select_module/<module_name>', methods=['GET'])
def on_select_module(module_name):
    """
    return module_help and module params 
    """
    global proxy
    _ret = proxy.get_help_for_module(module_name)
    module_help = json.dumps(_ret)
    return render_template('main.html', module_help=module_help, selected_module=module_name)


@client_app.route('/execute', methods=['post'])
def execute():
    """
    get params from form and translate into json then execute
    """
    # def execute(self, module_name, params, offline=False, task_id=None):
    global proxy
    module_name = request.form['module'].strip()
    target = request.form['target'].strip()
    payload = request.form['payload'].strip()
    config = json.loads(request.form['config'].strip())
    offline = True if request.form['offline'] != '0' else False

    task_id = proxy.execute(module_name, {"target": target,
                                          'payload': payload,
                                          'config': config
                                          },
                            offline=offline)

    #return '<p>waif for few seconds until the result back.</p><br><a href="result/'+str(task_id)+'">'+'check result here'+'</a>' 
    return redirect('result/'+task_id)
    

result = None


def on_result_feedback(result_dict):
    task_id = result_dict.get('task_id')
    task_result = result_dict.get('result')
    global result
    result = {'task_id': task_id, 'task_result': task_result}
    # return json.dumps({'task_id': task_id, 'task_result': task_result})


@client_app.route('/result/<task_id>', methods=['get'])
def show_result(task_id):
    if result != None and result.get('task_id') == task_id:
        #return '<p>task_id:' + result.get('task_id') + '</p><br>' + '<p>task_result:' + str(
        #    result.get('task_result')) + '</p>'
        return render_template('result.html', result=result, task_id=task_id)
    else:
        return render_template('result.html')

