from app import db
from app.models.customer import Customer
from app.models.video import Video
from flask import Blueprint, jsonify, request
from datetime import datetime
from sqlalchemy import exc

customer_bp = Blueprint("customer", __name__, url_prefix="/customers")
video_bp = Blueprint("video", __name__, url_prefix="/videos")

"""
/customers endpoints:
    GET /customers
    GET /customers/<id>
    POST /customers
    PUT /customers/<id>
    DELETE /customers/<id>

[
  {
    "id": 1,
    "name": "Shelley Rocha",
    "registered_at": "Wed, 29 Apr 2015 07:54:14 -0700",
    "postal_code": 24309,
    "phone": "(322) 510-8695"
  },
  {
    "id": 2,
    "name": "Curran Stout",
    "registered_at": "Wed, 16 Apr 2014 21:40:20 -0700",
    "postal_code": 94267,
    "phone": "(908) 949-6758"
  }
]

/videos endpoints:

    GET /videos
    GET /vidoes/<id>
    POST /videos
    PUT /videos/<id>
    DELETE /videos/<id>

[
  {
    "id": 1,
    "title": "Blacksmith Of The Banished",
    "release_date": "1979-01-18",
    "total_inventory": 10
  },
  {
    "id": 2,
    "title": "Savior Of The Curse",
    "release_date": "2010-11-05",
    "total_inventory": 11
  }
]
"""


@customer_bp.route("", methods=["GET"])
def get_all_customers():
    """
    This route will return all customer records.
    ---
    responses:
        200:
            description: Successful response containing all customer records. May be empty.
    """
    return jsonify([c.to_dict() for c in Customer.query.all()])


@video_bp.route("", methods=["GET"])
def get_all_videos():
    return jsonify([v.to_dict() for v in Video.query.all()])


@customer_bp.route("/<item_id>", methods=["GET", "DELETE", "PUT"])
@video_bp.route("/<item_id>", methods=["GET", "DELETE", "PUT"])
def single_item(item_id):
    model = {"customer": Customer, "video": Video}[request.blueprint]
    try:
        item = model.query.get(item_id)
    except exc.DataError:
        return {"message": f"Invalid {request.blueprint} id"}, 400
    if not item:
        return {
            "message": f"{request.blueprint.capitalize()} {item_id} was not found"
        }, 404
    if request.method == "DELETE":
        db.session.delete(item)
        db.session.commit()
    elif request.method == "PUT":
        try:
            item.update(request.get_json())
            db.session.commit()
        except KeyError as e:
            return {"details": f"Invalid data."}, 400
    return (item.to_dict(), 200)


@customer_bp.route("", methods=["POST"])
@video_bp.route("", methods=["POST"])
def post_create_item():
    model = {"customer": Customer, "video": Video}[request.blueprint]
    try:
        new_item = model(**request.get_json())
        db.session.add(new_item)
        db.session.commit()
    except exc.IntegrityError as e:
        missing_field = max(e.params, key=lambda p: e.params[p] is None)
        return {"details": f"Request body must include {missing_field}."}, 400
    return new_item.to_dict(), 201
