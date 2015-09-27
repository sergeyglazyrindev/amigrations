Ascetic Migrations
=============

For my personal projects I'd like to use raw sql migrations. Django for example generates ugly
key names: something like: key_number

Installation
-----------

Simply run in your bash:

.. code-block:: bash
                
    python setup.py install

Usage
-----------

In your **django like manage.py** command loader, you need to trigger following:

.. code-block:: python
                
    import os
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
    # please pass timestamp which you want downgrade to. You can get it directly from db
    # select id as downgrade_to_id from migrations
    amigrations.downgrade_to(downgrade_to_id)
