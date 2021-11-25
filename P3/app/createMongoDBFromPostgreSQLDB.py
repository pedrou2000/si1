# -*- coding: utf-8 -*-

import os
import sys
import traceback
import math
from sqlalchemy import create_engine, and_
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func, table
from datetime import datetime, timezone
from pymongo import MongoClient


# configurar el motor de sqlalchemy
db_engine = create_engine(
    "postgresql://alumnodb:alumnodb@localhost/si1_p3", echo=False)
db_meta = MetaData(bind=db_engine)

film_image = "/static/images/avatar.jpg"

# TABLAS
table_customers = Table(
    'customers', db_meta, autoload=True, autoload_with=db_engine)

# talas productos y pedidos
table_inventory = Table(
    'inventory', db_meta, autoload=True, autoload_with=db_engine)
table_products = Table(
    'products', db_meta, autoload=True, autoload_with=db_engine)
table_orders = Table(
    'orders', db_meta, autoload=True, autoload_with=db_engine)
table_orderdetail = Table(
    'orderdetail', db_meta, autoload=True, autoload_with=db_engine)


# tablas peliculas
table_movies = Table('imdb_movies', db_meta,
                     autoload=True, autoload_with=db_engine)
table_directors = Table(
    'imdb_directors', db_meta, autoload=True, autoload_with=db_engine)
table_directormovies = Table(
    'imdb_directormovies', db_meta, autoload=True, autoload_with=db_engine)
table_genremovies = Table(
    'imdb_moviegenres', db_meta, autoload=True, autoload_with=db_engine)
table_actors = Table(
    'imdb_actors', db_meta, autoload=True, autoload_with=db_engine)
table_actormovies = Table(
    'imdb_actormovies', db_meta, autoload=True, autoload_with=db_engine)



def db_connect():
    db_conn = None
    try:
        # conexion a la base de datos
        db_conn = db_engine.connect()
        return db_conn
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)
        return None

def get_top_UK_postgres():
    number_movies = 10

    db_conn = db_connect()

    query = 'select movieid, substr(movietitle, 1, length(movietitle) - 6) as title, year '\
            'from imdb_movies natural inner join '\
	        '(select movieid from imdb_moviecountries where country = \'UK\') uk_movies '\
            'order by year desc limit ' + str(number_movies)

    db_result = db_conn.execute(query)


    result_list = list(db_result)
    movies_dict = {}
    for item in result_list:
        movie_dict = {}
        movie_dict['title'] = item[1]
        movie_dict['year'] = item[2]
        movies_dict[item[0]] = movie_dict

    db_conn.close()

    return movies_dict


def get_movie_genres(db_conn, movieid):
    query = 'select distinct genre '\
            'from imdb_movies join imdb_moviegenres on imdb_moviegenres.movieid= ' + str(movieid)

    db_result = db_conn.execute(query)
    result_list = []
    for item in list(db_result):
        result_list.append(item[0])

    return result_list

def get_movie_directors(db_conn, movieid):

    query = 'select imdb_directors.directorname '\
            'from imdb_directors natural inner join imdb_directormovies '\
            'natural inner join imdb_movies '\
            'where imdb_movies.movieid= ' + str(movieid)

    db_result = db_conn.execute(query)
    result_list = []
    for item in list(db_result):
        result_list.append(item[0])

    return result_list

def get_movie_actors(db_conn, movieid):

    query = 'select imdb_actors.actorname '\
            'from imdb_actors join imdb_actormovies on '\
            'imdb_actormovies.actorid=imdb_actors.actorid '\
            'join imdb_movies on '\
            'imdb_actormovies.movieid=imdb_movies.movieid and imdb_movies.movieid= ' + str(movieid)

    db_result = db_conn.execute(query)
    result_list = []
    for item in list(db_result):
        result_list.append(item[0])

    return result_list


def get_movie_most_related_movies(db_conn, movieid, movies_dict):
    movie_list = []
    searched_genres = set(movies_dict[movieid]['genres'])
    total_genres = len(searched_genres)

    for id in movies_dict.keys():
        if id != movieid:
            current_genres = movies_dict[id]['genres']
            same_genres = 0
            for genre in current_genres:
                if genre not in searched_genres:
                    same_genres += 1
            if same_genres == total_genres:
                added_dict = {}
                added_dict['title'] = movies_dict[id]['title']
                added_dict['year'] = movies_dict[id]['year']
                movie_list.append(added_dict)


    return movie_list


def get_movie_related_movies(db_conn, movieid, movies_dict):
    movie_list = []
    searched_genres = set(movies_dict[movieid]['genres'])
    total_genres = math.ceil(len(searched_genres)/2)

    for id in movies_dict.keys():
        if id != movieid:
            current_genres = movies_dict[id]['genres']
            same_genres = 0
            for genre in current_genres:
                if genre not in searched_genres:
                    same_genres += 1
            if same_genres == total_genres:
                added_dict = {}
                added_dict['title'] = movies_dict[id]['title']
                added_dict['year'] = movies_dict[id]['year']
                movie_list.append(added_dict)


    return movie_list



def insert_top_UK_mongo(movies_dict):

    db_conn = db_connect()

    for movieid in movies_dict.keys():
        movies_dict[movieid]['genres'] = get_movie_genres(db_conn, movieid)
        movies_dict[movieid]['directors'] = get_movie_directors(db_conn, movieid)
        movies_dict[movieid]['actors'] = get_movie_actors(db_conn, movieid)
    
    for movieid in movies_dict.keys():
        movies_dict[movieid]['most_related_movies'] = get_movie_most_related_movies(db_conn, movieid, movies_dict)
        movies_dict[movieid]['related_movies'] = get_movie_related_movies(db_conn, movieid, movies_dict)


    db_conn.close()

    """
    print()
    print()
    print()
    for id in movies_dict.keys():
        print()
        print(movies_dict[id])
    """

    # mongo insertion    
    mongoClient = MongoClient("localhost", 27017)
    db = mongoClient["si1"]
    collist = db.list_collection_names()
    if "topUK" in collist:
        db["topUK"].drop()

    collection = db["topUK"]
    for movie_dict in movies_dict.values():
        collection.insert_one(movie_dict)
    
    return movies_dict

""""
from pymongo import MongoClient
def main():
    
    mongoClient = MongoClient("localhost", 27017)
    db = mongoClient.mi_base_de_datos
    collection = db.inventario
    cursor = collection.find({"status":"D"})
    for elemento in cursor:
        print ("%s" %(elemento['item']))
    mongoClient.close()
    
    mongoClient = MongoClient("localhost", 27017)
    db = mongoClient["si1"]
    collection = db["topUK"]
    for dict in movies_dict.values():
        collection.insert_one(dict)

if __name__ == '__main__':
    main()


"""
movies_dict = get_top_UK_postgres()
insert_top_UK_mongo(movies_dict)






"""
SELECT row_to_json(t) FROM 

(
select movieid, 
	substr(movietitle, 1, length(movietitle) - 6) as title, 
	year
from imdb_movies natural inner join 
	(select movieid from imdb_moviecountries where country = 'UK') uk_movies
order by year desc
limit 400) t


select movieid, 
	substr(movietitle, 1, length(movietitle) - 6) as title, 
	year
from imdb_movies
where movieid in (select movieid from imdb_moviecountries where country = 'UK')
order by year desc
limit 400
"""