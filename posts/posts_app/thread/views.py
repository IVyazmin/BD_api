from django.views.decorators.csrf import csrf_exempt
from json import loads
from django.db import connection
from django.http import JsonResponse
from posts_app.enquiry.enquiry import *
from posts_app.enquiry.connect import *
import psycopg2
from django.db.utils import IntegrityError, DatabaseError
import pytz, datetime
from django.utils import timezone
from random import random
from psycopg2.extras import *


@csrf_exempt
def create(request, thread_slug):
	bodies = loads(request.body.decode('utf8'))
	connect = connectPool()
	cursor = connect.cursor()
	try:
		thread_slug = int(thread_slug)
	except:
		pass
	if type(thread_slug) == int:
		cursor.execute(SELECT_THREAD_BY_SLUG_OR_ID, [thread_slug, str(thread_slug)])
	else:
		cursor.execute(SELECT_THREAD_BY_SLUG, [str(thread_slug)])
	if cursor.rowcount == 0:
		cursor.close()
		
		return JsonResponse({}, status = 404)

	thread = cursor.fetchone()
	thread_id = thread[0]
	thread_slug = thread[1]
	forum_slug = thread[2]
	param_list = []
	posts = []
	new_posts = 0
	time_now = localtime(timezone.now())

	parents = set()
	for body in bodies:
		if 'parent' in body:
			parents.add(body['parent'])
	parents = tuple(parents)
	if len(parents) > 0:
		paren = str(parents) if len(parents) > 1 else ("(" + str(tuple(parents)[0]) + ")")

		cursor.execute("select count(*) from posts where thread_id = " + str(thread_id) + " and id in " + paren +";")
		count = cursor.fetchone()
		if int(count[0]) != len(parents):
			cursor.close()
			
			return JsonResponse({}, status = 409)

	cursor.execute('select * from get_indexes()');
	ids = cursor.fetchall()


	for body in bodies:
		isEdited = body['isEdited'] if 'isEdited' in body else False
		parent = body['parent'] if 'parent' in body else None
		created = localtime(body['created']) if 'created' in body else time_now
		param_list.append(list((ids.pop(0)[0], body['author'], body['message'], isEdited, created, thread_id, forum_slug, parent)))
		new_posts += 1
		#print(body['created'] if 'created' in body else 0)
		#print(localtime(body['created']) if 'created' in body else 0)
		param_array = ['id', 'author', 'message', 'isEdited', 'created', 'thread', 'forum', 'parent']
		post = dict(zip(param_array, param_list[-1]))
		posts.append(post)
	
	cursor.execute("""Prepare posts_insert as INSERT INTO posts (id, user_nickname, message, isEdited, created, thread_id, forum_slug, parent_id)
				VALUES ($1, $2, $3, $4, $5, $6, $7, $8);""")
	try:
		execute_batch(cursor, "Execute posts_insert (%s, %s, %s, %s, %s, %s, %s, %s)", param_list)
	except: #psycopg2.Error as e:
		#print(e)
		#print(e.pgcode)
		cursor.execute("deallocate posts_insert;")
		cursor.close()
		
		return JsonResponse({}, status = 404)
		

	
	cursor.execute(PLASS_POSTS, [new_posts, forum_slug,])
	cursor.execute("deallocate posts_insert;")
	cursor.close()
	
	return JsonResponse(posts, status = 201, safe = False)


def localtime(created):
	timezone = pytz.timezone('Europe/Moscow')
	return created.astimezone(timezone)

@csrf_exempt
def vote(request, thread_slug):
	body = loads(request.body.decode('utf8'))
	user_nickname = body['nickname']
	vote = body['voice']
	connect = connectPool()
	cursor = connect.cursor()
	try:
		thread_slug = int(thread_slug)
	except:
		pass
	if type(thread_slug) == int:
		cursor.execute(SELECT_THREAD_BY_SLUG_OR_ID_ALL, [thread_slug, str(thread_slug)])
	else:
		cursor.execute(SELECT_THREAD_BY_SLUG_ALL, [str(thread_slug)])
	if cursor.rowcount == 0:
		cursor.close()
		
		return JsonResponse({}, status = 404)
	thread = cursor.fetchone()
	param_array = ['author', 'created', 'forum', 'id', 'message', 'slug', 'title', 'votes']
	thread = dict(zip(param_array, thread))
	thread_id = thread['id']
	thread['created'] = localtime(thread['created'])
	thread_slug = thread['slug']
	cursor.execute(SELECT_VOTE_BY_AUTHOR_SLUG, [user_nickname, thread_id,])
	if cursor.rowcount == 0:
		try:
			cursor.execute(INSERT_VOTE, [user_nickname, thread_id, vote])
		except:
			cursor.close()
			
			return JsonResponse({}, status = 404)
		thread['votes'] = thread['votes'] + vote
		cursor.execute(UPDATE_THREAD_VOTE, [vote, thread_id])
		cursor.close()
		
		return JsonResponse(thread, status = 200)
	else:
		vote_row = cursor.fetchone()
		if int(vote_row[2]) == int(vote):
			cursor.close()
			
			return JsonResponse(thread, status = 200)
		else:
			cursor.execute(UPDATE_VOTE, [vote, user_nickname, thread_id,])
			thread['votes'] = thread['votes'] + 2 * vote
			cursor.execute(UPDATE_THREAD_VOTE, [2 * vote, thread_id,])
			cursor.close()
			
			return JsonResponse(thread, status = 200)

@csrf_exempt
def details(request, thread_slug):
	if request.method == 'GET':
		connect = connectPool()
		cursor = connect.cursor()
		try:
			thread_slug = int(thread_slug)
		except:
			pass
		if type(thread_slug) == int:
			cursor.execute(SELECT_THREAD_BY_SLUG_OR_ID_ALL, [thread_slug, str(thread_slug)])
		else:
			cursor.execute(SELECT_THREAD_BY_SLUG_ALL, [str(thread_slug)])
		if cursor.rowcount == 0:
			cursor.close()
			
			return JsonResponse({}, status = 404)
		thread = cursor.fetchone()
		param_array = ['author', 'created', 'forum', 'id', 'message', 'slug', 'title', 'votes']
		thread = dict(zip(param_array, thread))
		thread['created'] = localtime(thread['created'])
		cursor.close()
		
		return JsonResponse(thread, status = 200)
	else:
		connect = connectPool()
		cursor = connect.cursor()
		body = loads(request.body.decode('utf8'))
		try:
			thread_slug = int(thread_slug)
		except:
			pass
		if type(thread_slug) == int:
			cursor.execute(SELECT_THREAD_BY_SLUG_OR_ID_ALL, [thread_slug, str(thread_slug)])
		else:
			cursor.execute(SELECT_THREAD_BY_SLUG_ALL, [str(thread_slug)])
		if cursor.rowcount == 0:
			cursor.close()
			
			return JsonResponse({}, status = 404)
		thread = cursor.fetchone()
		param_array = ['author', 'created', 'forum', 'id', 'message', 'slug', 'title', 'votes']
		thread = dict(zip(param_array, thread))
		author = body['author'] if 'author' in body else thread['author']
		created = body['created'] if 'created' in body else localtime(thread['created'])
		forum = body['forum'] if 'forum' in body else thread['forum']
		id = body['id'] if 'id' in body else thread['id']
		message = body['message'] if 'message' in body else thread['message']
		title = body['title'] if 'title' in body else thread['title']
		slug = body['slug'] if 'slug' in body else thread['slug']
		cursor.execute(UPDATE_THREAD, [author, created, forum, id, message, title, slug, id])
		thread = cursor.fetchone()
		thread = dict(zip(param_array, thread))
		thread['created'] = localtime(thread['created'])
		cursor.close()
	
		return JsonResponse(thread, status = 200)


@csrf_exempt
def slug_posts(request, thread_slug):
	sort = request.GET.get('sort', 'flat')
	desc = request.GET.get('desc', "false")
	limit = request.GET.get('limit', False)
	marker = request.GET.get('marker', False)
	offset = request.GET.get('offset', 0)
	connect = connectPool()
	cursor = connect.cursor()
	args = []
	if sort == 'tree':
		query = SELECT_POSTS_BY_THREAD_ID_TREE
	elif sort == 'parent_tree':
		query = SELECT_POSTS_BY_THREAD_ID_PARENT_TREE
	else:
		query = SELECT_POSTS_BY_THREAD_ID

	try:
		thread_slug = int(thread_slug)
	except:
		pass

	if type(thread_slug) == int:
		cursor.execute(SELECT_THREAD_BY_SLUG_OR_ID_ALL, [thread_slug, str(thread_slug)])
	else:
		cursor.execute(SELECT_THREAD_BY_SLUG_ALL, [str(thread_slug)])
	if cursor.rowcount == 0:
		cursor.close()
		
		return JsonResponse({}, status = 404)
	thread = cursor.fetchone()
	param_array = ['author', 'created', 'forum', 'id', 'message', 'slug', 'title', 'votes']
	thread = dict(zip(param_array, thread))
	thread_id = thread['id']
		
	args.append('\''+str(thread_id)+'\'')
	if desc == "false":
		if sort == 'flat':
			args.append('ASC')
		args.append('ASC')
	else:
		if sort == 'flat':
			args.append('DESC')
		args.append('DESC')
	
	if limit :
		args.append(str(limit))
	else:
		args.append('ALL')

	page = 0

	if marker:
		page = marking.m[marker]

	mark = str(random())

	marking(mark, int(limit) + page)
	args.append(str(page))

	if sort == "parent_tree":
		if desc == "false":
			args.append('ASC')
		else:
			args.append('DESC')

	args = tuple(args)
	query = query % args
	
	cursor.execute(query)
	
	param_array = ["id", "message", "author", "forum", "thread", "parent", "created", "isEdited"]
	all_posts = [dict(zip(param_array, row)) for row in cursor.fetchall()]
	if len(all_posts) == 0:
		mark = marker
	for post in all_posts:
		post['created'] = localtime(post['created'])

	response = {'marker': mark, 'posts': all_posts}

	cursor.close()
	
	return JsonResponse(response, status = 200)

def marking(name, page):
	try:
		marking.m[name] = page
	except:
		marking.m = {}
		marking.m[name] = page