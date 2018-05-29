import re

from flask import (
    request,
    url_for,
    redirect,
    render_template
)

from . import (
    db,
    app,
    models,
    shop
)


@app.route('/')
def shop_dashboard():
    return render_template('shop_dashboard.html',
                           products=models.ShopProduct.query.all())

@app.route('/shop/data', methods=['POST','GET'])
def shop_dataentry():
    if request.method == 'POST':
        if request.form.get('password') == 'r3m3di3s' and request.form.get('mission-data'):
            data = request.form['mission-data']
            clean_data = data.replace('\r\n', '\n')
            shop.parse_shop_output(clean_data)
            return redirect(url_for('shop_dashboard'))
    return render_template('shop_dataentry.html')

@app.route('/shop/product/<int:product_id>')
def shop_product_entries(product_id):
    product = models.ShopProduct.query.filter_by(id=product_id).first_or_404()
    return render_template('shop_product_entries.html', product=product)
