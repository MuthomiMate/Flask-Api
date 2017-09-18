import datetime

from flask_jwt import jwt

from shoppinglist import db
from flask import current_app


class AddUpdateDelete():
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()


class User(db.Model, AddUpdateDelete):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(128))
    shoppinglist = db.relationship('ShoppingList', backref='user',
                                 cascade='all,delete', passive_deletes=True)


class ShoppingList(db.Model, AddUpdateDelete):
    """
    Create shoppinglist model
    """
    __tablename__ = 'shoppinglist'
    shoppinglist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    date_modified = db.Column(db.DateTime, default=datetime.datetime.now,
                              onupdate=datetime.datetime.now)
    items = db.relationship('ShoppingListItem', backref='shoppinglist',
                            cascade='all,delete', passive_deletes=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id',
                           onupdate="CASCADE",
                           ondelete="CASCADE"), nullable=False)

    def __init__(self, name, created_by):
        self.name = name
        self.created_by = created_by


class ShoppinglistItem(db.Model, AddUpdateDelete):
    """
    Create shoppinglist item model
    """
    __tablename__ = 'shoppinglistitem'
    item_id = db.Column(db.Integer, autoincrement=True,
                        primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(300))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    date_modified = db.Column(db.DateTime, default=datetime.datetime.now,
                              onupdate=datetime.datetime.now)
    status = db.Column(db.Boolean, default=False)
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey(
                                                'shoppinglist.shoppinglist_id',
                                                onupdate="CASCADE",
                                                ondelete="CASCADE"),
                              nullable=False)

    def __init__(self, name, description, status, shoppinglist_id):
        self.name = name
        self.description = description
        self.status = status
        self.shoppinglist_id = shoppinglist_id
