import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from app.auth import login_required
from app.db import get_db, get_db_cursor


bp = Blueprint('project', __name__, url_prefix='/project')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/')
def index():
    db = get_db_cursor()
    db.execute(
        'SELECT p.id, title, link, date_started, author_id, username, summary, photo, category'
        ' FROM project p JOIN "user" u ON p.author_id = u.id'
        ' ORDER BY date_started DESC'
    )
    
    projects = db.fetchall()
    return render_template('project/index.html', projects=projects)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']
        date_started = request.form['date_started']
        category = request.form['category']
        languages = request.form['languages']
        link = request.form['link']
        video = request.form['video']
        error = None

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            photo = filename

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            cur = get_db_cursor()
            cur.execute(
                'INSERT INTO project (title, summary, date_started, link, photo, category, languages, video, author_id)'
                ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (title, summary, date_started, link, photo, category, languages, video, g.user['id'])
            )
            get_db().commit()
            return redirect(url_for('project.index'))

    return render_template('project/create.html')

def get_project(id, check_author=True):
    cur = get_db_cursor()
    cur.execute(
        'SELECT p.id, title, summary, date_started, link, photo, category, languages, video, author_id, username'
        ' FROM project p JOIN "user" u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,)
    )
    
    project = cur.fetchone()

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
            cur = get_db_cursor()
            cur.execute(
                'UPDATE project SET title = %s, summary = %s, date_started = %s, link = %s'
                ' WHERE id = %s',
                (title, summary, date_started, link, id)
            )
            get_db().commit()
            return redirect(url_for('project.index'))

    return render_template('project/update.html', project=project)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    project = get_project(id)
    cur = get_db_cursor()
    cur.execute('DELETE FROM project WHERE id = %s', (id,))
    get_db().commit()
    return redirect(url_for('project.index'))

@bp.route('/<int:id>', methods=('GET', 'POST'))
def project_detail(id):
    project = get_project(id, check_author=False)
    return render_template('project/project-details.html', project=project)
