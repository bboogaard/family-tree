###########
Family Tree
###########

Family Tree

.. image:: https://travis-ci.com/bboogaard/family-tree.svg?branch=master
    :target: https://travis-ci.com/bboogaard/family-tree

************
Dependencies
************

 - Python 3.6.3
 - PostgreSQL 9.6.8
 - Redis 4.0.9

************
Installation
************

Clone the repository::

    git clone https://github.com/bboogaard/family-tree.git <path-to-project>

Create database::

    createdb -U postgres family_tree

Create a virtual env::

    python3.6 -m venv (venv-dir)/family_tree

Add a postactivate file to the virtual env::

    touch (venv-dir)/family_tree/bin/postactivate

Add the following exports to the postactivate file::

    export DATABASE_URL=(database url)
    export REDIS_URL=(redis url)

    e.g.:

    export DATABASE_URL='postgresql://postgres:@/family_tree'
    export REDIS_URL='redis://127.0.0.1:6379/0'

Activate virtual env::

    source (venv-dir)/family_tree/bin/activate
    source (venv-dir)/family_tree/bin/postactivate

Go to the project path and install the requirements::

    pip install --upgrade pip
    pip install --upgrade setuptools
    pip install -r requirements_development.txt

Execute django migrations::

    ./manage.py migrate

Create a superuser::

    ./manage.py createsuperuser

Start development server::

    ./manage.py runserver 127.0.0.1:8000

Create the tree with is_admin = True in::

    http://127.0.0.1:8000/admin/tree/ancestor/

View the tree::

    http://127.0.0.1:8000/stamboom/

**********
Deployment
**********

Call deployment script for the key defined in fabfile.py::

    fab -H (host key) deploy

