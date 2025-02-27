from app import db
from datetime import datetime


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    postal_code = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    rentals = db.relationship("Rental", back_populates="customer")

    def update(self, new_data):
        self.name = new_data["name"]
        self.postal_code = new_data["postal_code"]
        self.phone = new_data["phone"]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "postal_code": self.postal_code,
            "phone": self.phone,
            "registered_at": self.registered_at,
        }
