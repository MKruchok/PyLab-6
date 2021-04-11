from flask import Flask
from flask import request
from flask import jsonify
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json
import copy


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
    class Meta:
        fields = ('name', 'write_item_type', 'customer_type', 'weight', 'price', 'ink_type', 'rating')


writing_item_schema = WritingItemSchema()
writing_items_schema = WritingItemSchema(many=True)


@app.route("/writingitem", methods=["POST"])
def add_writing_item():
    name = request.json['name']
    write_item_type = request.json['write_item_type']
    customer_type = request.json['customer_type']
    weight = request.json['weight']
    price = request.json['price']
    ink_type = request.json['ink_type']
    rating = request.json['rating']
    new_writing_item = WritingItem(name, write_item_type, customer_type, weight, price, ink_type, rating)
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
    old_writing_item = copy.deepcopy(writing_item)
    writing_item.name = request.json['name']
    writing_item.write_item_type = request.json['write_item_type']
    writing_item.customer_type = request.json['customer_type']
    writing_item.weight = request.json['weight']
    writing_item.price = request.json['price']
    writing_item.ink_type = request.json['ink_type']
    writing_item.rating = request.json['rating']
    sqla_db.session.commit()
    return writing_items_schema.jsonify(writing_item)


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
