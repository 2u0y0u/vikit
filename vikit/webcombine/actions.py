#!/usr/bin/env python
# coding:utf-8
"""
  Author:  Conan0xff
  Purpose: Define Actions
  Created: 07/29/17
"""

import json

from .app import client_app
from ..api.trigger import get_client_proxy
from ..api.trigger import get_platform_proxy

from flask import render_template, request, jsonify
from flask import session, redirect, url_for, make_response
from flask import g

from form import LoginForm
from flask_wtf.csrf import CsrfProtect
from model import User
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from flask_login import logout_user

# use login manager to manage session
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app=client_app)

# reload User object，根据session中存储的user id
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# csrf protextion
# csrf = CsrfProtect()
# csrf.init_app(app=client_app)

import flask


proxy = None
proxy2 = None

@client_app.route('/admin/start')
def start2():
    """"""
    global proxy2

    if proxy2 == None:
        proxy2 = get_platform_proxy(7000)
        # proxy.regist_result_callback(on_result_feedback)
    return 'success' if proxy2 != None else 'fail'

@client_app.route('/start')
def start():
    """"""
    global proxy

    if proxy==None:
        proxy = get_client_proxy('127.0.0.1', 7000)
        proxy.regist_result_callback(on_result_feedback)
    return 'success' if proxy != None else 'fail'

@client_app.route('/shutdown')
def shutdown():
    """"""
    global proxy
    global proxy2
    proxy.shutdown()
    proxy2.shutdown()
    # return '<h1>Success</h1>'
    return "closed"


@client_app.route('/add-default-service')
def add_default_service():
    module_name = request.args.get('module_name')
    port = int(request.args.get('port'))
    global proxy2
    proxy2.add_default_service(module_name, port)
    return 'add success'



@client_app.route('/available-service-nodes')
def get_available_service_nodes():
    """"""
    global proxy2
    return json.dumps(proxy2.get_available_service_nodes())


@client_app.route('/available-service-nodes-info')
def get_available_service_nodes_info():
    global proxy2
    return json.dumps(proxy2.get_service_nodes_info())


@client_app.route('/get-node-info/<node_id>')
def get_service_node_info(node_id):
    global proxy2
    return json.dumps(proxy2.get_service_node_info_by_id(node_id))


@client_app.route('/available-services')
def get_available_services():
    """"""
    global proxy2
    return json.dumps(proxy2.get_available_services())


@client_app.route('/available-services-info')
def get_available_services_info():
    global proxy2
    return json.dumps(proxy2.get_available_services_info())


@client_app.route('/get-service-info/<service_id>')
def get_service_info(service_id):
    global proxy2
    return json.dumps(proxy2.get_service_info_by_id(service_id))


# common route
@client_app.route('/', methods=['GET'])
@client_app.route('/AndDefaultService',methods=['GET'])
@login_required
def main():
    """"""
    #return "platform admin"
    return render_template('main.html')


#==============================================


# user route
@client_app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if flask.request.method=='GET':
        return render_template('login.html', form=form)

    if form.validate_on_submit():
        user_name = request.form.get('username', None)
        password = request.form.get('password', None)
        user = User(user_name)
        if user.verify_password(password):
            login_user(user)
            return redirect(url_for('main'))
        else:
            return 'login failed'

@client_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@client_app.route('/AndDefaultService', methods=['GET'])
@login_required
def AndDefaultService():
    """"""
    return render_template('AndDefaultService.html')

@client_app.route('/service_node', methods=['GET'])
@login_required
def service_node():
    """"""
    return render_template('node_list.html')

@client_app.route('/service', methods=['GET'])
@login_required
def service():
    """"""
    return render_template('service_list.html')

@client_app.route('/search', methods=['GET'])
@login_required
def search():
    """"""
    return render_template('search.html')

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
@client_app.route('/index', methods=['GET'])
@login_required
def index():
    """"""
    return render_template('index.html')


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



@client_app.route('/results', methods=['GET'])
@login_required
def all_result():
    """"""
    result='this is result'
    return render_template('results.html',result=result)

@client_app.route('/crawler', methods=['GET'])
@login_required
def crawler():
    """"""
    return render_template('crawler.html')

@client_app.route('/reqlist', methods=['GET'])
@login_required
def reqlist():
    """"""
    return render_template('reqlist.html')

@client_app.route('/monitor', methods=['GET'])
@login_required
def monitor():
    """"""
    result='this is result'
    return render_template('result.html',result=result)


