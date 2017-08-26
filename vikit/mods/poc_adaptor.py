# coding=utf-8

from frame.beebeeto import Beebeeto
from frame.pocsuite import PocSuite
from frame.tangscan import Tangscan
from frame.kspoc import KsPoc
from frame.bugscan import Bugscan

class Poc_Adaptor(object):

    def __init__(self,pl_type,poc_obj):
        self.plugin_type=pl_type
        self.poc_obj=poc_obj

    operator = {
        'beebeeto': Beebeeto,
        'pocsuite': PocSuite,
        #'tangscan': Tangscan,
        #'kspoc'   : KsPoc,
        'bugscan' : Bugscan,
    }

    def poc_verify(self, target,payload,config):
        result = self.operator.get(self.plugin_type)().run(target, self.poc_obj)
        return result




