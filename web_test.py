from vikit.webclient.app import client_app
from vikit .webclient.app import celery

if __name__=='__main__':

    client_app.run('0.0.0.0', 8080, debug=True)
