import psycopg2
from .base import BaseAdapter


class Adapter(BaseAdapter):

    @property
    def _client(self):
        uri = self._uri
        conn = psycopg2.connect(
            host=uri.host,
            user=uri.username,
            password=uri.password,
            database=uri.database,
            port=uri.port
        )
        conn.autocommit = True
        return conn

    @property
    def _schema(self):
        return 'public'
