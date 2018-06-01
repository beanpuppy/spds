import os
from peewee import MySQLDatabase, SqliteDatabase

"""
    CHANGE PLACEHOLDER VALUES AND RENAME TO config.py
"""

class ConfigBase(object):
    """MySQL Database handler"""
    DATABASE = MySQLDatabase('DATABASE',
                             **{'charset': 'utf8',
                                'use_unicode': True,
                                'user': 'USER',
                                'passwd': 'ROOT'})

    ID = "CLIENT ID"
    SECRET = "SECRET CLIENT ID"

class Config(ConfigBase): pass
