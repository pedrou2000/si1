#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from app import database
from flask import render_template, request, url_for
import os
import sys
import time
from pymongo import MongoClient


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


@app.route('/borraCiudad', methods=['POST', 'GET'])
def borraCiudad():
    if 'city' in request.form:
        city = request.form["city"]
        bSQL = request.form["txnSQL"]
        bCommit = "bCommit" in request.form
        bFallo = "bFallo" in request.form
        duerme = request.form["duerme"]
        dbr = database.delCity(city, bFallo, bSQL == '1', int(duerme), bCommit)
        return render_template('borraCiudad.html', dbr=dbr)
    else:
        return render_template('borraCiudad.html')


@app.route('/topUK', methods=['POST', 'GET'])
def topUK():
    # setup mongodb
    mongoClient = MongoClient("localhost", 27017)
    db = mongoClient["si1"]
    collist = db.list_collection_names()
    if "topUK" not in collist:
        return "No topUK collection!"
    collection = db["topUK"]

    # queries
    query = {
        "genres": {"$elemMatch": {"$in": ["Sci-Fi"]}},
        "year": {"$gte": "1994", "$lte": "1998"}
    }
    movies_scifi = list(collection.find(query))

    query = {
        "genres": {"$elemMatch": {"$in": ["Drama"]}},
        "year": {"$eq": "1998"},
        "title": {"$regex": "(.*, The)|(The.*)"}
    }
    movies_drama = list(collection.find(query))

    query = {"$and": [
        {'actors': {'$elemMatch': {"$regex": "Baldwin, Alec"}}},
        {'actors': {'$elemMatch': {"$regex": "Roberts, Julia"}}}
    ]}
    movies_last = list(collection.find(query))

    movies = [movies_scifi, movies_drama, movies_last]
    return render_template('topUK.html', movies=movies)
