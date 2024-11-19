from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017')
db = client['supermarket']
collection = db['items']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add')
def view_items():
    items = list(collection.find())
    return render_template('view_item.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        item = {'name': name, 'quantity': quantity, 'price': price}
        collection.insert_one(item)
        return redirect(url_for('view_items'))
    return render_template('add_items.html')

@app.route('/purchase_item', methods=['GET', 'POST'])
def purchase_item():
    if request.method == 'POST':
        name = request.form['name']
        item = collection.find_one({'name': name})
        if item:
            if item['quantity'] > 0:
                collection.update_one({'name': name}, {'$inc': {'quantity': -1}})
                message = f"Purchased {name} for ${item['price']}."
            else:
                message = f"{name} is out of stock."
        else:
            message = f"{name} not found in inventory."
        return render_template('purchase_item.html', message=message)
    return render_template('purchase_item.html')

@app.route('/search_item', methods=['GET', 'POST'])
def search_item():
    if request.method == 'POST':
        name = request.form['name']
        item = collection.find_one({'name': name})
        if item:
            return render_template('search_item.html', item=item)
        else:
            message = f"{name} not found in inventory."
            return render_template('search_item.html', message=message)
    return render_template('search_item.html')

@app.route('/edit_item', methods=['GET', 'POST'])
def edit_item():
    if request.method == 'POST':
        old_name = request.form['old_name']
        item = collection.find_one({'name': old_name})
        if item:
            new_name = request.form['name']
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
            collection.update_one({'name': old_name}, {'$set': {'name': new_name, 'quantity': quantity, 'price': price}})
            message = f"{old_name} has been updated successfully."
        else:
            message = f"{old_name} not found in inventory."
        return render_template('edit_item.html', message=message)
    return render_template('edit_item.html')

@app.route('/delete/<name>')
def delete_item(name):
    collection.delete_one({'name': name})
    return redirect(url_for('view_items'))

if __name__ == '__main__':
    app.run(debug=True)
