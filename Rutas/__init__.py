import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient

from Rutas.routes import pages

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
    )
    
    # Intentar conectar a MongoDB solo si la URI está configurada
    if app.config["MONGODB_URI"]:
        try:
            app.db = MongoClient(app.config["MONGODB_URI"]).get_default_database()
        except Exception as e:
            print(f"Error conectando a MongoDB: {e}")
            app.db = None
    else:
        app.db = None

    app.register_blueprint(pages)
    return app
