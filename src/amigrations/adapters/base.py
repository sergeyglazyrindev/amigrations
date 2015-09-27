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
        SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s AND table_name = %s;
        """, [self._uri.database, self.table_name])
        table_exists = bool(cursor.fetchone()[0])
        if not table_exists:
            table_sql = """
            CREATE TABLE {} (
                id int(11) not null AUTO_INCREMENT,
                name varchar(100) not null default '',
                applied_at timestamp not null default CURRENT_TIMESTAMP,
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
    def _uri(self):
        return URI(self.db_uri)

    def apply(self, name, migration):
        cursor = self._client.cursor()
        with migration.open() as fp:
            cursor.execute(fp.read())
        name_splitted = name.split('_')
        applied_at = datetime.fromtimestamp(int(name_splitted[0]))
        cursor.execute("""
        INSERT INTO {} (name, applied_at) VALUES(%s, %s)
        """.format(self.table_name), [name, applied_at.isoformat()])
        print("Applied {}".format(name))

    def get_migrations_to_downgrade(self, downgrade_to):
        sql = "SELECT name, id FROM {} WHERE applied_at >= %s ORDER BY id DESC".format(self.table_name)
        cursor = self._client.cursor()
        downgrade_to = datetime.fromtimestamp(int(downgrade_to))
        cursor.execute(sql, [downgrade_to.isoformat(), ])
        migrations = []
        for _row in cursor.fetchall():
            migrations.append((_row[0], _row[1]))
        return migrations

    def downgrade_migration(self, migration_id, migration):
        cursor = self._client.cursor()
        with migration.open() as fp:
            cursor.execute(fp.read())
        cursor.execute("""
        DELETE FROM {} WHERE id = %s
        """.format(self.table_name), [int(migration_id), ])
        print("Downgraded migration {}".format(migration.name))
