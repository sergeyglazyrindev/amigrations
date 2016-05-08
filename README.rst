**************************************
Ascetic Migrations
**************************************

.. image:: https://api.travis-ci.org/sergeyglazyrindev/amigrations.svg
   :target: https://travis-ci.org/sergeyglazyrindev/amigrations
   :alt: Travis CI status

.. image:: https://coveralls.io/repos/github/sergeyglazyrindev/amigrations/badge.svg?branch=master
   :target: https://coveralls.io/github/sergeyglazyrindev/amigrations?branch=master
   :alt: Coveralls status

For my personal projects I'd like to use raw sql migrations. Django for example generates ugly
key names: something like: key_number

**************************************
Installation
**************************************

Simply run in your bash:

.. code-block:: bash
                
    pip install amigrations

**************************************
Usage
**************************************

.. code-block:: python
                
    from amigratons import AMigrations

    amigrations = AMigrations('mysql://root:123456@localhost:3306/amigrations_test', path_to_folder_with_migrations)
    files_created = amigrations.create(migraiton_message)
    # files_created is a dictionary with two keys: up and down. If you want immediately update migration content, please
    # do following
    with files_created['up'].open('w') as fpu, files_created['down'].open('w') as fpd:
        fpu.write('CREATE TABLE test (id int(11) not null AUTO_INCREMENT, PRIMARY KEY(id))')
        fpd.write('drop table test')
    # run db upgrade
    amigrations.upgrade()
    # please pass migration id you want to downgrade to, including
    amigrations.downgrade_to(downgrade_to_id)
