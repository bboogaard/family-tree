"""
Base class for the deployments.

"""
import os
import shutil
import zipfile

from fabric import Connection
from git import Repo


class Deployment(object):
    """Base class for the deployments.

    """

    files = [
        'lib',
        'settings',
        'tree',
        '__init__.py',
        'CHANGES.txt',
        'manage.py',
        'requirements.txt',
        'urls.py',
        'version.py',
        'wsgi.py'
    ]

    def __init__(self, settings):
        self.settings = settings

        self.distribution_dir = os.path.join(self.settings['BASE_DIR'], 'dist')
        self.repo = Repo(self.settings['BASE_DIR'])
        self.name = str(self.repo.commit(self.repo.active_branch))[:7]

        self.local = Connection('localhost')
        self.connection = Connection(**self.settings['connection_kwargs'])

    def run(self):
        # Create dist dir for the zipfiles
        self.create_distribution_dir()

        # Create zipfiles containing repo and static files
        repo_archive = self.create_repo_archive()
        static_archive = self.create_static_archive()

        self.connection.open()

        self.pre_deploy()

        # Upload the zipfiles
        self.upload_archive(repo_archive, self.settings['DEPLOYMENT_DIR'])
        self.upload_archive(static_archive, self.settings['STATIC_DIR'])

        # Extract and update repo
        remote_repo_archive = os.path.join(
            self.settings['DEPLOYMENT_DIR'], os.path.basename(repo_archive)
        )
        destination = os.path.join(self.settings['DEPLOYMENT_DIR'], self.name)
        self.extract_archive(remote_repo_archive, destination)

        self.update_repo(destination)

        # Extract static files
        remote_static_archive = os.path.join(
            self.settings['STATIC_DIR'], os.path.basename(static_archive)
        )
        destination = os.path.join(self.settings['STATIC_DIR'], 'staticfiles')
        self.extract_archive(remote_static_archive, destination)

        # Clean up and finalize
        self.post_deploy([remote_repo_archive, remote_static_archive])

        self.connection.close()

    def pre_deploy(self):
        pass

    def post_deploy(self, archive_files):
        for archive_file in archive_files:
            self.connection.run('rm {}'.format(archive_file))

    def create_distribution_dir(self):
        if os.path.exists(self.distribution_dir):
            shutil.rmtree(self.distribution_dir)
        os.makedirs(self.distribution_dir)

    def create_repo_archive(self):
        archive_name = os.path.join(
            self.distribution_dir, '{}.zip'.format(self.name)
        )
        files = self.get_files()
        with open(archive_name, 'wb') as fh:
            self.repo.archive(fh, format='zip', path=files)
        return archive_name

    def create_static_archive(self):
        if os.path.exists(self.settings['STATIC_ROOT']):
            shutil.rmtree(self.settings['STATIC_ROOT'])
        self.local.local(
            'source {PYTHONPATH}/bin/activate && '
            'source {PYTHONPATH}/bin/postactivate && '
            'python manage.py collectstatic '
            '--noinput --settings=settings.deploy'.format(
                PYTHONPATH=self.settings['PYTHONPATH']
            )
        )

        archive_name = os.path.join(self.distribution_dir, 'staticfiles.zip')
        with zipfile.ZipFile(archive_name, 'w') as fh:
            for root, dirs, files in os.walk(self.settings['STATIC_ROOT']):
                for file in files:
                    fh.write(
                        os.path.join(root, file),
                        os.path.join(
                            os.path.relpath(
                                root, self.settings['STATIC_ROOT']
                            ),
                            file
                        )
                    )

        return archive_name

    def upload_archive(self, archive_name, destination):
        result = self.connection.run(
            'test -d {}'.format(destination),
            warn=True
        )
        if result.failed:
            self.connection.run('mkdir {}'.format(destination))
        self.connection.put(archive_name, remote=destination)

    def extract_archive(self, archive_name, destination):
        result = self.connection.run(
            'test -d {}'.format(destination),
            warn=True
        )
        if result.ok:
            self.connection.run('rm -rf {}'.format(destination))
        self.connection.run('unzip {} -d {}'.format(archive_name, destination))

    def update_repo(self, repo_dir):
        result = self.connection.run(
            'cmp {}/requirements.txt {}/requirements.txt'.format(
                repo_dir, self.settings['APP_DIR']
            ),
            warn=True
        )
        if result.exited != 0:
            self.connection.run(
                'bash -c "source {}/bin/activate && '
                'pip install --upgrade pip"'.format(
                    self.settings['REMOTE_PYTHONPATH']
                )
            )
            self.connection.run(
                'bash -c "source {}/bin/activate && '
                'pip install -r {}/requirements.txt"'.format(
                    self.settings['REMOTE_PYTHONPATH'], repo_dir
                )
            )

        self.connection.run(
            'bash -c "source {REMOTE_PYTHONPATH}/bin/activate && '
            'source {REMOTE_PYTHONPATH}/bin/postactivate &&'
            '{repo_dir}/manage.py migrate"'.format(
                REMOTE_PYTHONPATH=self.settings['REMOTE_PYTHONPATH'],
                repo_dir=repo_dir
            )
        )

    def get_files(self):
        return self.files
