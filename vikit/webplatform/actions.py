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
csrf = CsrfProtect()
csrf.init_app(app=client_app)

import flask

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
@client_app.route('/index',methods=['GET'])
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
def AndDefaultService():
    """"""
    return render_template('AndDefaultService.html')

@client_app.route('/service_node', methods=['GET'])
def service_node():
    """"""
    return render_template('node_list.html')

@client_app.route('/service', methods=['GET'])
def service():
    """"""
    return render_template('service_list.html')

@client_app.route('/search', methods=['GET'])
def search():
    """"""
    return render_template('search.html')

