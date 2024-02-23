from flask import Flask, request, jsonify
from flask_cors import CORS
from decimal import Decimal

app = Flask(__name__)
CORS(app)

# Sample in-memory product list
products = [
    {'id': 1, 'name': 'Apple', 'price': Decimal('10'), 'units': 'units', 'taken': 0, 'payable': Decimal('0.0')},
    {'id': 2, 'name': 'Banana', 'price': Decimal('20'), 'units': 'units', 'taken': 0, 'payable': Decimal('0.0')},
    # Add more products as needed
]

# Helper function to find a product by ID
def find_product(product_id):
    return next((product for product in products if product['id'] == product_id), None)



# Route to get all products
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify({'products': products})




# Route to get a specific product by ID
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = find_product(product_id)
    if product:
        return jsonify({'product': product})
    return jsonify({'message': 'Product not found'}), 404




# Route to create a new product
@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()

    # Input validation
    if not all(key in data for key in ('name', 'price', 'units')):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        new_product = {
            'id': len(products) + 1,
            'name': data['name'],
            'price': Decimal(str(data['price'])),  # Convert to Decimal for accuracy
            'units': data['units'],
            'taken': 0,
            'payable': Decimal('0.0'),
        }
        products.append(new_product)
        return jsonify({'message': 'Product created successfully', 'product': new_product}), 201
    except ValueError:
        return jsonify({'message': 'Invalid price format'}), 400



# Route to update a product by ID
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = find_product(product_id)
    if product:
        data = request.get_json()
        product.update(data)
        return jsonify({'message': 'Product updated successfully', 'product': product})
    return jsonify({'message': 'Product not found'}), 404




# Route to delete a product by ID
# @app.route('/products/<int:product_id>', methods=['DELETE'])
# def delete_product(product_id):
#     global products
#     products = [product for product in products if product['id'] != product_id]
#     return jsonify({'message': 'Product deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)




# Invoke-RestMethod -Uri http://127.0.0.1:5000/products/1 -Method Put -Headers @{"Content-Type"="application/json"} -Body '{"name": "Updated Apple", "price": 15.0, "units": "updated units"}'
    

    # Invoke-RestMethod -Uri http://127.0.0.1:5000/products -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"name": "New Product", "price": 25.0, "units": "new units"}'



# Invoke-RestMethod -Uri http://127.0.0.1:5000/products -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"name": "mango", "price": 34.2, "units": "4","taken":4}'