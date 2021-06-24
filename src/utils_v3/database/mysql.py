#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import os, sys
import time
import traceback


# technical
import json
import shutil
import glob


# database
import pymysql


# logger
from ..logger import getLogger
logger = getLogger(__name__)



class MySQLHelper():

    def __init__(
        self,
        host,
        port,
        db,
        user,
        passwd,
        charset='utf8',
        max_retries__total=5,
        max_retries__backoff_factor=0.5,
    ):

        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.passwd = passwd
        self.charset = charset

        self.max_retries__total=5
        self.max_retries__backoff_factor=0.5

        self.connection = self.new_connection()


    def new_connection(self):
        logger.green('## Establishing new MySQL connection...')

        for i in range(self.max_retries__total):
            try:

                Connection = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    user=self.user,
                    passwd=self.passwd,
                    charset=self.charset,
                )

                break

            except Exception as e:
                logger.warning(type(e).__name__, e)
                time.sleep(self.max_retries__backoff_factor)

        else:
            raise Exception('Cant execute given SQL query')

        Connection.autocommit(True)

        with Connection.cursor() as Cursor:
            Cursor.execute(r'SELECT VERSION()')
            db_version = Cursor.fetchone()
            logger.green('db_version:', db_version)

        return Connection


    def execute_sql(self, query, verbose=False):
        for i in range(self.max_retries__total):
            try:
                with self.connection.cursor() as Cursor:

                    if verbose:
                        logger.green('⇄ Executing SQL:\n', query)

                    Cursor.execute(query)

                    if Cursor.rowcount > 0:
                        if verbose:
                            logger.green('--> Total rows affected:', Cursor.rowcount)
                    else:
                        logger.warning('No rows affected:', query)

                    return Cursor.fetchall()

            except Exception as e:
                logger.warning(type(e).__name__, e)

                time.sleep(self.max_retries__backoff_factor)
                self.connection = self.new_connection()

        else:
            raise Exception('Cant execute given SQL query')
