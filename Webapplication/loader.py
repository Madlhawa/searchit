from elasticsearch import Elasticsearch
import csv
import json

es = Elasticsearch(hosts=['http://127.0.0.1:9200'])
print(f'Connected to ElasticSearch cluster {es.info().body["cluster_name"]}')

# with open("CAR DETAILS FROM CAR DEKHO.xls", 'r') as data_file:
#     reader = csv.reader(data_file)

#     for i, line in enumerate(reader):
#         document = {
#             'name' : line[0],
#             'fuel' : line[3],
#             'year' : line[1],
#             'price' : line[2]
#         }
#         es.index(index="cars", document=document)

es.options(ignore_status=[400,404]).indices.delete(index='items')

with open('data/data.json', 'r') as data_file:
    json_file = json.load(data_file)

    for item in json_file:
        es.index(index="items", document=item)
        print(item['title'])

# {
#     "location": "online", 
#     "condition": "New", 
#     "price": 250.0, 
#     "title": " Replacement Microfiber Heads (Self Spray Mop)", 
#     "description": "Extra pads for the Self Spray Mop Mop Head Material: Microfiber : Blue / Red (Sent at Random)", 
#     "store": "Laabai", 
#     "img": "https://www.laabai.lk/wp-content/uploads/2017/05/SELF-SPRAY-MOP-PADS-510x510.jpg", 
#     "url": "https://www.laabai.lk/shop/spray-mop-pads/"
# }
