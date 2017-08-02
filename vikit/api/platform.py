"""
  Author:   --<v1ll4n>
  Purpose: API for platform
  Created: 06/30/17
"""

from twisted.internet import reactor

from ..apps import twistedplatform
from ..core.utils import getuuid

PLATFORM = None
CONFIG = None
ID = None


##
## define fsm
##
# state_START = 'start'
# state_CONNECTED = 'connected'
# state_CLOSE = 'close'

# action_START_SUCCESS = 'start_success'
# action_START_ERROR = 'start_error'
# action_SHUTDOWN = 'shutdown'

# _fsm = FSM(state_START, state_CLOSE,
# [state_CLOSE, state_CONNECTED, state_START])

# _fsm.create_action(action_START_SUCCESS, state_START, state_CONNECTED)
# _fsm.create_action(action_START_ERROR, state_START, state_CLOSE)
# _fsm.create_action(action_SHUTDOWN, state_CONNECTED, state_CLOSE)

# ----------------------------------------------------------------------
def get_platform():
    """"""
    global PLATFORM
    return PLATFORM


# ----------------------------------------------------------------------
def twisted_start_platform(port=7000, async=True, **config):
    """"""
    global ID, PLATFORM, CONFIG
    ID = id if id else getuuid()
    CONFIG = twistedplatform.PlatformConfig(port, **config)

    PLATFORM = twistedplatform.TwistedPlatform(ID, CONFIG)

    PLATFORM.start()

    if async:
        pass
    else:
        reactor.run()


def twisted_stop_platform():
    global PLATFORM
    PLATFORM.shutdown()


# ----------------------------------------------------------------------
def add_default_service(module_name, port):
    """"""
    platform = get_platform()

    assert isinstance(platform, twistedplatform.TwistedPlatform)

    platform.add_default_service(module_name, port)
    return 'add service success'


# ----------------------------------------------------------------------
def get_available_service_nodes():
    """"""
    platform = get_platform()
    assert isinstance(platform, twistedplatform.TwistedPlatform)
    return platform.get_service_nodes()


# ----------------------------------------------------------------------
def get_available_services():
    """"""
    """"""
    platform = get_platform()
    assert isinstance(platform, twistedplatform.TwistedPlatform)

    return platform.get_services()


# ----------------------------------------------------------------------
def get_services_info():
    """"""
    platform = get_platform()
    assert isinstance(platform, twistedplatform.TwistedPlatform)

    return str(platform.get_services_info())


# ----------------------------------------------------------------------
def get_service_nodes_info():
    """"""
    platform = get_platform()
    assert isinstance(platform, twistedplatform.TwistedPlatform)
    return str(platform.get_service_nodes_info())


# ----------------------------------------------------------------------
def get_service_info_by_id(service_id):
    """"""
    platform = get_platform()
    assert isinstance(platform, twistedplatform.TwistedPlatform)

    return str(platform.get_service_info_by_id(service_id))


# ----------------------------------------------------------------------
def get_service_node_info_by_id(service_node_id):
    """"""
    platform = get_platform()
    assert isinstance(platform, twistedplatform.TwistedPlatform)

    return str(platform.get_service_node_info_by_id(service_node_id))


def regist_common_result_callback(callback):
    """"""
    platform = get_platform()
    platform.regist_common_result_callback(callback)


def call_in_thread(executable):
    """"""
    reactor.callInThread(executable)


def mainloop_start():
    """"""
    platform = get_platform()
    assert isinstance(platform, twistedplatform.TwistedPlatform)
    platform.mainloop_start()
