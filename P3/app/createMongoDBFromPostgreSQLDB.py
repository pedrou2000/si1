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
    number_movies = 400

    db_conn = db_connect()

    query = 'select movieid, regexp_replace(movietitle, \'\(.*\)\', \'\') as title, year '\
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


def get_movie_related_movies(movieid, movies_dict, total_genres):
    movie_list = []
    searched_genres = set(movies_dict[movieid]['genres'])

    for id in movies_dict.keys():
        if id != movieid:
            current_genres = movies_dict[id]['genres']
            same_genres = 0
            for genre in current_genres:
                if genre in searched_genres:
                    same_genres += 1
            
            # si el numero de generos es igual insertamos 
            if same_genres == total_genres:# and len(current_genres) == len(searched_genres):
                if len(movie_list) == 0:
                    oldest_film_index = 0
                    added_dict = {}
                    added_dict['title'] = movies_dict[id]['title']
                    added_dict['year'] = movies_dict[id]['year']
                    #added_dict['genres'] = movies_dict[id]['genres']
                    movie_list.append(added_dict)
                
                # si la lista esta llena ya
                elif len(movie_list) == 10:
                    if int(movie_list[oldest_film_index]['year']) < int(movies_dict[id]['year']):
                        added_dict = {}
                        added_dict['title'] = movies_dict[id]['title']
                        added_dict['year'] = movies_dict[id]['year']
                        #added_dict['genres'] = movies_dict[id]['genres']
                        movie_list.append(added_dict)
                        movie_list[oldest_film_index] = added_dict
                        # actualizamos el index de la pelicula mas antigua de la lista
                        oldest_film_index = 0
                        for i in range(9):
                            if int(movie_list[oldest_film_index]['year']) > int(movie_list[i]['year']):
                                oldest_film_index = i

                # si todavia hay espacio en la lista de 10 elementos
                else:
                    added_dict = {}
                    added_dict['title'] = movies_dict[id]['title']
                    added_dict['year'] = movies_dict[id]['year']
                    #added_dict['genres'] = movies_dict[id]['genres']
                    movie_list.append(added_dict)
                    # guardamos el indice de la lista de la pelicula mas antigua
                    if int(movie_list[oldest_film_index]['year']) > int(movies_dict[id]['year']):
                        oldest_film_index = len(movie_list) - 1

    return movie_list


def insert_top_UK_mongo(movies_dict):

    db_conn = db_connect()

    for movieid in movies_dict.keys():
        movies_dict[movieid]['genres'] = get_movie_genres(db_conn, movieid)
        movies_dict[movieid]['directors'] = get_movie_directors(db_conn, movieid)
        movies_dict[movieid]['actors'] = get_movie_actors(db_conn, movieid)
    
    for movieid in movies_dict.keys():
        movies_dict[movieid]['most_related_movies'] = get_movie_related_movies(movieid, movies_dict, len(movies_dict[movieid]['genres']))
        if len(movies_dict[movieid]['genres']) > 1:
            movies_dict[movieid]['related_movies'] = get_movie_related_movies(movieid, movies_dict, math.ceil(len(movies_dict[movieid]['genres'])/2))

    db_conn.close()

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



movies_dict = get_top_UK_postgres()
insert_top_UK_mongo(movies_dict)



