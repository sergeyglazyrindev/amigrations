from operator import attrgetter
import time
from pathlib import Path
import os
import re
import importlib
import sys


def _get_all_migrations_from_folder(migration_folder):
    return sorted(Path(migration_folder).glob("*.up.sql"), key=attrgetter('name'))


def _transform_file_name_to_migration_name(name):
    return re.sub(r'\.(up|down)\.sql$', '', name)


class AMigrations(object):

    def __init__(self, db_uri, migration_folder, table_name='migrations'):
        self.db_uri = db_uri
        self.migration_folder = migration_folder
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
        for suffix in ('up', 'down'):
            _filepath = Path(self.migration_folder, base_filename.format(suffix))
            with _filepath.open('w') as fp:
                fp.write(suffix_to_messages[suffix])
            print("Added {}".format(_filepath))
            files[suffix] = _filepath
        return files

    @property
    def _adapter(self):
        adapter = self.db_uri.split(':')[0]
        return getattr(importlib.import_module(
            '.adapters.' + adapter,
            sys.modules[__name__].__package__
        ), 'Adapter')(self.db_uri, self.table_name)

    def upgrade(self):
        adapter = self._adapter
        all_migrations = _get_all_migrations_from_folder(self.migration_folder)
        applied_migrations = adapter.get_applied_migrations()
        for _migration in all_migrations:
            migration_name = _transform_file_name_to_migration_name(_migration.name)
            if migration_name in applied_migrations:
                continue
            adapter.apply(migration_name, _migration)

    def downgrade_to(self, downgrade_to):
        adapter = self._adapter
        applied_migrations = adapter.get_migrations_to_downgrade(downgrade_to)
        for _migration_to_downgrade in applied_migrations:
            migration_name, migration_id = _migration_to_downgrade
            _migration = Path(self.migration_folder, migration_name + ".down.sql")
            adapter.downgrade_migration(migration_id, _migration)
