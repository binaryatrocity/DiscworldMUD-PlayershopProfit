from datetime import datetime

from . import (
    db,
    shop
)


class ShopProduct(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    total_listed = db.Column(db.Integer)
    total_sold = db.Column(db.Integer)
    entries = db.relationship('ShopEntry', backref='product', lazy=True,
                              order_by="desc(ShopEntry.date)")

    def __repr__(self):
        return '<ShopProduct "{}">'.format(self.name)

    @property
    def latest_entry(self):
        return ShopEntry.query.filter_by(
            product_id=self.id).order_by(ShopEntry.date.desc()).first()

    @property
    def total_stocked(self):
        entries = ShopEntry.query.filter_by(product_id=self.id).order_by(
            ShopEntry.date.asc())

        last_stock = 0
        stocked_count = 0
        for entry in entries:
            diff = last_stock - entry.stock
            if diff < 0:
                stocked_count += abs(diff)
            last_stock = entry.stock
        return stocked_count

    @property
    def total_sold(self):
        entries = ShopEntry.query.filter_by(product_id=self.id).order_by(
            ShopEntry.date.asc())

        last_stock = 0
        sold_count = 0
        for entry in entries:
            diff = last_stock - entry.stock
            if diff > 0:
                sold_count += diff
            last_stock = entry.stock
        return sold_count

    @property
    def total_earned(self):
        entries = ShopEntry.query.filter_by(product_id=self.id).order_by(
            ShopEntry.date.asc())

        last_stock = 0
        earned_count = 0.00
        for entry in entries:
            diff = last_stock - entry.stock
            if diff > 0:
                earned_count += (entry.price * diff)
            last_stock = entry.stock
        return earned_count


class ShopEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock = db.Column(db.Integer, unique=False, nullable=False)
    raw_price = db.Column(db.String(20), unique=False, nullable=False)
    raw_stock = db.Column(db.String(2), unique=False, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey('shop_product.id'),
                           nullable=False)

    def __repr__(self):
        return '<ShopEntry "{}" {}>'.format(
            self.product.name,
            self.id
        )

    @property
    def stock(self):
        stock_map = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14
        }
        return stock_map[self.raw_stock]

    @property
    def price(self):
        brass = shop.convert_lancre_to_brass(self.raw_price)
        return shop.convert_brass_to_am(brass)
