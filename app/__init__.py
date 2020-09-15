import os

from flask import Flask, render_template, url_for, request, redirect
from flask_mail import Mail

mail = Mail()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = os.environ['SECRET_KEY'],
        DATABASE_URL= os.environ['DATABASE_URL'],
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

    mail.init_app(app)

    #database
    from . import db
    db.init_app(app)

    #authentication
    from . import auth
    app.register_blueprint(auth.bp)

    from . import project
    app.register_blueprint(project.bp)

    from . import blog
    app.register_blueprint(blog.bp)

    from . import routes
    app.register_blueprint(routes.bp)
    app.add_url_rule('/', endpoint='index')
    app.add_url_rule('/resume', endpoint='resume')
    app.add_url_rule('/sitemap.xml', endpoint='sitemap')

    @app.route('/robots.txt/')
    def robots():
        return("User-agent: *\nDisallow: /index/\nDisallow: /login/")
    
    return app