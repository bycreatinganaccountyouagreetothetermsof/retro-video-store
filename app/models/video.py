from app import db
from sorcery import dict_of


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)
    total_inventory = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return dict_of(
            self.id,
            self.title,
            self.release_date,
            self.total_inventory,
        )
