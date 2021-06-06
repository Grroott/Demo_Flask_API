from flask import Flask, jsonify, request
from datetime import datetime
import json

mandatory_request_params = ['Product_name', 'Category', 'Expiry_date', 'Cost_price', 'Selling_price']

app = Flask(__name__)


def read_file():
    with open("data.json") as f:
        return json.load(f)


@app.route("/")
def home():
    return "Use some route"


@app.route("/get_all_data", methods=['GET'])
def get_all_data():
    file_data = read_file()
    return jsonify(file_data["data"])


@app.route("/get_all_product_names", methods=['GET'])
def get_all_product_names():
    file_data = read_file()
    get_product_name = {i["ID"]: i["Product_name"] for i in file_data["data"]}
    return jsonify(get_product_name)


@app.route("/get_product_by_id/<product_id>", methods=['GET'])
def get_product_by_id(product_id=None):
    file_data = read_file()
    get_product_data = [item for item in file_data["data"] if item["ID"] == int(product_id)]
    return jsonify(get_product_data)


@app.route("/add_product", methods=['POST'])
def add_product():
    if request.method == 'POST' and request.headers.get('secret-key') == 'some-random-secret-key':
        request_data = json.loads(request.data)
        # mandatory params check
        missing_params = [params for params in mandatory_request_params if params not in request_data.keys()]

        if missing_params:
            return "{} is/are missing in request!".format(missing_params), 400

        # Format check
        cost_price_format = True if any(
            [isinstance(request_data['Cost_price'], int) or isinstance(request_data['Cost_price'], float)]) else False
        selling_price_format = True if any([isinstance(request_data['Selling_price'], int) or isinstance(
            request_data['Selling_price'], float)]) else False
        try:
            if request_data['Expiry_date'] == "None" or datetime.strptime(request_data['Expiry_date'],
                                                                          '%Y-%m-%d').date():
                expiry_date_format = True
        except:
            expiry_date_format = False

        if not all([cost_price_format, selling_price_format, expiry_date_format]):
            return jsonify({"Expected_Format": {"Cost_price": "Integer or Float", "Selling_price": "Integer or Float",
                                                "Expiry_date": "YYYY-mm-dd"}}), 400

        request_data_dict = {'Product_name': request_data['Product_name'], 'Category': request_data['Category'],
                             'Expiry_date': request_data['Expiry_date'], 'Cost_price': request_data['Cost_price'],
                             'Selling_price': request_data['Selling_price']}
        request_data_dict['Profit'] = request_data_dict['Selling_price'] - request_data_dict['Cost_price']

        file_data = read_file()
        get_max_product_id = max([item["ID"] for item in file_data["data"] if item["ID"]])
        request_data_dict['ID'] = get_max_product_id + 1

        file_data["data"].append(request_data_dict)

        user_encode_data = json.dumps(file_data, indent=2).encode('utf-8')
        with open('data.json', 'wb') as f:
            f.write(user_encode_data)

        return jsonify(request_data_dict)
    else:
        return jsonify({"Error": "Invalid secret-key"}), 400


@app.route("/get_product_count/<product_name>", methods=['GET'])
def get_product_count(product_name=None):
    file_data = read_file()
    product_count = len([product for product in file_data['data'] if product.get("Product_name", []) == product_name])
    return jsonify({"Product_Name": product_name, "count": product_count})


if __name__ == '__main__':
    app.run(debug=True)
