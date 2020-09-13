import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from hashlib import md5

from app.auth import login_required
from app.db import get_db

bp = Blueprint('blog', __name__, url_prefix='/blog')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img/blog')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, created, author_id, username, summary, category, photo, time_to_read'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        summary = request.form['summary']
        category = request.form['category']
        time_to_read = request.form['time_to_read']

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

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body,  summary, category, photo, time_to_read, author_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (title, body,  summary, category, photo, time_to_read, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, summary, category, photo, time_to_read'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        summary = request.form['summary']
        category = request.form['category']
        time_to_read = request.form['time_to_read']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, summary = ?, category = ?, time_to_read = ?'
                ' WHERE id = ?',
                (title, body, summary, category, time_to_read, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/<int:id>', methods=('GET', 'POST'))
def blog_detail(id):
    post = get_post(id, check_author=False)
    db = get_db()
    comments = db.execute(
        ' SELECT c.id, c.created, post_id, username, email, c.body'
        ' FROM comment c JOIN post p ON c.post_id = p.id'
        ' ORDER BY c.created ASC'
    ).fetchall()

    recent_posts = db.execute(
        ' SELECT p.id, title, author_id'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE title != ? ORDER BY created DESC LIMIT 3',
        (post['title'],)
    ).fetchall()

    if request.method == 'POST':
        body = request.form['message']
        username = request.form['inputName']
        email = request.form['inputEmail1']
        email = "https://www.gravatar.com/avatar/" + md5(email.lower().encode('utf-8')).hexdigest() + "?d=identicon&s=128"
        error = None

        if not body:
            error = 'Body is required.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                 'INSERT INTO comment (body, username, email, post_id)'
                ' VALUES (?, ?, ?, ?)',
                (body, username, email, id)
            )
            db.commit()
            return redirect(url_for('blog.blog_detail', id=id))

    return render_template('blog/post-details.html', post=post, comments=comments, recent_posts=recent_posts)

@bp.route('/<int:post_id>/delete_comment/<int:id>', methods=('POST', 'GET'))
@login_required
def delete_comment(post_id, id):
    db = get_db()
    db.execute('DELETE FROM comment WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.blog_detail', id=post_id))