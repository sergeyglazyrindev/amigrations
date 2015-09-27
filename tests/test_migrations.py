import time
import os
from unittest import TestCase
import shutil

from src.amigrations import AMigrations


class TestMigrations(TestCase):

    def setUp(self):
        self.migration_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "migrations"
        ))
        self.amigrations = AMigrations('mysql://root:123456@localhost:3306/amigrations_test', self.migration_path)

    def tearDown(self):
        shutil.rmtree(self.migration_path)

    @property
    def c_migrations(self):
        cursor = self.amigrations._adapter._client.cursor()
        cursor.execute("SELECT COUNT(*) FROM migrations")
        return cursor.fetchone()[0]

    def test_migrations(self):
        files = self.amigrations.create('test message')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('CREATE TABLE test (id int(11) not null AUTO_INCREMENT, PRIMARY KEY(id))')
            fpd.write('drop table test')
        files = self.amigrations.create('test message1 dsadas')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('CREATE TABLE test1 (id int(11) not null AUTO_INCREMENT, PRIMARY KEY(id))')
            fpd.write('drop table test1')
        downgrade_to = int(files['up'].name.split('_')[0]) + 1
        self.amigrations.upgrade()
        self.assertEqual(self.c_migrations, 2)
        time.sleep(5)
        files = self.amigrations.create('test message')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('alter table test add column prefix varchar(10) not null default "";')
            fpd.write('alter table test drop column prefix')
        files = self.amigrations.create('test message1 dsadas')
        with files['up'].open('w') as fpu, files['down'].open('w') as fpd:
            fpu.write('alter table test1 add column prefix varchar(10) not null default "";')
            fpd.write('alter table test1 drop column prefix')
        self.amigrations.upgrade()
        self.assertEqual(self.c_migrations, 4)
        self.amigrations.downgrade_to(downgrade_to)
        self.assertEqual(self.c_migrations, 2)
        self.amigrations.downgrade_to(0)
        self.assertEqual(self.c_migrations, 0)
