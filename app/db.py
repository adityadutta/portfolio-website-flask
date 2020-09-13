import psycopg2
# load the psycopg extras module
import psycopg2.extras

import click
from flask import current_app, g
from flask.cli import with_appcontext

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(update_db_command)
    
def init_db():
    db = get_db()
    
    with current_app.open_resource('schema.sql') as f:
        get_db_cursor().execute(f.read().decode('utf8'))

    db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            current_app.config['DATABASE_URL'], sslmode='require'
        )

    return g.db

def get_db_cursor():
    return get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)

@click.command('update-db')
@with_appcontext
def update_db_command():
    cur = get_db_cursor()

    with current_app.open_resource('schema.sql') as f:
        cur.executescript(f.read().decode('utf8'))

    get_db().commit()
    click.echo('Updated the database.')


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


