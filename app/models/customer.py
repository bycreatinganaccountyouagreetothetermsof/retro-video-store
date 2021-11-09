from app import db
from sorcery import dict_of


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    postal_code = db.Column(db.Integer)
    phone_number = db.Column(db.String)
    registered_at = db.Column(db.DateTime)

    def to_dict(self):
        return dict_of(
            [
                self.id,
                self.name,
                self.postal_code,
                self.phone_number,
                self.registered_at,
            ]
        )
