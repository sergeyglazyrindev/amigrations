from datetime import datetime

from ._uri import URI


class BaseAdapter(object):

    def __init__(self, db_uri, table_name):
        self.db_uri = db_uri
        self.table_name = table_name
        self._ensure_db_has_migration_table()

    @property
    def _client(self):
        raise NotImplementedError

    def _ensure_db_has_migration_table(self):
        cursor = self._client.cursor()
        cursor.execute("""
        SELECT EXISTS( SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s);
        """, [self._schema, self.table_name])
        table_exists = bool(cursor.fetchone()[0])
        if not table_exists:
            table_sql = """
            CREATE TABLE {} (
                id serial,
                name varchar(100) not null default '',
                applied_at timestamp not null default CURRENT_TIMESTAMP,
                package varchar(20) not null default 'main',
                PRIMARY KEY (id)
            )
            """.format(self.table_name)
            cursor.execute(table_sql)

    def get_applied_migrations(self):
        sql = "SELECT name FROM {}".format(self.table_name)
        cursor = self._client.cursor()
        cursor.execute(sql)
        migrations = []
        for _row in cursor.fetchall():
            migrations.append(_row[0])
        return migrations

    @property
    def _schema(self):
        return self._uri.database

    @property
    def _uri(self):
        return URI(self.db_uri)

    def apply(self, name, migration, package):
        cursor = self._client.cursor()
        with migration.open() as fp:
            cursor.execute(fp.read())
        name_splitted = name.split('_')
        applied_at = datetime.fromtimestamp(int(name_splitted[0]))
        cursor.execute("""
        INSERT INTO {} (name, applied_at, package) VALUES(%s, %s, %s)
        """.format(self.table_name), [name, applied_at.isoformat(), package])
        print("\tApplied {}".format(name))

    def get_migrations_to_downgrade(self, downgrade_to):
        sql = "SELECT name, id, package FROM {} WHERE id >= %s ORDER BY id DESC".format(self.table_name)
        cursor = self._client.cursor()
        cursor.execute(sql, [downgrade_to, ])
        migrations = []
        for _row in cursor.fetchall():
            migrations.append(_row)
        return migrations

    def downgrade_migration(self, migration_id, migration):
        cursor = self._client.cursor()
        with migration.open() as fp:
            cursor.execute(fp.read())
        cursor.execute("""
        DELETE FROM {} WHERE id = %s
        """.format(self.table_name), [int(migration_id), ])
        print("\tDowngraded migration {}".format(migration.name))
