import os
import uuid

from bson import json_util
from flasgger import Swagger
# from flask_restful_swagger_3 import Api
from flask import Flask, jsonify, request, Response
from db import database
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
db = database.db_connection(mongo_uri=os.getenv("MONGO_URI"), db_name=os.getenv("DATABASE_NAME"))
app.config['SWAGGER'] = {
    "title": "API Products",
    "version": "3.1.6",
    "specs_route": "/docs/",
    "description": "API Products",
    "colorize": True,
}
swagger = Swagger(app)


# api = Api(app)

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
        product = db['Products'].find_one({'index': request.json['index']})
        if product is not None:
            return jsonify({'message': 'Product already exists'}), 409
        product = request.json
        product["_id"] = str(uuid.uuid4())
        db['Products'].insert_one(product)
        return jsonify({'message': 'Product created successfully'}), 201
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
        review = search_id_review(request.json['id'], product['reviews'])
        if review is not None:
            return jsonify({'message': 'Review already exists'}), 409
        review = request.json
        product['reviews'].append(review)
        db['Products'].update_one({'index': id_product}, {'$set': product})
        return jsonify({'message': 'Review created successfully'}), 201
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
        id_review = search_id_review(request.json['id'], product['reviews'])
        # if id_review is not None:
        #     return jsonify({'message': 'ID Review already exists'}), 409
        product['reviews'][id_review] = request.json
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


@app.route('/feature/<int:id_product>', methods=['POST'])
def create_feature(id_product):
    """
    file: swagger/Feature/create_feature.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        feature = request.json['feature']
        db['Products'].update_one({'index': id_product}, {'$push': {'features': feature}})
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


@app.route('/feature/<int:id_product>/<string:previous_feature>', methods=['PUT'])
def update_feature(id_product, previous_feature):
    """
    file: swagger/Feature/update_feature.yml
    """
    try:
        product = db['Products'].find_one({'index': id_product})
        if product is None:
            return not_found('Product not found')
        features = product['features']
        for feature in features:
            if feature == previous_feature:
                db['Products'].update_one({'index': id_product}, {'$pull': {'features': feature}})
                db['Products'].update_one({'index': id_product}, {'$push': {'features': request.json['feature']}})
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
