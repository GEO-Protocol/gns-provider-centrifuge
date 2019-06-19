import os,sys
import psycopg2
from datetime import datetime

import core.service.client.interface as interface
import core.service.client.redis as redis
from core.model.client import Client
from core.settings import Settings


class Manager(interface.Manager):
    def __init__(self, settings: Settings):
        self.redis = redis.Manager(settings)

        self._conn = None
        try:
            self._conn = psycopg2.connect(
                host=settings.postgres.host,
                port=settings.postgres.port,
                database=settings.postgres.database,
                user=settings.postgres.user,
                password=settings.postgres.password
            )
            self._cur = self._conn.cursor()
            self._cur.execute(
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
            print(error)

        # client = self.create(1, "minyor")
        # self.save(client)

    def find_by_id(self, id):
        self._cur.execute(
            'SELECT * from client where id = %s', (str(id),)
        )
        results = self._cur.fetchall()
        if len(results) < 1:
            return None
        client = self._load_client(results)
        return self.redis.load(client)

    def find_by_username(self, username):
        self._cur.execute(
            'SELECT * from client where username = %s', (username,)
        )
        results = self._cur.fetchall()
        if len(results) < 1:
            return None
        client = self._load_client(results)
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
            self._cur.execute(
                "update client SET time_created=%s, secret=%s, username=%s where id=%s;",
                (client.time_created, client.secret, client.username, client.id)
            )
        else:
            self._cur.execute(
                "insert into client (id, time_created, secret, username) values (%s, %s, %s, %s);",
                (client.id, client.time_created, client.secret, client.username)
            )
        self._conn.commit()

    def delete(self, client, redis_only=False):
        self.redis.delete(client)
        if redis_only:
            return
        self._cur.execute(
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
