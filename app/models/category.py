import datetime
from app import db

_utcnow = lambda: datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(64), nullable=False, index=True)

    description = db.Column(db.String(255), nullable=True)

    color = db.Column(db.String(7), nullable=True, default="#6C757D")

    icon = db.Column(db.String(32), nullable=True, default="")

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    is_default = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False,
                           default=_utcnow)

    transactions = db.relationship("Transaction", backref="category_ref",
                                   lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "name":        self.name,
            "description": self.description,
            "color":       self.color,
            "icon":        self.icon,
            "is_default":  self.is_default,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Category {self.name}>"
