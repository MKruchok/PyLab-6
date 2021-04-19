from flask import Flask, abort, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
import json

with open("classified.json") as f:
    PASS = json.load(f)

URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}".format(
    user = PASS["user"],
    password = PASS["password"],
    host = PASS["host"],
    port = PASS["port"],
    db = PASS["db"])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
sqla_db = SQLAlchemy(app)
marshmallow = Marshmallow(app)

class WritingItem(sqla_db.Model):
    id = sqla_db.Column(sqla_db.Integer, primary_key=True)
    name = sqla_db.Column(sqla_db.String(20), unique=False)
    write_item_type = sqla_db.Column(sqla_db.String(20), unique=False)
    customer_type = sqla_db.Column(sqla_db.String(20), unique=False)
    weight = sqla_db.Column(sqla_db.Integer, unique=False)
    price = sqla_db.Column(sqla_db.Float, unique=False)
    ink_type = sqla_db.Column(sqla_db.String(20), unique=False)
    rating = sqla_db.Column(sqla_db.Float, unique=False)

    def __init__(self, name: str, write_item_type: str,  customer_type: str, weight: int, price: float, ink_type: str, rating: float):
        self.name = name
        self.write_item_type = write_item_type
        self.customer_type = customer_type
        self.weight = weight
        self.price = price
        self.ink_type = ink_type
        self.rating = rating


class WritingItemSchema(marshmallow.Schema):
    name = fields.String()
    write_item_type = fields.String()
    customer_type = fields.String()
    weight = fields.Integer()
    price = fields.Float()
    ink_type = fields.String()
    rating = fields.Float()


writing_item_schema = WritingItemSchema()
writing_items_schema = WritingItemSchema(many=True)


@app.route("/writingitem", methods=["POST"])
def add_writing_item():
    params = writing_item_schema.load(request.json)
    new_writing_item = WritingItem(**params)
    sqla_db.session.add(new_writing_item)
    sqla_db.session.commit()
    return writing_item_schema.jsonify(new_writing_item)


@app.route("/writingitem", methods=["GET"])
def get_writing_item():
    all_writing_items = WritingItem.query.all()
    result = writing_items_schema.dump(all_writing_items)
    return jsonify({'writing_items_schema': result})


@app.route("/writingitem/<id>", methods=["GET"])
def writing_item_detail(id):
    writing_item = WritingItem.query.get(id)
    if not writing_item:
        abort(404)
    return writing_items_schema.jsonify(writing_item)


@app.route("/writingitem/<id>", methods=["PUT"])
def writing_item_update(id):
    writing_item = WritingItem.query.get(id)
    if not writing_item:
        abort(404)
    new_params = writing_item_schema.load(request.json)
    for param in new_params:
        setattr(writing_item, param, request.json[param])
    sqla_db.session.commit()


@app.route("/writingitem/<id>", methods=["DELETE"])
def writing_item_delete(id):
    writing_item = WritingItem.query.get(id)
    if not writing_item:
        abort(404)
    sqla_db.session.delete(writing_item)
    sqla_db.session.commit()
    return writing_items_schema.jsonify(writing_item)


if __name__ == '__main__':
    sqla_db.create_all()
    app.run(debug=1, host='127.0.0.1')
