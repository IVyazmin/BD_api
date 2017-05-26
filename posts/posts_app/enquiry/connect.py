import psycopg2
import psycopg2.pool

def connectPool():
	try:
		connect = connectPool.pool.getconn()
	except:
		connectPool.pool = psycopg2.pool.PersistentConnectionPool(5, 10, dbname='poststest', user='viv', password='sunmoonmars', host='localhost', port='5432')
		connect = connectPool.pool.getconn()
	finally:
		connect.autocommit = True;
		return connect