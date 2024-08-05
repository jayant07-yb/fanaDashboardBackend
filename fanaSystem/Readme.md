Commands to run the project

```bash
set DJANGO_SETTINGS_MODULE=fanaSystem.settings
daphne -u /tmp/daphne.sock fanaSystem.asgi:application


python manage.py runserver 0.0.0.0:8000
python manage.py collectstatic
python manage.py makemigrations fanaCallSetup
python manage.py migrate
```

URLS
- http://127.0.0.1:8000/fanaCall/setup/
- http://127.0.0.1:8000/fanaDashboard/



SQL to cleanup
```bash
sqlite3 db.sqlite3
```

```sql
DELETE FROM fanaCallSetup_fanacallrequest
WHERE id NOT IN (
    SELECT MIN(id)
    FROM fanaCallSetup_fanacallrequest
    GROUP BY table_id
);
```