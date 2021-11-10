from app import db
from app.models.customer import Customer
from app.models.video import Video
from app.models.rental import Rental
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import exc
from sorcery import dict_of

customer_bp = Blueprint("customer", __name__, url_prefix="/customers")
video_bp = Blueprint("video", __name__, url_prefix="/videos")
rental_bp = Blueprint("rental", __name__, url_prefix="/rentals")

select_model = {"customer": Customer, "video": Video}
counterpart_model = {"customer": "video", "video": "customer"}


def must_include(field_name):
    return {"details": f"Request body must include {field_name}."}, 400


def page_or_all(model, sort=None, n=None, p=None):
    if sort:
        sort = getattr(model, sort)
    if n or p:
        return model.query.order_by(sort).paginate(per_page=int(n), page=int(p)).items
    return model.query.order_by(sort).all()


@customer_bp.route("", methods=["GET"])
@video_bp.route("", methods=["GET"])
def get_items():
    model = select_model[request.blueprint]
    page = page_or_all(model, **request.args)
    return jsonify([item.to_dict() for item in page])


@customer_bp.route("/<item_id>", methods=["GET", "DELETE", "PUT"])
@video_bp.route("/<item_id>", methods=["GET", "DELETE", "PUT"])
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
        for active_rental in item.rentals:
            active_rental.video.total_inventory -= 1
            db.session.delete(active_rental)
        db.session.delete(item)
        db.session.commit()
    elif request.method == "PUT":
        try:
            item.update(request.get_json())
            db.session.commit()
        except KeyError as e:
            missing_field = e.args[0]
            return must_include(missing_field)
    return (item.to_dict(), 200)


@customer_bp.route("", methods=["POST"])
@video_bp.route("", methods=["POST"])
def post_create_item():
    model = select_model[request.blueprint]
    try:
        new_item = model(**request.get_json())
        db.session.add(new_item)
        db.session.commit()
    except exc.IntegrityError as e:
        missing_field = max(e.params, key=lambda p: e.params[p] is None)
        return must_include(missing_field)
    return new_item.to_dict(), 201


@rental_bp.route("/check-out", methods=["POST"])
def check_out():
    rental_data = request.get_json()
    rental_data["due_date"] = datetime.utcnow() + timedelta(days=-7)  # last week lol
    try:
        rental_data["video"] = Video.query.get_or_404(rental_data["video_id"])
        rental_data["customer"] = Customer.query.get_or_404(rental_data["customer_id"])
        new_rental = Rental(**rental_data)
    except KeyError as e:
        missing_field = e.args[0]
        return must_include(missing_field)
    except exc.IntegrityError as e:
        missing_field = max(e.params, key=lambda p: e.params[p] is None)
        return must_include(missing_field)
    if new_rental.to_dict()["available_inventory"] < 0:
        return {"message": "Could not perform checkout"}, 400
    db.session.add(new_rental)
    db.session.commit()
    return new_rental.to_dict()


@rental_bp.route("/check-in", methods=["POST"])
def check_in():
    rental_data = request.get_json()
    try:
        video_rented = Video.query.get_or_404(rental_data["video_id"])
        customer_rented = Customer.query.get_or_404(rental_data["customer_id"])
        active_rental = Rental.query.filter_by(**rental_data, checked_in=None).first()
    except KeyError as e:
        missing_field = e.args[0]
        return must_include(missing_field)
    except exc.IntegrityError as e:
        missing_field = max(e.params, key=lambda p: e.params[p] is None)
        return must_include(missing_field)
    else:
        if not active_rental:
            return {
                "message": f"No outstanding rentals for customer {customer_rented.id} and video {video_rented.id}"
            }, 400
    active_rental.checked_in = datetime.utcnow()
    db.session.commit()
    completed_rental = active_rental.to_dict()
    return completed_rental


@customer_bp.route("<item_id>/rentals", methods=["GET"])
@video_bp.route("<item_id>/rentals", methods=["GET"])
def list_active_rentals(item_id):
    model = select_model[request.blueprint]
    try:
        item = model.query.get(item_id)
    except exc.DataError:
        return {"message": f"Invalid {request.blueprint} id"}, 400
    if not item:
        return {
            "message": f"{request.blueprint.capitalize()} {item_id} was not found"
        }, 404
    return jsonify(
        [
            getattr(rental, counterpart_model[request.blueprint]).to_dict()
            for rental in item.rentals
            if not rental.checked_in
        ]
    )


@rental_bp.route("/overdue", methods=["GET"])
def overdue_rentals():
    overdue = (
        Rental.query.filter_by(checked_in=None)
        .filter(Rental.due_date <= datetime.utcnow())
        .all()
    )
    return jsonify([rental.overdue_dict() for rental in overdue])
