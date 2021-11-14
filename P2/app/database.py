# -*- coding: utf-8 -*-

import os
import sys
import traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text, bindparam
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func

# configurar el motor de sqlalchemy
db_engine = create_engine(
    "postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)
# cargar una tabla
db_table_movies = Table('imdb_movies', db_meta,
                        autoload=True, autoload_with=db_engine)
db_table_customers = Table(
    'customers', db_meta, autoload=True, autoload_with=db_engine)


def db_listOfMovies1949():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Seleccionar las peliculas del anno 1949
        db_movies_1949 = select([db_table_movies]).where(text("year = '1949'"))
        db_result = db_conn.execute(db_movies_1949)
        #db_result = db_conn.execute("Select * from imdb_movies where year = '1949'")

        db_conn.close()

        return list(db_result)
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'


def db_getTopActors(genre, number_of_films):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        topActors = select(
            ['*']).select_from(func.getTopActors(genre)).limit(number_of_films)
        print(topActors)
        db_result = db_conn.execute(topActors)

        db_conn.close()

        result_list = list(db_result)

        return result_list
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'


def db_user_already_exists(username):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_username = select([db_table_customers]).where(
            text("username = '" + username + "'"))
        db_result = db_conn.execute(db_username)

        db_conn.close()

        users = list(db_result)
        if len(users) == 0:
            print('no usuer named ' + username)
            return False
        print('Found usuer named ' + username)
        print(users)
        return True

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'


def db_login(username, password):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_username = select([db_table_customers]).where(
            text("username = '" + username + "'"))
        db_result = list(db_conn.execute(db_username))[0]

        db_conn.close()

        if db_result['password'] != password:
            print('Different passwords, ' + db_result['password'] + ' != ' + password)
            return None

        user = dict()
        user['data'] = dict()
        user['data']['username'] = db_result['username']
        user['data']['password'] = db_result['password']
        user['data']['email'] = db_result['email']
        user['data']['credit_card'] = db_result['creditcard']
        user['data']['direccion_envio'] = db_result['address1']
        user['data']['balance'] = db_result['balance']
        user['data']['points'] = db_result['points']
        print('Correct login, username: ' + user['data']['username'])

        return user
        """
        {"username": "benton", "password": "oooooooo", "email": "o@gmail.com", "credit_card": "1234567812345678", 
        "direccion_envio": "a", "balance": 97.67, "points": 0}
        """

        if len(users) == 0:
            print('no usuer named ' + username)
            return False
        print('Found usuer named ' + username)
        print(users)
        return True

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'


def db_add_user(username, password, email, credit_card, direccion_envio, balance):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        new_id = list(db_conn.execute(
            "SELECT max(customerid) FROM customers"))[0][0]
        new_id += 1

        user_insertion = db_table_customers.insert().values(customerid=new_id,
                                                            firstname=username,
                                                            lastname=username,
                                                            address1=direccion_envio,
                                                            city='Getafe',
                                                            country='Spain',
                                                            region='Madrid',
                                                            email=email,
                                                            creditcardtype='VISA',
                                                            creditcard=credit_card,
                                                            creditcardexpiration='8/2030',
                                                            username=username,
                                                            password=password,
                                                            loyalty=1,
                                                            balance=balance,
                                                            points=0,
                                                            )
        db_result = db_conn.execute(user_insertion)

        db_conn.close()

        print(db_result)

        return True

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'
