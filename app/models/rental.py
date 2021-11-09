from app import db
from sorcery import dict_of
from datetime import datetime


class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    customer = db.relationship("Customer", back_populates="customer")
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"))
    video = db.relationship("Video", back_populates="video")
    due_date = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return dict_of(
            self.customer_id,
            self.video_id,
            self.due_date,
            videos_checked_out_count=len(self.video.rentals),
            available_inventory=(self.video.total_inventory - len(self.video.rentals)),
        )
