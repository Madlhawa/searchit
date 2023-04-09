from flask import Flask, request, render_template
from flask_cors import CORS
from elasticsearch import Elasticsearch
import string

app = Flask(__name__)
CORS(app)
es = Elasticsearch(hosts=['http://127.0.0.1:9200'])

MAX_SIZE = 20

def search_query(query):
    tokens_list = query.translate(str.maketrans('', '', string.punctuation)).lower().strip().replace('–',' ').split(' ')
    tokens = [x for x in tokens_list if x != '']
    print(tokens)

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

    resp = es.search(index="items", query=payload, size=MAX_SIZE)
    return resp['hits']['hits']

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/results',methods = ['POST', 'GET'])
def result():
   if request.method == 'GET':
      query = request.args.get('query')
      print(query)
      for item in search_query(query):
          print(item)
      return render_template("results.html",result = search_query(query))

@app.route('/search')
def search():
    query = request.args['q']
    return list(set([result['_source']['title'] for result in search_query(query)]))

if __name__ == '__main__':
    app.run(debug=True)