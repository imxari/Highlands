""" Imports """
import ConfigParser
import os
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
import sqlalchemy as db

""" Initiate ConfigParser and load INI file """
Config = ConfigParser.ConfigParser()
Config.read("/app/public/highlands.ini")

username=Config.get('mysql','username')
password=Config.get('mysql','password')
hostname=Config.get('mysql','hostname')
database=Config.get('mysql','database')

""" Connect to the MySQL database """
connectionString="mysql://"+username+":"+password+"@"+hostname+"/"+database
engine = create_engine(connectionString)

Base = declarative_base()

""" Connect to the database and get a blank metadata """
engine.connect()
metadata = db.MetaData()

""" Define the structure of the tables """
users = db.Table('users', metadata,
                Column('id', Integer(), primary_key=True),
		Column('username', String(75)),
		Column('password', String(75)),
		Column('firstname', String(75)),
		Column('lastname', String(75)),
		Column('email', String(100)))

""" Create the tables """
metadata.create_all(engine)
