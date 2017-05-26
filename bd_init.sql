drop table if exists votes ;
drop table if exists posts;
drop table if exists threads;
drop table if exists forums;
drop table if exists users;
drop sequence if exists posts_id_seq;

CREATE EXTENSION IF NOT EXISTS CITEXT;

SET SYNCHRONOUS_COMMIT = 'off';


create sequence posts_id_seq
start with 1
increment by 1
no minvalue
no maxvalue;

create table users (
about text,
email citext collate ucs_basic,
fullname varchar(100),
nickname citext collate ucs_basic constraint firstkey_u PRIMARY KEY,
constraint uniq_email unique(email)
);

create table forums (
slug citext collate ucs_basic constraint firstkey_f PRIMARY KEY,
title varchar(100),
user_nickname citext collate ucs_basic references users (nickname) on delete cascade,
threads integer default 0,
posts integer default 0);

create table threads (
id serial constraint firstkey_t PRIMARY KEY,
user_nickname citext collate ucs_basic references users (nickname) on delete cascade,
title varchar(100),
slug citext collate ucs_basic unique,
created timestamp with time zone,
forum_slug citext collate ucs_basic references forums (slug) on delete cascade,
message text,
vote int DEFAULT 0);

create table posts (
id int default NEXTVAL('posts_id_seq') constraint firstkey_p PRIMARY KEY,
message text,
user_nickname citext collate ucs_basic references users (nickname) on delete cascade,
forum_slug citext collate ucs_basic references forums (slug),
thread_id int references threads (id) on delete cascade,
parent_id int references posts (id) default NULL,
created timestamp with time zone,
isEdited boolean default False);

create table votes (
user_nickname citext collate ucs_basic references users (nickname) on delete cascade,
thread_id int references threads (id) on delete cascade,
vote smallint,
PRIMARY KEY (user_nickname, thread_id));

create table forum_users (
user_nickname citext collate ucs_basic references users (nickname) on delete cascade,
forum citext collate ucs_basic references forums (slug) on delete cascade,
PRIMARY KEY (forum, user_nickname));

create INDEX idx_users_nickname on users using btree (nickname text_pattern_ops);
create INDEX idx_users_email on users using btree (email text_pattern_ops);
create INDEX idx_forums_slug on forums using btree (slug text_pattern_ops);
create INDEX idx_forums_nickname on forums using btree (user_nickname text_pattern_ops);
create INDEX idx_threads_id on threads using btree (id);
create INDEX idx_threads_nickname on threads using btree (user_nickname text_pattern_ops);
create INDEX idx_threads_slug on threads using btree (slug text_pattern_ops);
create INDEX idx_threads_forum on threads using btree (forum_slug text_pattern_ops);
create INDEX idx_posts_id on posts using btree (id);
create INDEX idx_posts_nickname on posts using btree (user_nickname text_pattern_ops);
create INDEX idx_posts_forum on posts using btree (forum_slug text_pattern_ops);
create INDEX idx_posts_thread on posts using btree (thread_id);
create INDEX idx_votes_nickname_thread on votes using btree (user_nickname text_pattern_ops, thread_id);
create INDEX idx_votes_thread on votes using btree (thread_id);
create INDEX idx_forumusers_forum on forum_users using btree (forum);
create INDEX idx_forumusers_user on forum_users using btree (user_nickname);

create or replace function get_indexes() returns setof int as
$body$
declare
	i int;
	current_id int;
begin
	i = 0;
	while i < 100
	loop
		SELECT NEXTVAL('posts_id_seq') into current_id;
		return next current_id;
		i = i + 1;
	end loop;
	return;
end
$body$
language plpgsql;