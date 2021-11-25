# -*- coding: utf-8 -*-

import os
import sys
import traceback
from sqlalchemy import create_engine, and_
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func, table
from datetime import datetime, timezone


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
    number_movies = 3

    db_conn = db_connect()

    query = 'select movieid, substr(movietitle, 1, length(movietitle) - 6) as title, year '\
        'from imdb_movies ' \
        'where movieid in (select movieid from imdb_moviecountries where country = \'UK\') ' \
        'order by year desc limit ' + str(number_movies)

    db_result = db_conn.execute(query)

    db_conn.close()

    result_list = list(db_result)
    print(result_list)

def insert_top_UK_mongo(top_UK):
    return top_UK


top_UK = get_top_UK_postgres()
insert_top_UK_mongo(top_UK)






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