#!/bin/bash

#if [ "$(whoami)" != "postgres" ]; then
#	echo "Script must be run as user postgres"
#	exit 1
#fi

#echo "Script Ok"


sudo -u postgres /usr/local/bin/psql pthier -c 'select pg_kill_all_sessions('"'"'pthier'"'"','"'"'dpdb'"'"');'
sleep 1

sudo -u postgres /usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data stop
sudo -u postgres bash -c "rm -r /run/hecher/postgres-data/*"
#sudo -u postgres rm -r /run/hecher/postgres-data/*
sudo -u postgres sudo mkdir -p /run/hecher/postgres-data
sudo -u postgres sudo chown postgres /run/hecher/postgres-data
sudo -u postgres sudo chgrp postgres /run/hecher/postgres-data
sudo -u postgres sudo chmod 700 /run/hecher/postgres-data

#sudo -u postgres mkdir /run/hecher/postgres-data
sudo -u postgres /usr/local/e192/postgres/bin/initdb -D /run/hecher/postgres-data --no-locale 
#-l #$1

#langsamer:

#/usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data start -o "--fsync=off --shared-buffers=128kB \
#    --temp-buffers=800kB --work-mem=64kB  \
#    --maintenance-work-mem=1024kB --wal-buffers=32kB \
#    --max_wal_size=64 --seq-page-cost=0.01  \
#    --random-page-cost=0.01 --effective-cache-size=64kB"

#bissl schneller:
#188
#/usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data start -o "--fsync=off \
#    --max_wal_size=64 --seq-page-cost=0.01  \
#    --random-page-cost=0.01 --autovacuum=off"

#langsamer:
#/usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data start -o "--fsync=off \
#    --seq-page-cost=0.01  \
#    --random-page-cost=0.01 --autovacuum=off"

#langsamer:
#/usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data start -o "--fsync=off --wal_level=minimal --synchronous_commit=off --archive_mode=off --max_wal_senders=0 --track_counts=off --autovacuum=off --seq-page-cost=0.01 --random-page-cost=0.01"

#langsamer:
#/usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data start -o "--fsync=off --max_wal_size=64 --wal_level=minimal --synchronous_commit=off --archive_mode=off --max_wal_senders=0 --track_counts=off --autovacuum=off --seq-page-cost=0.01 --random-page-cost=0.01"

#148
#175
#147
sudo -u postgres /usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data start -o "--fsync=off --wal_level=minimal --synchronous_commit=off --archive_mode=off --max_wal_senders=0 --track_counts=off --autovacuum=off"

#207
#207
#/usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data start -o "--fsync=off --wal_level=minimal --synchronous_commit=off --archive_mode=off --max_wal_senders=0 --track_counts=off --autovacuum=off --seq-page-cost=0.01 --random-page-cost=0.01"

#200
#/usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data start -o "--fsync=off --max_wal_size=64 --wal_level=minimal --synchronous_commit=off --archive_mode=off --max_wal_senders=0 --track_counts=off --autovacuum=off"

#156
#/usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data start -o "--fsync=off --synchronous_commit=off --archive_mode=off --track_counts=off --autovacuum=off"

#160
#/usr/local/e192/postgres/bin/pg_ctl -D /run/hecher/postgres-data start -o "--fsync=off --synchronous_commit=off --archive_mode=off --track_counts=off --autovacuum=off"


sudo -u postgres /usr/local/bin/psql postgres -c "create user pthier with password 'pthier';"
#sudo -u postgres /usr/local/e192/postgres/bin/createuser -PE pthier

echo "user Ok"

#sudo -u postgres /usr/local/e192/postgres/bin/dropdb pthier
sudo -u postgres /usr/local/e192/postgres/bin/createdb pthier

echo "db created"

sudo -u postgres /usr/local/e192/postgres/bin/psql pthier <<'EOF'
create or replace function pg_kill_all_sessions(db varchar, application varchar)
returns integer as
$$
begin
return (select count(*) from (select pg_catalog.pg_terminate_backend(pid) from pg_catalog.pg_stat_activity where pid <> pg_backend_pid() and datname = db and application_name = application) k);
end;
$$
language plpgsql security definer volatile set search_path = pg_catalog;

grant execute on function pg_kill_all_sessions(varchar,varchar) to pthier;
EOF

