from __future__ import unicode_literals
import os
from unittest import TestCase
import shutil

from amigrations import AMigrations

cur_dir = os.path.dirname(__file__)


class TestMigrations(TestCase):

    def setUp(self):
        self.migration_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "migrations"
        ))

    def create_migration_handler(
            self,
            package=None,
            supported_packages=('testpackage', 'testpackage2')
    ):
        self.amigrations = AMigrations(
            'sqlite+pysqlite:///{}'.format(
                os.path.join(self.migration_path, 'test.db')
            ),
            self.migration_path,
            current_package=package,
            supported_packages=supported_packages
        )

    def tearDown(self):
        shutil.rmtree(self.migration_path)

    @property
    def c_migrations(self):
        cursor = self.amigrations._adapter._client.cursor()
        cursor.execute("SELECT COUNT(*) FROM migrations")
        return cursor.fetchone()[0]

    def test_migrations(self):
        self.create_migration_handler()
        files = self.amigrations.create('test message1')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('''
            CREATE TABLE test
             (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL)
            ''')
            fpd.write('drop table test')
        files = self.amigrations.create('test message2')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('''
            CREATE TABLE test1
             (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL)''')
            fpd.write('drop table test1')
        self.amigrations.upgrade()
        self.assertEqual(self.c_migrations, 2)
        files = self.amigrations.create('test message3')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('''
            alter table test add column prefix
             varchar(10) not null default "";''')
            fpd.write('''
            alter table test add column prefix1
             varchar(11) not null default "";''')
        files = self.amigrations.create('test message4')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('''
            alter table test1 add column prefix
             varchar(10) not null default "";''')
            fpd.write('''
            alter table test1 add column prefix1
             varchar(11) not null default "";''')
        self.amigrations.upgrade()
        self.assertEqual(self.c_migrations, 4)
        self.amigrations.downgrade_to(3)
        self.assertEqual(self.c_migrations, 2)
        self.amigrations.downgrade_to(0)
        self.assertEqual(self.c_migrations, 0)

    def test_migrations_with_a_package(self):
        self.create_migration_handler(package='testpackage')
        files = self.amigrations.create('test message1')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('''
            CREATE TABLE test
             (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL)
            ''')
            fpd.write('drop table test')
        files = self.amigrations.create('test message2')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('''
            CREATE TABLE test1
             (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL)''')
            fpd.write('drop table test1')
        self.amigrations.upgrade()
        self.assertEqual(self.c_migrations, 2)
        files = self.amigrations.create('test message3')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('''
            alter table test add column prefix
             varchar(10) not null default "";''')
            fpd.write('''
            alter table test add column prefix1
             varchar(11) not null default "";''')
        files = self.amigrations.create('test message4')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('''
            alter table test1 add column prefix
             varchar(10) not null default "";''')
            fpd.write('''
            alter table test1 add column prefix1
             varchar(11) not null default "";''')
        self.amigrations.upgrade()
        self.assertEqual(self.c_migrations, 4)
        self.amigrations.downgrade_to(3)
        self.assertEqual(self.c_migrations, 2)
        self.amigrations.downgrade_to(0)
        self.assertEqual(self.c_migrations, 0)
