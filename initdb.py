from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from pytz import all_timezones

# Connecting to the database and create an engine, echo will print all SQL
# queries
engine = create_engine('sqlite:///users.db', echo=True)

# Create a MetaData object and bind it to the engine
metadata = MetaData()  # 1
metadata.bind = engine

# Create a timezone_counter_table object which contains the table to be created
users_table = Table('users_table', metadata, Column(
    'id', Integer, primary_key=True), Column('user', String(50)), Column('password', String(50)))

# Actually create the table
# checkfirst=True makes sure that the table does not already exist
users_table.create(engine, checkfirst=True)
