from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db


bp = Blueprint('project', __name__, url_prefix='/project')

@bp.route('/')
def index():
    db = get_db()
    projects = db.execute(
        'SELECT p.id, title, link, date_started, author_id, username, summary'
        ' FROM project p JOIN user u ON p.author_id = u.id'
        ' ORDER BY date_started DESC'
    ).fetchall()
    return render_template('project/index.html', projects=projects)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']
        date_started = request.form['date_started']
        link = request.form['link']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO project (title, summary, date_started, link, author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, summary, date_started, link, g.user['id'])
            )
            db.commit()
            return redirect(url_for('project.index'))

    return render_template('project/create.html')

def get_project(id, check_author=True):
    project = get_db().execute(
        'SELECT p.id, title, summary, date_started, link, author_id, username'
        ' FROM project p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if project is None:
        abort(404, "Project id {0} doesn't exist.".format(id))

    if check_author and project['author_id'] != g.user['id']:
        abort(403)

    return project

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    project = get_project(id)

    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']
        date_started = request.form['date_started']
        link = request.form['link']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE project SET title = ?, summary = ?, date_started = ?, link = ?'
                ' WHERE id = ?',
                (title, summary, date_started, link, id)
            )
            db.commit()
            return redirect(url_for('project.index'))

    return render_template('project/update.html', project=project)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_project(id)
    db = get_db()
    db.execute('DELETE FROM project WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('project.index'))