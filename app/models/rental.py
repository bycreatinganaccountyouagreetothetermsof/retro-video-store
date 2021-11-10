from app import db
from sqlalchemy.sql import func
from datetime import datetime


class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    customer = db.relationship("Customer", back_populates="rentals")
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"), nullable=False)
    video = db.relationship("Video", back_populates="rentals")
    due_date = db.Column(db.DateTime, nullable=False)
    checkout_date = db.Column(db.DateTime, nullable=False, server_default=func.now())
    checked_in = db.Column(db.DateTime)

    def to_dict(self, format=None):
        print(format)
        if format == "overdue":
            return {
                "video_id": self.video_id,
                "title": self.video.title,
                "customer_id": self.customer_id,
                "name": self.customer.name,
                "postal_code": self.customer.postal_code,
                "checkout_date": self.checkout_date,
                "due_date": self.due_date,
            }
        if format == "video":
            return {
                "customer_id": self.customer_id,
                "name": self.customer.name,
                "postal_code": self.customer.postal_code,
                "checkout_date": self.checkout_date,
                "due_date": self.due_date,
            }
        if format == "customer":
            return {
                "title": self.video.title,
                "checkout_date": self.checkout_date,
                "due_date": self.due_date,
            }
        active_rentals = len([r for r in self.video.rentals if not r.checked_in])
        return {
            "customer_id": self.customer_id,
            "video_id": self.video_id,
            "due_date": self.due_date,
            "videos_checked_out_count": active_rentals,
            "available_inventory": (self.video.total_inventory - active_rentals),
        }
