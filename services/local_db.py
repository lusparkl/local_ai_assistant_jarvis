import sqlite3
import logging
from pathlib import Path
import config

logger = logging.getLogger(__name__)


def _connect():
    db_path = Path(config.LOCAL_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path.as_posix())


def setup_database():
    logger.info("Setting up database")
    con = _connect()
    cur = con.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS todo(id INTEGER PRIMARY KEY AUTOINCREMENT , title VARCHAR255 NOT NULL, value TEXT)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS facts(id INTEGER PRIMARY KEY AUTOINCREMENT , title VARCHAR255 NOT NULL, value TEXT)"
    )
    
    con.commit()
    con.close()

def insert_into_table(table, title, value):
    con = _connect()
    cur = con.cursor()

    cur.execute(f"INSERT INTO {table} (title, value) VALUES(?, ?)", (title, value))
    con.commit()
    con.close()

def get_table_values(table):
    con = _connect()
    cur = con.cursor()

    cur.execute(f"SELECT * FROM {table}")
    output = cur.fetchall()
    con.close()

    return output

def delete_table_value(table, id):
    con = _connect()
    cur = con.cursor()

    cur.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
    
    con.commit()
    con.close()
