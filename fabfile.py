"""
Deployment script.

"""
import os

from fabric import task

from deployment.strato import StratoDeployment


default_settings = {
    'BASE_DIR': os.path.dirname(__file__),
    'STATIC_ROOT': os.path.join(os.path.dirname(__file__), 'staticfiles'),
    'PYTHONPATH': os.getenv('PYTHONPATH')
}

environments = {
    'strato': {
        'DEPLOYMENT_DIR': '/home/bboogaard/apps/deployments',
        'STATIC_DIR': '/home/bboogaard/media/py-wikkel',
        'APP_DIR': '/home/bboogaard/apps/py-wikkel',
        'REMOTE_PYTHONPATH': '/home/bboogaard/vens/py-wikkel',
        'connection_kwargs': {
            'host': '85.214.231.140',
            'user': 'bboogaard',
            'connect_kwargs': {
                "key_filename": os.getenv('SSH_KEYFILE'),
            }
        }
    }
}


@task
def deploy(connection):
    settings = environments.get(connection.host)
    if not settings:
        print("No such host defined")
        return

    settings.update(default_settings)
    deployment = StratoDeployment(settings)
    deployment.run()
