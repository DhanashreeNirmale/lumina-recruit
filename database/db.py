import sqlite3
from config.settings import DATABASE_PATH

def get_connection():
    """
    Establishes and returns a connection to the SQLite database.
    Enables Row factory for dictionaries.
    """
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    return connection
