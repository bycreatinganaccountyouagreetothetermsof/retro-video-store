from app import db
from sqlalchemy.sql import func
from sorcery import dict_of
from datetime import datetime


class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    customer = db.relationship("Customer", back_populates="rentals")
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"), nullable=False)
    video = db.relationship("Video", back_populates="rentals")
    due_date = db.Column(db.DateTime, nullable=False)
    checkout_date = db.Column(db.DateTime, nullable=False, server_default=func.now())

    def to_dict(self):
        return dict_of(
            self.customer_id,
            self.video_id,
            self.due_date,
            videos_checked_out_count=len(self.video.rentals),
            available_inventory=(self.video.total_inventory - len(self.video.rentals)),
        )

    def overdue_dict(self):
        return dict_of(
            self.video_id,
            self.video.title,
            self.customer_id,
            self.customer.name,
            self.customer.postal_code,
            self.checkout_date,
            self.due_date,
        )
