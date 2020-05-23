# Database Management

We use flask-sqlalchemy (which wraps sqlalchemy) to talk to the database.
We use flask-migrate (which wraps alembic) to manage database migrations.

How to make models (i.e., tables): https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/

The database migration CLI:
https://flask-migrate.readthedocs.io/en/latest/#command-reference

After creating a new model, run `flask db migrate` to create a new migration,
and `flask db upgrade` to apply the migration.
**Commit migrations to git.**

The production database is automatically upgraded in `release-tasks.sh`
