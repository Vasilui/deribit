#!/bin/sh
# wait-for-mysql.sh

set -e

host="$1"
shift

until mysql -h "$host" -U "root" -P "123456" -c '\q'; do
  >&2 echo "MySQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "MySQL is up - executing command"
exec "$@"