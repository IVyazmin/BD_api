create or replace function insert_vote(t_id int, t_slug citext, u_nickname citext,_vote int, flag boolean) returns threads as
$body$
declare
	thread threads;
	vot votes;
	len int;
	old_vot int;
	e int;
	_vote2 int;
begin
select * from threads limit 1 into thread;
return thread;
	if flag = True
	Then
		create view my_v as
		SELECT * from threads where id = t_id;
	else 
		create view my_v as
		SELECT * from threads where slug = t_slug;
	end if;
	select id from my_v into t_id;
	select * from votes where thread_id = t_id and user_nickname = u_nickname into vot;
	select count(*) from vot into len;
	if len = 0
	Then 
		INSERT INTO votes (user_nickname, thread_id, vote) VALUES (u_nickname, t_id, _vote);
		UPDATE threads SET vote = vote + _vote WHERE id = t_id;
	else
		old_vot = vot[2];
		if _vote = old_vot
		Then
			SELECT 1 into e;
		else
			UPDATE votes SET vote = _vote WHERE user_nickname = u_nickname AND thread_id = t_id;
			_vote2 = _vote + _vote;
			UPDATE threads SET vote = vote + _vote2 WHERE id = t_id;
		end if;
	end if;
	SELECT * from my_v into thread;
	drop view my_v;
	return thread;
end
$body$
language plpgsql;

SELECT max_time, mean_time, total_time, query from pg_stat_statements;