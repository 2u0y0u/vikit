#!/usr/bin/env python
# coding:utf-8
"""
  Author:   --<v1ll4n>
  Purpose: Define Actions
  Created: 07/02/17
"""

import json

from .app import client_app
from .app import celery

from ..api.trigger import get_client_proxy
from ..api.trigger import get_platform_proxy
from flask import render_template, request, jsonify
from flask import session, redirect, url_for, make_response
from flask import g

proxy = None
proxy2 = None


@client_app.route('/start')
def start():
    """"""
    global proxy

    if proxy == None:
        proxy = get_client_proxy('127.0.0.1', 7000)
        proxy.regist_result_callback(on_result_feedback)
    return 'success' if proxy != None else 'fail'


# -----------------------------------------
@client_app.route('/admin/start')
def start2():
    """"""
    global proxy2

    if proxy2 == None:
        proxy2 = get_platform_proxy(7000)
        # proxy.regist_result_callback(on_result_feedback)
    return 'success' if proxy != None else 'fail'


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


# ---------------------------------------------
@client_app.route('/shutdown')
def shutdown():
    """"""
    global proxy

    proxy.shutdown()
    # return '<h1>Success</h1>'
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


result = {}


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
    # 往结果字典加入(task_id:'processing')
    global result
    status_and_result=('processing',None)
    result[task_id] = status_and_result
    # 返回结果页面
    return redirect('results')


def on_result_feedback(result_dict):
    task_id = result_dict.get('task_id')
    task_result = result_dict.get('result')
    global result
    # 改变对应的task状态
    status_and_result=('finished',task_result)
    result[task_id] = status_and_result


@client_app.route('/results', methods=['GET'])
def all_result():
    """"""
    global result
    all_result=json.dumps(result)

    return render_template('results.html',result=all_result)     


@client_app.route('/result/<task_id>', methods=['get'])
def show_result(task_id):
    # 点击查看结果时显示
    if result != None and result.get(task_id)[0] == 'finished':
        return render_template('result.html', result=result, task_id=task_id)
    else:
        return render_template('result.html', result='task is not finish', task_id=task_id)


@client_app.route('/task_status/<task_id>', methods=['get'])
def get_status(task_id):
    if result and result.has_key(task_id):
        return result[task_id][0]  # processing finished
    else:
        return 'wrong task_id'


from vikit.mod_tools.ConaPenTSuite.search_url.search_url import conasearch

@client_app.route('/crawler', methods=['GET'])
def crawler2():
    """"""
    return render_template('crawler.html')

@celery.task(bind=True)
def get_targets(self, engine='baidu', key='python', start_page=1, end_page=3, page_size=10):
    result = []
    print engine,key,start_page,end_page,page_size
    for i in range(start_page, end_page + 1):
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': end_page - start_page + 1, 'status': 'processing'})
        result.extend(conasearch(engine=engine, key=key, page_num=i, page_size=page_size, savefile=0))
    return {'current': end_page, 'total': end_page - start_page + 1, 'status': 'completed', 'result': result}


@client_app.route('/get_targets', methods=['POST'])
def crawler():
    """"""
    engine = request.form['engine'].strip()
    key = request.form['key'].strip()
    start_page = int(request.form['start_page'].strip())
    end_page = int(request.form['end_page'].strip())
    page_size = int(request.form['page_size'].strip())
    #return jsonify(get_targets2(engine,key,start_page,end_page,page_size))
    task = get_targets.apply_async(args=[engine, key, start_page, end_page, page_size])
    #return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}
    return jsonify({'task_id':task.id})


@client_app.route('/status/<task_id>')
def taskstatus(task_id):
    task = get_targets.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 100,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 100),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # some thing went wrong in the background job
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 100),
            'status': str(task.info)
        }
    return jsonify(response)
