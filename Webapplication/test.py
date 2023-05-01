import json
import string
from flask_cors import CORS
from collections import Counter
from elasticsearch import Elasticsearch
from flask import Flask, request, render_template, jsonify

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

if __name__ == '__main__':
    query = 'controller'
    print(query)
    category_list, store_list, price_list, availability_list = [], [], [], []
    search_results = search_query(query)
    for item in search_results:
        category_list.extend(item['_source']['category'])
        store_list.append(item['_source']['store'])
        price_list.append(item['_source']['price'])
        availability_list.append(item['_source']['availability'])

    category_list = list(set(category_list))
    store_list = list(set(store_list))
    availability_list = list(set(availability_list))
    max_price = max(price_list)
    min_price = min(price_list)

    results_dict = {
        'category': category_list,
        'store': store_list,
        'availability': availability_list,
        'max_price': max_price,
        'min_price': min_price,
        'items': search_results
    }

    print(results_dict)