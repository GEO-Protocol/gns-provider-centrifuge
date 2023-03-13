import os,sys
import psycopg2
from datetime import datetime

import core.service.client.interface as interface
import core.service.client.redis as redis
from core.model.client import Client
from core.settings import Settings


class Manager(interface.Manager):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis = redis.Manager(settings)

        self._conn = None
        self._cur = None
        self.connect()
        try:
            self.execute(
                """
                CREATE TABLE IF NOT EXISTS client (
                    id SERIAL PRIMARY KEY,
                    time_created timestamp without time zone,
                    secret character varying(255),
                    username text
                )
                """)
            self._conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self._conn = None
            self.debug(error)

        # client = self.create(1, "minyor")
        # self.save(client)

    def debug(self, str):
        if self.settings.is_in_debug():
            self.settings.logger.debug(str)

    def error(self, str) :
        self.settings.logger.error(str)

    def connect(self):
        try:
            self._conn = psycopg2.connect(
                host=self.settings.postgres.host,
                port=self.settings.postgres.port,
                database=self.settings.postgres.database,
                user=self.settings.postgres.user,
                password=self.settings.postgres.password
            )
            self._cur = self._conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            self._conn = None
            self.debug(error)

    def execute(self, query, params=None):
        cnt_attempts = 1
        while True:
            try:
                return self._cur.execute(query, params)
            #except psycopg2.OperationalError:
            except Exception as error:
                cnt_attempts = cnt_attempts + 1
                self.error("execute")
                self.error(error)
                if cnt_attempts > 3:
                    return None
                self.error("Reestablishing connection to the database...")
                self.connect()

    def fetchall(self, query, params=None):
        cnt_attempts = 1
        while True:
            try:
                self._cur.execute(query, params)
                return self._cur.fetchall()
            #except psycopg2.OperationalError:
            except Exception as error:
                cnt_attempts = cnt_attempts + 1
                self.error("fetchall error")
                self.error(error)
                if cnt_attempts > 3:
                    return None
                self.error("Reestablishing connection to the database...")
                self.connect()

    def find_by_id(self, id):
        results = self.fetchall('SELECT * from client where id = %s', (str(id),))
        if not results:
            return None
        if len(results) < 1:
            return None
        client = self._load_client(results)
        return self.redis.load(client)

    def find_by_username(self, username):
        # self.error("find_by_username " + username)
        results = self.fetchall('SELECT * from client where username = %s', (username,))
        if not results:
            # self.error("find_by_username " + username + " not results")
            return None
        if len(results) < 1:
            self.error("find_by_username " + username + " wrong results")
            return None
        self.debug("find_by_username " + username + " results: " + ', '.join(map(str, results[0])))
        client = self._load_client(results)
        if client.username != username:
            return None
        return self.redis.load(client)

    def create(self, id, username):
        client = Client(id, username)
        client.time_created = datetime.now()
        return client

    def save(self, client, redis_only=False):
        self.redis.save(client)
        if redis_only:
            return
        existing_client = self.find_by_id(client.id)
        if existing_client:
            self.execute(
                "update client SET time_created=%s, secret=%s, username=%s where id=%s;",
                (client.time_created, client.secret, client.username, client.id)
            )
        else:
            self.execute(
                "insert into client (id, time_created, secret, username) values (%s, %s, %s, %s);",
                (client.id, client.time_created, client.secret, client.username)
            )
        self._conn.commit()

    def delete(self, client, redis_only=False):
        self.redis.delete(client)
        if redis_only:
            return
        self.execute(
            "delete from client where id=%s;",
            (client.id,)
        )
        self._conn.commit()

    @staticmethod
    def _load_client(results):
        client = Client()
        client.id = int(results[0][0])
        client.time_created = results[0][1]
        client.secret = None if results[0][2] == "NULL" else results[0][2]
        client.username = results[0][3]
        return client
