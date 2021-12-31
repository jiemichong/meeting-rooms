# import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
# if os.environ.get('db_conn'):
#     uri = os.environ.get('db_conn') + '/rooms'
#     app.config['SQLALCHEMY_DATABASE_URI'] = uri
# else:
#     app.config['SQLALCHEMY_DATABASE_URI'] = None
uri = 'mysql+mysqlconnector://cs302:cs302@host.docker.internal:3306/rooms'
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 100,
                                           'pool_recycle': 280}

db = SQLAlchemy(app)

CORS(app)


class Room(db.Model):
    __tablename__ = 'rooms'

    room_id = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    floor = db.Column(db.Integer, nullable=False)

    def __init__(self, capacity, price, floor):
        self.capacity = capacity
        self.price = price
        self.floor = floor

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "capacity": self.capacity,
            "price": self.price,
            "floor": self.floor
        }

    def get_price(self):
        return {
            "price": self.price
        }


@app.route("/health")
def health_check():
    return jsonify(
        {
            "message": "Meeting Rooms service is healthy.Testing release job"
        }
    ), 200


@app.route("/rooms")
def get_all():
    rooms_list = Room.query.all()
    if len(rooms_list) != 0:
        return jsonify(
            {
                "data": {
                    "rooms": [room.to_dict() for room in rooms_list]
                }
            }
        ), 200
    return jsonify(
        {
            "message": "There are no meeting rooms."
        }
    )


@app.route("/rooms/<int:room_id>")
def find_by_id(room_id):
    room = Room.query.filter_by(room_id=room_id).first()
    if room:
        return jsonify(
            {
                "data": room.to_dict()
            }
        ), 200
    return jsonify(
        {
            "message": "Meeting room not found."
        }
    ), 404


@app.route("/rooms/<int:room_id>/price")
def find_room_price(room_id):
    room = Room.query.filter_by(room_id=room_id).first()
    if room:
        return jsonify(
            {
                "data": room.get_price()
            }
        ), 200
    return jsonify(
        {
            "message": "Meeting room not found."
        }
    ), 404


@app.route("/rooms", methods=['POST'])
def new_room():
    try:
        data = request.get_json()
        room = Room(**data)
        db.session.add(room)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred creating the room.",
                "error": str(e)
            }
        ), 500

    return jsonify(
        {
            "data": room.to_dict()
        }
    ), 201


@app.route("/rooms/<int:room_id>", methods=['PATCH'])
def update_room(room_id):
    room = Room.query.filter_by(room_id=room_id).first()
    if room is None:
        return jsonify(
            {
                "data": {
                    "room_id": room_id
                },
                "message": "Meeting room not found."
            }
        ), 404
    data = request.get_json()
    if 'capacity' in data.keys():
        room.capacity = data['capacity']
    if 'price' in data.keys():
        room.price = data['price']
    if 'floor' in data.keys():
        room.floor = data['floor']
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred in updating the room.",
                "error": str(e)
            }
        ), 500
    return jsonify(
        {
            "data": room.to_dict()
        }
    ), 200


@app.route("/rooms/<int:room_id>", methods=['DELETE'])
def delete_room(room_id):
    room = Room.query.filter_by(room_id=room_id).first()
    if room is not None:
        try:
            db.session.delete(room)
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "message": "An error occurred deleting the room.",
                    "error": str(e)
                }
            ), 500
        return jsonify(
            {
                "data": {
                    "room_id": room_id
                }
            }
        ), 200
    return jsonify(
        {
            "data": {
                "room_id": room_id
            },
            "message": "Meeting room not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
