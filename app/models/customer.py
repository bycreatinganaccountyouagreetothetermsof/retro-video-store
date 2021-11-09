from app import db
from sorcery import dict_of


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    postal_code = db.Column(db.String)
    phone = db.Column(db.String)
    registered_at = db.Column(db.DateTime)

    def to_dict(self):
        return dict_of(
            self.id,
            self.name,
            self.postal_code,
            self.phone,
            self.registered_at,
        )
