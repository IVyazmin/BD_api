from django.views.decorators.csrf import csrf_exempt
from json import loads
from django.db import connection
from django.http import JsonResponse
from posts_app.enquiry.enquiry import *
import psycopg2
from django.db.utils import IntegrityError, DatabaseError
import pytz

def status(request):
	cursor = connection.cursor()
	stat = dict()
	cursor.execute(COUNT_FORUMS)
	stat['forum'] = cursor.fetchone()[0]
	cursor.execute(COUNT_POSTS)
	stat['post'] = cursor.fetchone()[0]
	cursor.execute(COUNT_THREADS)
	stat['thread'] = cursor.fetchone()[0]
	cursor.execute(COUNT_USERS)
	stat['user'] = cursor.fetchone()[0]
	cursor.close()
	return JsonResponse(stat, status = 200)

@csrf_exempt
def clear(request):
	cursor = connection.cursor()
	cursor.execute(DELETE_ALL)
	cursor.close()
	return JsonResponse({}, status = 200)