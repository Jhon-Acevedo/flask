from bson import json_util
from flasgger import Swagger
from flask import Flask, jsonify, request, Response
from db import database
from dotenv import load_dotenv
from flask_cors import CORS
import os
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)
db = database.db_connection(mongo_uri=os.getenv("MONGO_URI"), db_name=os.getenv("DATABASE_NAME"))
app.config['SWAGGER'] = {
    "title": "API Products",
    "version": "3.1.6",
    "specs_route": "/docs/",
    "description": "API Products",
    "colorize": True,
}
swagger = Swagger(app)



@app.route('/')
def hello_world():
    return 'BACKEND API PRODUCTS !'


####################################################################################################
# Products
@app.route('/product')
def get_products():
    """
    file: swagger/Product/get_products.yml
    """
    try:
        response = json_util.dumps(db['Products'].find())
        return Response(response, mimetype='application/json')
    except Exception as e:
        return error_handler(e)


@app.route('/product/<int:id_product>')
def get_product_by_id(id_product):
    """
    file: swagger/Product/get_product_by_id.yml
    """
    try:
        response = db['Products'].find_one({'index': id_product})
        if response is None:
            return not_found('Product not found')
        response = json_util.dumps(response)
        return Response(response, mimetype='application/json')
    except Exception as e:
        error_handler(e)


@app.route('/product/<int:id_product>', methods=['DELETE'])
def delete_product(id_product):
    """
    file: swagger/Product/delete_product.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        db['Products'].delete_one({'index': id_product})
        return jsonify({'message': 'Product deleted successfully'}), 204
    except Exception as e:
        error_handler(e)


@app.route("/product/<int:id_product>", methods=['PUT'])
def update_product(id_product):
    """
    file: swagger/Product/update_product.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        if request.json.get('index') is not None:
            return jsonify({'message': 'Index cannot be updated'}), 400
        db['Products'].update_one({'index': id_product}, {'$set': request.json})
        return jsonify({'message': 'Product updated successfully'}), 200
    except Exception as e:
        error_handler(e)


@app.route('/product', methods=['POST'])
def create_product():
    """
    file: swagger/Product/create_product.yml
    """
    try:
        validate = validate_create_product(request)
        if validate is None:
            product = db['Products'].find_one({'index': request.json['index']})
            if product is not None:
                return jsonify({'message': 'Product already exists'}), 409
            product = request.json
            product["_id"] = str(uuid.uuid4())
            db['Products'].insert_one(product)
            return jsonify({'message': 'Product created successfully'}), 201
        else:
            return validate
    except Exception as e:
        error_handler(e)


def validate_create_product(json):
    try:
        if json.json.get('index') is None:
            return jsonify({'message': 'Index is required'}), 400
        if json.json.get('description') is None:
            return jsonify({'message': 'description is required'}), 400
        if json.json.get('imageUrl') is None:
            return jsonify({'message': 'imageUrl is required'}), 400
        if json.json.get('inStock') is None:
            return jsonify({'message': 'InStock is required'}), 400
        if json.json.get('category') is None:
            return jsonify({'message': 'category is required'}), 400
        if json.json.get('product_name') is None:
            return jsonify({'message': 'product_name is required'}), 400
        if json.json.get('price') is None:
            return jsonify({'message': 'price is required'}), 400
        if json.json.get('rating') is None:
            return jsonify({'message': 'rating is required'}), 400
        return None
    except Exception as e:
        error_handler(e)


#####################################################################################
# Reviews
@app.route('/review/<int:id_product>')
def get_reviews(id_product):
    """
    file: swagger/Review/get_list_review.yml
    """
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
    """
    file: swagger/Review/create_review.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        if product.get('reviews') is None:
            product['reviews'] = []
        validate = validate_create_review(request)
        if validate is None:
            review = request.json
            product['reviews'].append(review)
            db['Products'].update_one({'index': id_product}, {'$set': product})
            return jsonify({'message': 'Review created successfully'}), 201
        else:
            return validate
    except Exception as e:
        error_handler(e)


def validate_create_review(json):
    try:
        if json.json.get('id') is None:
            return jsonify({'message': 'Rating is required'}), 400
        if json.json.get('username') is None:
            return jsonify({'message': 'Username is required'}), 400
        if json.json.get('text') is None:
            return jsonify({'message': 'Text is required'}), 400
        if json.json.get('rating') is None:
            return jsonify({'message': 'Rating is required'}), 400
        if json.json.get('date') is None:
            return jsonify({'message': 'Date is required'}), 400
        return None
    except Exception as e:
        error_handler(e)


@app.route('/review/<int:id_product>/<int:id_review>', methods=['DELETE'])
def delete_review(id_product, id_review):
    """
    file: swagger/Review/delete_review.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        review = search_id_review(id_review, product['reviews'])
        if review is None:
            return not_found('Review not found')
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
    """
    file: swagger/Review/update_review.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        review = search_id_review(id_review, product['reviews'])
        if review is None:
            return not_found('Review not found')
        review = product['reviews'][id_review]
        if review is None:
            return not_found('Review not found')
        if request.json.get('id') is not None:
            return jsonify({'message': 'Id cannot be updated'}), 400
        review = request.json
        product['reviews'][id_review] = review
        db['Products'].update_one({'index': id_product}, {'$set': product})
        return jsonify({'message': 'Review updated successfully'}), 200
    except Exception as e:
        error_handler(e)


@app.route('/review/<int:id_product>/<int:id_review>', methods=['GET'])
def get_review(id_product, id_review):
    """
    file: swagger/Review/get_review.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        review = search_id_review(id_review, product['reviews'])
        if review is None:
            return not_found('Review not found')
        review = product['reviews'][id_review]
        if review is None:
            return not_found('Review not found')
        response = json_util.dumps(review)
        return Response(response, mimetype='application/json')
    except Exception as e:
        error_handler(e)


def search_id_review(id_review, reviews):
    for review in reviews:
        if review['id'] == id_review:
            return review
    return None


#####################################################################################
# Features
@app.route('/feature/<int:id_product>')
def get_features(id_product):
    """
    file: swagger/Feature/get_features.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        response = json_util.dumps(product['features'])
        return Response(response, mimetype='application/json')
    except Exception as e:
        error_handler(e)


@app.route('/feature/<int:id_product>/<string:feature>', methods=['POST'])
def create_feature(id_product, feature):
    """
    file: swagger/Feature/create_feature.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        if product.get('features') is None:
            product['features'] = []
        features = product['features']
        for fea in features:
            if fea == feature:
                return jsonify({'message': 'Feature already exists'}), 409
        product['features'].append(feature)
        db['Products'].update_one({'index': id_product}, {'$set': product})
        return jsonify({'message': 'Feature created successfully'}), 201
    except Exception as e:
        error_handler(e)


@app.route('/feature/<int:id_product>/<string:feature>', methods=['DELETE'])
def delete_feature(id_product, feature):
    """
    file: swagger/Feature/delete_feature.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        features = product['features']
        for fea in features:
            if fea == feature:
                db['Products'].update_one({'index': id_product}, {'$pull': {'features': feature}})
                return jsonify({'message': 'Feature deleted successfully'}), 204
        return not_found('Feature not found')
    except Exception as e:
        error_handler(e)


@app.route('/feature/<int:id_product>/<string:previous_feature>/<string:new_feature>', methods=['PUT'])
def update_feature(id_product, previous_feature, new_feature):
    """
    file: swagger/Feature/update_feature.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        features = product['features']
        for fea in features:
            if fea == previous_feature:
                db['Products'].update_one({'index': id_product}, {'$pull': {'features': previous_feature}})
                db['Products'].update_one({'index': id_product}, {'$push': {'features': new_feature}})
                return jsonify({'message': 'Feature updated successfully'}), 200
        return not_found('Feature not found')
    except Exception as e:
        error_handler(e)


def error_handler(error):
    return jsonify({'message': str(error)}), 500


def not_found(error):
    return jsonify({'message': str(error)}), 404


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
