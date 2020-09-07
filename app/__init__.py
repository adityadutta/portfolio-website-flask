import os

from flask import Flask, render_template, url_for, request, redirect
from flask_mail import Mail, Message


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = os.environ['SECRET_KEY'],
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        MAIL_SERVER = os.environ['MAIL_SERVER'],
        MAIL_PORT = os.environ['MAIL_PORT'],
        MAIL_USERNAME = os.environ['MAIL_USERNAME'],
        MAIL_PASSWORD = os.environ['MAIL_PASSWORD'],
        MAIL_USE_TLS = False,
        MAIL_USE_SSL = True,
        GA_TRACKING_ID = os.environ['GA_TRACKING_ID'],
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    mail = Mail()
    mail.init_app(app)

    #database
    from . import db
    db.init_app(app)

    #authentication
    from . import auth
    app.register_blueprint(auth.bp)

    from . import project
    app.register_blueprint(project.bp)

    # index landing page
    from .db import get_db
    from .contact import contact
    @app.route('/', methods=['POST', 'GET'])
    def index():
        message = {}
        if request.method == 'POST':  
            message['name'] = request.form['name']
            message['email'] = request.form['email']
            message['subject'] = request.form['subject']
            message['message'] = request.form['message'] + "\n\n Sender: " + message['email']

            send_message(message)
            return redirect(url_for('index'))   

        db = get_db() 
        projects = db.execute(
            'SELECT p.id, title, link, date_started, author_id, username, summary, photo, category'
            ' FROM project p JOIN user u ON p.author_id = u.id'
            ' ORDER BY date_started DESC'
        ).fetchall()
        return render_template('index.html', projects=projects)
    
    def send_message(message):
        msg = Message(message.get('subject'), sender = message.get('email'),
                recipients = [app.config['MAIL_USERNAME']],
                body= message.get('message')
        )  

        mail.send(msg)

    return app