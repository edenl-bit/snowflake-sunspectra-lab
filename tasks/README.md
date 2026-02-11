# Tasks (duplicate from Snowflake)

This folder holds **exported** Snowflake Task DDL so you can duplicate the same tasks elsewhere.

**Export** (from the Snowflake that has the tasks):

```bash
# .env pointed at source database
python export_tasks_from_snowflake.py
```

That writes `tasks/tasks.sql` (one CREATE TASK per task in the database).

**Duplicate** (in the same or another Snowflake):

```bash
# .env pointed at target database/schema if needed
python generate_tasks.py
```

`generate_tasks.py` runs `tasks/tasks.sql` if it exists, so the same tasks are created in the target environment.
