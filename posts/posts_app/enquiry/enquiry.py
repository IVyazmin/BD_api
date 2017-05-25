INSERT_USER = '''INSERT INTO users (about, email, fullname, nickname)
				VALUES (%s, %s, %s, %s);'''

SELECT_USERS_BY_EMAIL_OR_NICKNAME = '''SELECT about, email, fullname, nickname FROM users
										WHERE email = %s OR nickname = %s;'''

SELECT_USER_BY_NICKNAME = '''SELECT about, email, fullname, nickname FROM users
							WHERE nickname = %s;'''

UPDATE_USER = '''UPDATE users SET about = %s, email = %s, fullname = %s
				WHERE nickname = %s'''

INSERT_FORUM = '''INSERT INTO forums (slug, title, user_nickname)
				VALUES (%s, %s, %s);'''

SELECT_FORUM_BY_SLUG = '''SELECT posts, slug, threads, title, user_nickname FROM forums
						WHERE slug = %s;'''

INSERT_THREAD = '''INSERT INTO threads (user_nickname, created, forum_slug, message, slug, title)
				VALUES (%s, %s, %s, %s, %s, %s)
				RETURNING id;'''

INSERT_THREAD_NOW = '''INSERT INTO threads (user_nickname, created, forum_slug, message, slug, title)
				VALUES (%s, now(), %s, %s, %s, %s)
				RETURNING id;'''

SELECT_THREAD_BY_SLUG_ALL = '''SELECT user_nickname, created, forum_slug, id, message, slug, title, vote FROM threads
						WHERE slug = %s;'''

SELECT_THREAD_BY_SLUG_OR_ID_ALL = '''SELECT user_nickname, created, forum_slug, id, message, slug, title, vote FROM threads
						WHERE id = %s OR slug = %s;'''

SELECT_THREAD_BY_ID_ALL = '''SELECT user_nickname, created, forum_slug, id, message, slug, title, vote FROM threads
						WHERE id = %s;'''

SELECT_FORUM_BY_SLUG = '''SELECT posts, slug, threads, title, user_nickname FROM forums
						WHERE slug = %s;'''

SELECT_THREADS_BY_FORUM = '''SELECT user_nickname, created, forum_slug, id, message, slug, title, vote FROM threads
						WHERE forum_slug = %s %s
						ORDER BY created %s
						LIMIT %s;'''

INSERT_POST_NOW = '''INSERT INTO posts (user_nickname, message, isEdited, created, thread_id, forum_slug, parent_id)
				VALUES (%s, %s, %s, now(), %s, %s, %s)
				RETURNING id, created;'''

INSERT_POST = '''INSERT INTO posts (user_nickname, message, isEdited, created, thread_id, forum_slug, parent_id)
				VALUES (%s, %s, %s, %s, %s, %s, %s)
				RETURNING id, created;'''

SELECT_THREAD_BY_SLUG_OR_ID = '''SELECT id, slug, forum_slug FROM threads
								WHERE id = %s OR slug = %s;'''

SELECT_THREAD_BY_SLUG = '''SELECT id, slug, forum_slug FROM threads
								WHERE slug = %s;'''

SELECT_THREAD_BY_ID = '''SELECT id, slug, forum_slug FROM threads
								WHERE id = %s;'''

SELECT_VOTE_BY_AUTHOR_SLUG = '''SELECT user_nickname, thread_id, vote FROM votes
								WHERE user_nickname = %s AND thread_id = %s;'''

INSERT_VOTE = '''INSERT INTO votes (user_nickname, thread_id, vote)
				VALUES (%s, %s, %s)'''

UPDATE_THREAD_VOTE = '''UPDATE threads SET vote = vote + %s
						WHERE id = %s'''

UPDATE_VOTE = '''UPDATE votes SET vote = %s
				WHERE user_nickname = %s AND thread_id = %s'''

SELECT_POSTS_BY_THREAD_ID = '''
			SELECT id, message, user_nickname, forum_slug, thread_id, parent_id, created, isEdited FROM "posts"
			WHERE thread_id = %s
			ORDER BY created %s, "id" %s
			LIMIT %s OFFSET %s
		'''

SELECT_POSTS_BY_THREAD_ID_TREE = '''
			WITH RECURSIVE recursetree (id, message, author, forum, thread, parent, created, isEdited, path) AS (
					SELECT posts.*, array_append('{}'::int[], id) FROM posts
					WHERE parent_id IS NULL
						AND thread_id = %s
				UNION ALL
					SELECT p.*, array_append(path, p.id)
					FROM posts AS p
					JOIN recursetree rt ON rt.id = p.parent_id
			)
			SELECT rt.*, array_to_string(path, '.') as path1 
			FROM recursetree AS rt
			ORDER BY path %s
			LIMIT %s OFFSET %s
		'''

SELECT_POSTS_BY_THREAD_ID_PARENT_TREE = '''
			WITH RECURSIVE recursetree (id, message, author, forum, thread, parent, created, isEdited, path) AS (
					(SELECT posts.*, array_append('{}'::int[], id) FROM posts
					WHERE parent_id IS NULL AND
					thread_id = %s
					ORDER BY "id" %s
					LIMIT %s OFFSET %s)
				UNION ALL
					SELECT p.*, array_append(path, p.id)
					FROM posts AS p
					JOIN recursetree rt ON rt.id = p.parent_id
			)
			SELECT rt.*, array_to_string(path, '.') as path1 
			FROM recursetree AS rt
			ORDER BY path %s
		'''


UPDATE_THREAD = '''UPDATE threads SET user_nickname = %s, created = %s, forum_slug = %s, id = %s, message = %s, title = %s, slug = %s
				WHERE id = %s
				RETURNING user_nickname, created, forum_slug, id, message, slug, title, vote;'''

PLASS_THREAD = '''UPDATE forums SET threads = threads + 1
				WHERE slug = %s;'''

PLASS_POSTS = '''UPDATE forums SET posts = posts + %s
				WHERE slug = %s;'''

SELECT_USERS_BY_FORUM = '''SELECT about, email, fullname, nickname FROM users
								%s nickname IN 
								(SELECT user_nickname FROM threads 
								WHERE forum_slug = %s
								UNION
								SELECT user_nickname FROM posts
								WHERE forum_slug = %s)
								ORDER BY nickname %s
								%s;'''


SELECT_POST_BY_ID = '''SELECT "id", "message", "user_nickname", "forum_slug", "thread_id", "parent_id", "created", "isedited" from posts
						WHERE id = %s;'''

UPDATE_POST = '''UPDATE posts SET message = %s, isedited = True
				WHERE id = %s;'''

COUNT_FORUMS = '''SELECT COUNT(*) from forums;'''

COUNT_THREADS = '''SELECT COUNT(*) from threads;'''

COUNT_USERS = '''SELECT COUNT(*) from users;'''

COUNT_POSTS = '''SELECT COUNT(*) from posts;'''

DELETE_ALL = '''TRUNCATE votes CASCADE;
				TRUNCATE posts CASCADE;
				TRUNCATE threads CASCADE;
				TRUNCATE forums CASCADE;
				TRUNCATE users CASCADE;'''