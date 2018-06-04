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
                                'passwd': 'PASSWORD'})

    # Spotify API
    ID = "CLIENT ID"
    SECRET = "SECRET CLIENT ID"
    # Genius API
    TOKEN = "TOKEN"

    LEXICON_SADNESS = [line.strip() for line in open("./lexicon/sadness.txt", 'r')]
    LEXICON_FEAR    = [line.strip() for line in open("./lexicon/fear.txt", 'r')]
    LEXICON_ANGER   = [line.strip() for line in open("./lexicon/anger.txt", 'r')]

class Config(ConfigBase): pass
