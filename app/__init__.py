import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_sistema_evaluacion')
    app.config['TEMPLATES_AUTO_RELOAD'] = os.environ.get('TEMPLATES_AUTO_RELOAD', 'true').lower() in ('1', 'true', 'yes', 'on')
    
    # Configuracion basica para la base de datos local SQLite.
    # Nota: Flask-SQLAlchemy interpreta sqlite:///archivo.db como relativo a instance/.
    # Para instalaciones simples, normalizamos ese caso a una ruta absoluta en la raíz del proyecto.
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    database_url = os.environ.get('DATABASE_URL', '').strip()
    if not database_url or database_url == 'sqlite:///evaluaciones.db':
        database_url = 'sqlite:///' + os.path.join(basedir, 'evaluaciones.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar las extensiones
    db.init_app(app)

    # Registrar Blueprints
    from app.routes.analytics import analytics_bp
    from app.routes.master import master_bp
    from app.routes.tablet import tablet_bp
    
    app.register_blueprint(master_bp)
    app.register_blueprint(tablet_bp, url_prefix='/tablet')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')

    return app
