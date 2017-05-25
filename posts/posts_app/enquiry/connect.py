import psycopg2
import psycopg2.pool

def connectPool(connection = 7):
	if connection != 7:
		connectPool.pool.putconn(connection)
		return
	try:
		connect = connectPool.pool.getconn()
	except:
		connectPool.pool = psycopg2.pool.ThreadedConnectionPool(5, 10, dbname='poststest', user='viv', password='sunmoonmars', host='localhost', port='5432')
		connect = connectPool.pool.getconn()
	finally:
		connect.autocommit = True;
		return connect