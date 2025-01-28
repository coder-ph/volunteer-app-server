from models import db
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api, Resource

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


if __name__ == '__main__':
    app.run(port=5555, debug=True)