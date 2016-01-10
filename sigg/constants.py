from os.path import dirname
from peewee import SqliteDatabase

RESOURCES_DIR = dirname(__file__) + "/resources"
DB = SqliteDatabase(RESOURCES_DIR + "/sigg.db")
