import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, make_response
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from hashlib import md5

from urllib.parse import quote

from app.auth import login_required
from app.db import get_db, get_db_cursor
from flask_mail import Mail, Message
from _datetime import datetime, timedelta

bp = Blueprint('routes', __name__,)

@bp.route('/', methods=['POST', 'GET'])
def index():
    message = {}
    if request.method == 'POST':  
        message['name'] = request.form['name']
        message['email'] = request.form['email']
        message['subject'] = request.form['subject']
        message['message'] = request.form['message'] + "\n\n Sender: " + message['email']
        send_message(message)
        return redirect(url_for('index'))   
    cur = get_db_cursor()
    cur.execute(
        'SELECT p.id, title, link, date_started, author_id, username, summary, photo, category'
        ' FROM project p JOIN "user" u ON p.author_id = u.id'
        ' ORDER BY date_started DESC LIMIT 6'
    )
    projects = cur.fetchall()

    cur.execute(
        'SELECT p.id, title, created, author_id, username, summary, category, photo, time_to_read'
        ' FROM post p JOIN "user" u ON p.author_id = u.id'
        ' ORDER BY created DESC LIMIT 3'
    )
    posts = cur.fetchall()
    
    return render_template('index.html', projects=projects, posts=posts)

def send_message(message):
    msg = Message(message.get('subject'), sender = message.get('email'),
            recipients = [current_app.config['MAIL_USERNAME']],
            body= message.get('message')
    )  
    current_app.mail.send(msg)

@bp.route('/resume')
def resume():
    resume_link = "https://docs.google.com/document/d/e/2PACX-1vSFvWsauLPiP6T-I32weOqKp4cyR6NyraGskcxtd083IZOpKeoarbR5sqJsBDxwfb6JV-Lm-ih5dbz1/pub?embedded=true"
    return render_template('resume.html', resume_link = resume_link)


@bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    try:
      """Generate sitemap.xml. Makes a list of urls and date modified."""
      pages=[]
      ten_days_ago=(datetime.now() - timedelta(days=7)).date().isoformat()
      # static pages
      for rule in current_app.url_map.iter_rules():
          if "GET" in rule.methods and len(rule.arguments)==0:
              pages.append(
                           ["http://adityadutta.herokuapp.com"+str(rule.rule),ten_days_ago]
                           )
        
      cur = get_db_cursor()
      cur.execute(
          ' SELECT title'
          ' FROM project'
      )
      projects = cur.fetchall()
      for project in projects:
            pages.append(
                         ["http://adityadutta.herokuapp.com/project/"+quote(project['title']),ten_days_ago]
                         )

      cur.execute(
          'SELECT title'
          ' FROM post '
      )
      posts = cur.fetchall()
      for post in posts:
            pages.append(
                         ["http://adityadutta.herokuapp.com/blog/"+quote(post['title']),ten_days_ago]
                         )

      sitemap_xml = render_template('sitemap_template.xml', pages=pages)
      response= make_response(sitemap_xml)
      response.headers["Content-Type"] = "application/xml"    
    
      return response
    except Exception as e:
        return(str(e))	


