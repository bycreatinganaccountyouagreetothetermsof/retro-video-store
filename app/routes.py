from app import db
from app.models.customer import Customer
from app.models.video import Video
from app.models.rental import Rental
from flask import Blueprint, jsonify, request
from datetime import datetime
from sqlalchemy import exc

customer_bp = Blueprint("customer", __name__, url_prefix="/customers")
video_bp = Blueprint("video", __name__, url_prefix="/videos")
rental_bp = Blueprint("rental", __name__, url_prefix="/rentals")

select_model = {"customer": Customer, "video": Video, "rental": Rental}


@customer_bp.route("", methods=["GET"])
@video_bp.route("", methods=["GET"])
@rental_bp.route("", methods=["GET"])
def get_all_item():
    model = select_model[request.blueprint]
    return jsonify([item.to_dict() for item in model.query.all()])


@customer_bp.route("/<item_id>", methods=["GET", "DELETE", "PUT"])
@video_bp.route("/<item_id>", methods=["GET", "DELETE", "PUT"])
@rental_bp.route("/<item_id>", methods=["GET", "DELETE", "PUT"])
def single_item(item_id):
    model = select_model[request.blueprint]
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
            missing_field = e.args[0]
            return {"details": f"Request body must include {missing_field}."}, 400
    return (item.to_dict(), 200)


@customer_bp.route("", methods=["POST"])
@video_bp.route("", methods=["POST"])
@rental_bp.route("", methods=["POST"])
def post_create_item():
    model = select_model[request.blueprint]
    try:
        new_item = model(**request.get_json())
        db.session.add(new_item)
        db.session.commit()
    except exc.IntegrityError as e:
        missing_field = max(e.params, key=lambda p: e.params[p] is None)
        return {"details": f"Request body must include {missing_field}."}, 400
    return new_item.to_dict(), 201
