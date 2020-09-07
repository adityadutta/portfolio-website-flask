from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from app import app

@app.route("/")
def index():
    def index():
        db = app.db.get_db() 
        projects = db.execute(
            'SELECT p.id, title, link, date_started, author_id, username, summary, photo'
            ' FROM project p JOIN user u ON p.author_id = u.id'
            ' ORDER BY date_started DESC'
        ).fetchall()
    return render_template('index.html', projects=projects)