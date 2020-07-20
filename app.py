# import csv
import sys
import os
# import json
import pandas as pd 
import tensorflow as tf 
import keras 
from keras.models import model_from_json, load_model
import numpy as np 
# import sys, getopt, pprint
import flask 
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient


#read in csv file 
# df = pd.read_csv('/Users/angelicacalderon/repos/Perfectly_Paired/Resources/winemag-data-130k-v2.csv', low_memory=False)
# df = df.rename(columns = {'region_1': 'region_one', 'region_2': 'region_two'})
# df.to_csv('/Users/angelicacalderon/repos/Perfectly_Paired/Resources/winemag-data-130k-v2.csv',index=False)

conn = 'mongodb://localhost:27017'
client = MongoClient(conn)

#connect to MongoDB wine_db
db = client['wine_db']

#create collections 
reviews_collection = db['reviews']
red_white_collection = db['red_white']

#drop collection if available to remove duplicates
db.reviews_collection.drop()
db.red_white_collection.drop()

#define function to read csv file as json 
def csv_to_json(filename, header=True):
    data = pd.read_csv(filename,low_memory=False)
    return data.to_dict('records')

#insert json file to collections 
reviews_collection.insert_many(csv_to_json('/Users/angelicacalderon/repos/Perfectly_Paired/Resources/winemag-data-130k-v2.csv'))
red_white_collection.insert_many(csv_to_json('/Users/angelicacalderon/repos/Perfectly_Paired/Resources/red_wine_combined.csv'))

#connect to mongoDB wine db 
mongoDB = ('mongodb:///?Server=localhost&Port=27017&Database=wine_db')


#################################################
# Flask Routes
#################################################


app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h2>Welcome to the Directory</h2>"
        f"Available Routes:<br/>"
        f"<a href = '/reviews' target='_blank'>/Wine Reviews</a><br/>"
        f"<a href = '/red_white_wines' target='_blank'>/Red & White Wines</a><br/>"
        f"<a href = '/predict_red_white' target='_blank'>/Red & White Prediction</a><br/>"
    )

#reviews route 
@app.route('/reviews')
def reviews():
    reviews_documents = reviews_collection.find()
    response = []
    for document in reviews_documents:
        document['_id'] = str(document['_id'])
        response.append(document)
    return jsonify(response)

#red_white_wines route 
@app.route('/red_white_wines')
def red_white():
    red_white_documents = red_white_collection.find()
    response = []
    for document in red_white_documents:
        document['_id'] = str(document['_id'])
        response.append(document)
    return jsonify(response)

@app.route('/predict_red_white')
def predict():
    # whenever the predict method is called, we're going
    # to input the user psychochemical characteristics 
    
    # enter user input in html 
    # test_x= request.get_data()
    # test_x = [[test_x]]
    test_x = [[0.15702479, 0.128     , 0.38211382, 0.08742331, 0.0951586 ,
        0.11805556, 0.40552995, 0.13109697, 0.29133858, 0.13483146,
        0.25120773]]

    #  Load the model
    redorwhite_model = load_model('/Users/angelicacalderon/repos/Perfectly_Paired/Red_and_White_Analysis/redorwhite_model_trained.h5')

    #predict the wine class based on model and save output to 'out'
    out = redorwhite_model.predict_classes(test_x)
    out = out[0]
    return jsonify({'wine_selection': str(out)})

if __name__ == "__main__":
    app.run(debug=True)





