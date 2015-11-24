import time
from pathlib import Path
import os
import re
import importlib
import sys


def _get_all_migrations_from_folder(migration_folder):
    return Path(migration_folder).glob("*.up.sql")


def _transform_file_name_to_migration_name(name):
    return re.sub(r'\.(up|down)\.sql$', '', name)


class AMigrations(object):

    def __init__(self, db_uri, migration_folder, current_package=None,
                 table_name='migrations', supported_packages=()):
        self.db_uri = db_uri
        self.migration_folder = migration_folder
        self.current_package = current_package if current_package in supported_packages else None
        self.supported_packages = supported_packages
        if not os.path.exists(migration_folder):
            os.makedirs(migration_folder)
        self.table_name = table_name

    def create(self, message):
        timestamp = str(int(time.time()))
        s_message = re.sub(r'\s', '_', message[:30])
        base_filename = timestamp + "_" + s_message + ".{}.sql"
        suffix_to_messages = {
            'up': "/**Up migration\n{}**/".format(message),
            'down': "/**Down migration\n{}**/".format(message)
        }
        files = {}
        migration_folder = self.migration_folder
        if self.current_package:
            migration_folder += "/" + self.current_package + "/"
        for suffix in ('up', 'down'):
            _filepath = Path(migration_folder, base_filename.format(suffix))
            with _filepath.open('w') as fp:
                fp.write(suffix_to_messages[suffix])
            print("Added {}".format(_filepath))
            files[suffix] = _filepath
        return files

    @property
    def _adapter(self):
        adapter = self.db_uri.split(':')[0].split('+')[0]
        return getattr(importlib.import_module(
            '.adapters.' + adapter,
            sys.modules[__name__].__package__
        ), 'Adapter')(self.db_uri, self.table_name)

    def upgrade(self):
        adapter = self._adapter
        migrations = _get_all_migrations_from_folder(self.migration_folder)
        all_migrations = {migration.name: {
            'package': 'main',
            'migration': migration
        } for migration in migrations}
        if self.supported_packages:
            for package in self.supported_packages:
                package_migrations = _get_all_migrations_from_folder(self.migration_folder + "/" + package + "/")
                all_migrations.update({
                    migration.name: {
                        'package': package,
                        'migration': migration
                    } for migration in package_migrations
                })

        sorted_migrations = sorted(all_migrations.keys())
        applied_migrations = adapter.get_applied_migrations()
        for _migration in sorted_migrations:
            migration_name = _transform_file_name_to_migration_name(_migration)
            if migration_name in applied_migrations:
                continue
            migration_data = all_migrations[_migration]
            adapter.apply(migration_name, migration_data['migration'], migration_data['package'])

    def downgrade_to(self, downgrade_to):
        adapter = self._adapter
        applied_migrations = adapter.get_migrations_to_downgrade(downgrade_to)
        for _migration_to_downgrade in applied_migrations:
            migration_name, migration_id, package = _migration_to_downgrade
            migration_folder = self.migration_folder
            if package != 'main' and package in self.supported_packages:
                migration_folder += "/" + package + "/"
            _migration = Path(migration_folder, migration_name + ".down.sql")
            adapter.downgrade_migration(migration_id, _migration)
