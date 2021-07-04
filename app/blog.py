import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from hashlib import md5

from app.auth import login_required
from app.db import get_db, get_db_cursor

bp = Blueprint('blog', __name__, url_prefix='/blog')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img/blog')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/')
def index():
    cur = get_db_cursor()
    cur.execute(
        'SELECT p.id, title, created, author_id, username, summary, category, photo, time_to_read'
        ' FROM post p JOIN "user" u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )
    
    posts= cur.fetchall()
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
                ' VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (title, body,  summary, category, photo, time_to_read, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(title, check_author=True):
    # t = urllib.parse.unquote(title)

    cur = get_db_cursor()
    cur.execute(
        'SELECT p.id, title, body, created, author_id, username, summary, category, photo, time_to_read'
        ' FROM post p JOIN "user" u ON p.author_id = u.id'
        ' WHERE p.title = %s',
        (title,)
    )
    
    post = cur.fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

def get_post_from_id(id, check_author=True):
    # t = urllib.parse.unquote(title)

    cur = get_db_cursor()
    cur.execute(
        'SELECT p.id, title, body, created, author_id, username, summary, category, photo, time_to_read'
        ' FROM post p JOIN "user" u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,)
    )
    
    post = cur.fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<string:title>/update', methods=('GET', 'POST'))
@login_required
def update(title):
    post = get_post(title)

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
            cur = get_db_cursor()
            cur.execute(
                'UPDATE post SET title = %s, body = %s, summary = %s, category = %s, time_to_read = %s'
                ' WHERE id = %s',
                (title, body, summary, category, time_to_read, post['id'])
            )
            get_db().commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    cur = get_db_cursor()
    cur.execute('DELETE FROM post WHERE id = %s', (id,))
    get_db().commit()
    return redirect(url_for('blog.index'))

@bp.route('/<string:title>', methods=('GET', 'POST'))
def blog_detail(title):
    post = get_post(title, check_author=False)
    cur = get_db_cursor()
    cur.execute(
        ' SELECT c.id, c.created, post_id, username, email, c.body'
        ' FROM comment c JOIN post p ON c.post_id = p.id'
        ' WHERE post_id = %s ORDER BY c.created ASC',
        (post['id'],)
    )
    
    comments = cur.fetchall()

    cur.execute(
        ' SELECT p.id, title, author_id'
        ' FROM post p JOIN "user" u ON p.author_id = u.id'
        ' WHERE title != %s ORDER BY created DESC LIMIT 3',
        (post['title'],)
    )
    
    recent_posts = cur.fetchall()

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
            comm = 'INSERT INTO comment (body, username, email, post_id) VALUES (\'{}\', \'{}\', \'{}\', {})'.format(body, username, email, post['id'])
            print(comm)
            cur.execute(comm)
            get_db().commit()
            return redirect(url_for('blog.blog_detail', title=title))

    return render_template('blog/post-details.html', post=post, comments=comments, recent_posts=recent_posts)

@bp.route('/<int:post_id>/delete_comment/<int:id>', methods=('POST', 'GET'))
@login_required
def delete_comment(post_id, id):
    post = get_post_from_id(post_id)
    cur = get_db_cursor()
    cur.execute('DELETE FROM comment WHERE id = %s', (id,))
    get_db().commit()
    return redirect(url_for('blog.blog_detail', title=post['title']))