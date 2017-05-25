from django.views.decorators.csrf import csrf_exempt
from json import loads
from django.db import connection
from django.http import JsonResponse
from posts_app.enquiry.enquiry import *
from posts_app.enquiry.connect import *
import psycopg2
from django.db.utils import IntegrityError, DatabaseError
import pytz

@csrf_exempt
def details(request, post_id):
	if request.method == 'GET':
		related = request.GET.get('related', False)
		related = related.split(',') if related else []
		connect = connectPool()
		cursor = connect.cursor()
		cursor.execute(SELECT_POST_BY_ID, [post_id,])
		if cursor.rowcount == 0:
			cursor.close()
			connectPool(connect)
			return JsonResponse({}, status = 404)
		param_array = ["id", "message", "author", "forum", "thread", "parent", "created", "isEdited"]
		post = dict(zip(param_array, cursor.fetchone()))
		post['created'] = localtime(post['created'])
		post_all = dict()
		post_all['post'] = post
		if 'user' in related:
			cursor.execute(SELECT_USER_BY_NICKNAME, [post['author'],])
			param_array = ["about", "email", "fullname", "nickname"]
			author = dict(zip(param_array, cursor.fetchone()))
			post_all['author'] = author
		if 'forum' in related:
			cursor.execute(SELECT_FORUM_BY_SLUG, [post['forum'],])
			param_array = ["posts", "slug", "threads", "title", "user"]
			forum = dict(zip(param_array, cursor.fetchone()))
			post_all['forum'] = forum
		if 'thread' in related:
			cursor.execute(SELECT_THREAD_BY_ID_ALL, [post['thread'],])
			param_array = ['author', 'created', 'forum', 'id', 'message', 'slug', 'title', 'votes']
			thread = dict(zip(param_array, cursor.fetchone()))
			thread['created'] = localtime(thread['created'])
			post_all['thread'] = thread
		cursor.close()
		connectPool(connect)
		return JsonResponse(post_all, status = 200)
	else:
		body = loads(request.body.decode('utf8'))
		message = body['message'] if 'message' in body else False
		connect = connectPool()
		cursor = connect.cursor()
		cursor.execute(SELECT_POST_BY_ID, [post_id,])
		if cursor.rowcount == 0:
			cursor.close()
			connectPool(connect)
			return JsonResponse({}, status = 404)
		param_array = ["id", "message", "author", "forum", "thread", "parent", "created", "isEdited"]
		post = dict(zip(param_array, cursor.fetchone()))
		if message and (message != post['message']):
			cursor.execute(UPDATE_POST, [message, post_id,])
			post['isEdited'] = True
			post['message'] = message
		post['created'] = localtime(post['created'])
		cursor.close()
		connectPool(connect)
		return JsonResponse(post, status = 200)



def localtime(created):
	timezone = pytz.timezone('Europe/Moscow')
	return created.astimezone(timezone)
