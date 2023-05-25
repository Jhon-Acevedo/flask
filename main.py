import os
from bson import json_util
from flask import Flask, jsonify, request, Response
from db import database
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db = database.db_connection(mongo_uri=os.getenv("MONGO_URI"), db_name=os.getenv("DATABASE_NAME"))


@app.route('/')
def hello_world():
    print(db['Products'].find_one({'index': 1}))
    return 'BACKEND API PRODUCTS !'


####################################################################################################
# Products
@app.route('/product')
def get_products():
    try:
        response = json_util.dumps(db['Products'].find())
        return Response(response, mimetype='application/json')
    except Exception as e:
        return error_handler(e)


@app.route('/product/<int:id_product>')
def get_product_by_id(id_product):
    try:
        response = json_util.dumps(db['Products'].find_one({'index': id_product}))
        if response is None:
            return not_found('Product not found')
        return Response(response, mimetype='application/json')
    except Exception as e:
        error_handler(e)


@app.route('/product/<int:id_product>', methods=['DELETE'])
def delete_product(id_product):
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        return jsonify({'message': 'Product deleted successfully'}), 204
    except Exception as e:
        error_handler(e)


@app.route("/product/<int:id_product>", methods=['PUT'])
def update_product(id_product):
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        db['Products'].update_one({'index': id_product}, {'$set': request.json})
        return jsonify({'message': 'Product updated successfully'}), 200
    except Exception as e:
        error_handler(e)


@app.route('/product', methods=['POST'])
def create_product():
    try:
        product = db['Products'].find_one({'index': request.json['index']})
        if product is not None:
            return jsonify({'message': 'Product already exists'}), 409
        product = {
            "index": request.json['index'],
            "category": request.json['category'],
            "imageUrl": request.json['imageUrl'],
            "inStock": request.json['inStock'],
            "price": request.json['price'],
            "product_name": request.json['product_name'],
            "description": request.json['description'],
            "rating": request.json['rating'],
            "reviews": request.json['reviews'],
            "features": request.json['features']
        }
        db['Products'].insert_one(product)
        return jsonify({'message': 'Product created successfully'}), 201
    except Exception as e:
        error_handler(e)


#####################################################################################
# Reviews
@app.route('/review/<int:id_product>')
def get_reviews(id_product):
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        response = json_util.dumps(product['reviews'])
        return Response(response, mimetype='application/json')
    except Exception as e:
        error_handler(e)


@app.route('/review/<int:id_product>', methods=['POST'])
def create_review(id_product):
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        review = request.json
        product['reviews'].append(review)
        db['Products'].update_one({'index': id_product}, {'$set': product})
        return jsonify({'message': 'Review created successfully'}), 201
    except Exception as e:
        error_handler(e)


@app.route('/review/<int:id_product>/<int:id_review>', methods=['DELETE'])
def delete_review(id_product, id_review):
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        review = product['reviews'][id_review]
        if review is None:
            return not_found('Review not found')
        product['reviews'].pop(id_review)
        db['Products'].update_one({'index': id_product}, {'$set': product})
        return jsonify({'message': 'Review deleted successfully'}), 204
    except Exception as e:
        error_handler(e)


@app.route('/review/<int:id_product>/<int:id_review>', methods=['PUT'])
def update_review(id_product, id_review):
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        review = product['reviews'][id_review]
        if review is None:
            return not_found('Review not found')
        product['reviews'][id_review] = request.json
        db['Products'].update_one({'index': id_product}, {'$set': product})
        return jsonify({'message': 'Review updated successfully'}), 200
    except Exception as e:
        error_handler(e)


@app.route('/review/<int:id_product>/<int:id_review>', methods=['GET'])
def get_review(id_product, id_review):
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        review = product['reviews'][id_review]
        if review is None:
            return not_found('Review not found')
        response = json_util.dumps(review)
        return Response(response, mimetype='application/json')
    except Exception as e:
        error_handler(e)


#####################################################################################
# Features
@app.route('/feature/<int:id_product>')
def get_features(id_product):
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        response = json_util.dumps(product['features'])
        return Response(response, mimetype='application/json')
    except Exception as e:
        error_handler(e)


@app.route('/feature/<int:id_product>', methods=['POST'])
def create_feature(id_product):
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        feature = request.json['feature']
        db['Products'].update_one({'index': id_product}, {'$push': {'features': feature}})
        return jsonify({'message': 'Feature created successfully'}), 201
    except Exception as e:
        error_handler(e)


@app.route('/feature/<int:id_product>', methods=['DELETE'])
def delete_feature(id_product):
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        feature = request.json['feature']
        db['Products'].update_one({'index': id_product}, {'$pull': {'features': feature}})
        return jsonify({'message': 'Feature deleted successfully'}), 204
    except Exception as e:
        error_handler(e)


def error_handler(error):
    return jsonify({'message': str(error)}), 500


def not_found(error):
    return jsonify({'message': str(error)}), 404


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
