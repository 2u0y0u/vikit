#coding=utf-8
import imp
import sys

from ..config import PLUGINS_DIR

class Beebeeto(object):

    plugins_name = 'beebeeto'
    result = {
        'vul_info': {},
        'result': {}
    }

    def get_vul_info(self, poc):
        vul_info = {
            'name': poc.MyPoc.poc_info['poc']['name'],
            'author': poc.MyPoc.poc_info['poc']['author'],
            'desc': poc.MyPoc.poc_info['vul']['desc']
        }
        return vul_info

    def run(self, target, poc_obj):
        try:
            options = {
                'target': target,
                'verify': True,
                'verbose': False,
            }
            ret = poc_obj.MyPoc(False).run(options=options, debug=False)
            if ret['success'] == True:
                self.result['vul_info'] = self.get_vul_info(poc_obj)
                self.result['result'] = ret['poc_ret']
                return self.result
            else:
                return {}
        except Exception,e:
            print e
            return
