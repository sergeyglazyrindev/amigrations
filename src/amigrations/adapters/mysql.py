import MySQLdb
from .base import BaseAdapter


class Adapter(BaseAdapter):

    @property
    def _client(self):
        uri = self._uri
        conn = MySQLdb.connect(
            host=uri.host,
            user=uri.username,
            passwd=uri.password,
            db=uri.database,
            port=uri.port
        )
        conn.autocommit(True)
        return conn
