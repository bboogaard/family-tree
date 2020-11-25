"""
Deployment for strato server.

"""
import os

from deployment.base import Deployment


class StratoDeployment(Deployment):
    """Deployment class for strato server."""

    def post_deploy(self, archive_files):
        super().post_deploy(archive_files)

        # Create symlink and restart server and worker
        result = self.connection.run(
            'test -d {}'.format(self.settings['APP_DIR']), warn=True
        )
        if result.ok:
            self.connection.run('rm {}'.format(self.settings['APP_DIR']))
        source = os.path.join(self.settings['DEPLOYMENT_DIR'], self.name)
        self.connection.run('ln -s {} {}'.format(
            source, self.settings['APP_DIR']
        ))

        self.connection.run('sudo systemctl restart gunicorn', pty=True)
