import threading
import telebot
import check_work
import datetime
import time
import psycopg2
url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port
global db
global sql
global user_id
db = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
sql=db.cursor()

def block_work(user_id):
    sql.execute(f"UPDATE players SET job_blocked = 'unblocked' WHERE chatid = '{user_id}'")
    db.commit()