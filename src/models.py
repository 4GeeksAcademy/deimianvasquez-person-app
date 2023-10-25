from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    lastname = db.Column(db.String(80), unique=False, nullable=True)

    def serialize(self):
        return {
            "id":self.id,
            "name":self.name,
            "lastname": self.lastname
        }
