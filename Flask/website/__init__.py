from flask import Flask
from website.page import page


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Text2AnimeTROLOLOLOLOLOLOLOLOLOLOLOLOLOLOLOO'
    app.register_blueprint(page, url_prefix='/')

    return app
