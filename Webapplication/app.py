import json
import string
from flask_cors import CORS
from collections import Counter
from elasticsearch import Elasticsearch
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)
CORS(app)
es = Elasticsearch(hosts=['http://127.0.0.1:9200'])

MAX_SIZE = 20

def search_query(query):
    tokens_list = query.translate(str.maketrans('', '', string.punctuation)).lower().strip().replace('–',' ').split(' ')
    tokens = [x for x in tokens_list if x != '']

    clauses = [
        {
            "span_multi": {
                "match": {"fuzzy": {"title": {"value": token, "fuzziness": "AUTO"}}}
            }
        } for token in tokens
    ]

    payload = {
        "bool": {
            "must": [{"span_near": {"clauses": clauses, "slop": 0, "in_order": False}}]
        }
    }

    response = es.search(index="items", query=payload, size=MAX_SIZE)
    results = response['hits']['hits']
    return results

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/results',methods = ['POST', 'GET'])
def result():
    if request.method == 'GET':
        query = request.args.get('query')
        print(query)
        category_list, store_list, price_list, availability_list = [], [], [], []
        search_results = search_query(query)
        for item in search_results:
            category_list.extend(item['_source']['category'])
            store_list.append(item['_source']['store'])
            price_list.append(item['_source']['price'])
            availability_list.append(item['_source']['availability'])
        category_dict = dict(Counter(category_list).items())
        store_dict = dict(Counter(store_list).items())
        availability_dict = dict(Counter(availability_list).items())
        max_price = max(price_list)
        min_price = min(price_list)
        # results = jsonify(
        #     category_dict= category_dict,
        #     store_dict= store_dict,
        #     availability_dict= availability_dict,
        #     max_price= max_price,
        #     min_price= min_price,
        #     items=search_results
        # )
        # return render_template("results.html", result = results)
        json_string = jsonify(items=search_results)
        results = json_string
        # return results
        return render_template("results.html", result = results)


@app.route('/search')
def search():
    query = request.args['q']
    return list(set([result['_source']['title'] for result in search_query(query)]))

if __name__ == '__main__':
    app.run(debug=True)