import re

from . import (
    db,
    models
)


def convert_lancre_to_brass(raw_price):
    coins = {
        'penny': 0,
        'shilling': 0,
        'crown': 0,
        'sovereign': 0,
        'hedgehog': 0
    }

    def noz(num):
        if num and num is not '-':
            return int(num)
        return 0

    # Figure out which special notation we have
    if "LC" in raw_price:
        pattern = r'^LC (\d+)\|(\d+|-)\|(\d+|-)$'
        match = re.match(pattern, raw_price)
        groups = match.groups()

        coins['penny'] = noz(groups[2])
        coins['shilling'] = noz(groups[1])
        coins['crown'] = noz(groups[0])
    elif "LSov" in raw_price:
        pattern = r'^LSov (\d+)\|(\d+|-)\|(\d+|-)\|(\d+|-)$'
        match = re.match(pattern, raw_price)
        groups = match.groups()

        coins['penny'] = noz(groups[3])
        coins['shilling'] = noz(groups[2])
        coins['crown'] = noz(groups[1])
        coins['sovereign'] = noz(groups[0])
    elif "LH" in raw_price:
        pattern = r'^LH (\d+)\|(\d+|-)\|(\d+|-)\|(\d+|-)\|(\d+|-)$'
        match = re.match(pattern, raw_price)
        groups = match.groups()

        coins['penny'] = noz(groups[4])
        coins['shilling'] = noz(groups[3])
        coins['crown'] = noz(groups[2])
        coins['sovereign'] = noz(groups[1])
        coins['hedgehog'] = noz(groups[0])

    # Convert to brass
    brass_coins = (
        (coins['hedgehog'] * 248832) + 
        (coins['sovereign'] * 20736) + 
        (coins['crown'] * 1728) + 
        (coins['shilling'] * 144) + 
        (coins['penny'] * 12) 
    )
    return brass_coins

def convert_brass_to_am(brass_price):
    # 12 brass coins to am pennies
    pennies = brass_price / 4
    return (pennies/100)

def parse_shop_output(data):
    pattern = r'^\s{3}?\w{2}\)\sAn*\s([\w\s-]+) for (L\w{1,3} [\d\-|]+);\s(\w+)\sleft\.$'
    matches = [m.groups() for m in re.finditer(pattern, data, re.MULTILINE)]

    if not matches:
        return

    # Iterate over each product line in the data
    seen_products = []
    for m in matches:
        product = models.ShopProduct.query.filter_by(name=m[0]).first()
        if not product:
            # If we didn't find a product, create it
            product = models.ShopProduct(name=m[0])
            db.session.add(product)
        # Add a ShopEntry for this row only if stock has changed
        if not product.latest_entry or product.latest_entry.raw_stock != m[2]:
            entry = models.ShopEntry(raw_price=m[1], raw_stock=m[2], product=product)
            db.session.add(entry)
        seen_products.append(product)

    # Check all products against seen, record sellouts
    products = models.ShopProduct.query.all()
    for product in products:
        if product not in seen_products and product.latest_entry.stock != 0:
            entry = models.ShopEntry(
                raw_price=product.latest_entry.raw_price,
                raw_stock='zero', product=product
            )
            db.session.add(entry)
    db.session.commit()
