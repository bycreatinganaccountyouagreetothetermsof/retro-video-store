from app import db
from app.models.customer import Customer
from app.models.video import Video
from flask import Blueprint, jsonify, request
from datetime import datetime

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
    return [c.to_dict() for c in Customer.query.all()]


@video_bp.route("", methods=["GET"])
def get_all_videos():
    return [v.to_dict() for v in Video.query.all()]


@customer_bp.route("/<customer_id>", methods=["GET"])
def get_single_customer(customer_id):
    return Customer.query.get_or_404(customer_id).to_dict()


@video_bp.route("/<video_id>", methods=["GET"])
def get_single_video(video_id):
    return Video.query.get_or_404(video_id).to_dict()


@customer_bp.route("", methods=["POST"])
@video_bp.route("", methods=["POST"])
def post_create_item():
    model = {"customer": Customer, "video": Video}[request.blueprint]
    new_item = model(**model.validate(request.get_json()))
    db.session.add(new_item)
    db.commit()
    return new_item.to_dict()
