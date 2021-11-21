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
    "postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
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
table_genres = Table(
    'imdb_genres', db_meta, autoload=True, autoload_with=db_engine)
table_genremovies = Table(
    'imdb_genremovies', db_meta, autoload=True, autoload_with=db_engine)
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


def db_getTopActors(genre, number_of_films):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    topActors = select(
        ['*']).select_from(func.getTopActors(genre)).limit(number_of_films)
    db_result = db_conn.execute(topActors)

    db_conn.close()

    result_list = list(db_result)
    return result_list


def db_search_closmovies(string, max_movies):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    look_for = '%{0}%'.format(string)

    query = select([table_movies]).where(
        table_movies.c.movietitle.contains(look_for)).limit(max_movies)
    result = list(db_conn.execute(query))

    result_list = []
    for row in result:
        movieid = row['movieid']
        movied_dict = db_parse_movie(db_conn, movieid)
        result_list.append(movied_dict)

    db_conn.close()

    return result_list


def db_filter_movies(category, max_movies):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_genres]).where(
        table_genres.c.genre == category)
    result = list(db_conn.execute(query))[0]
    genre_id = result['genreid']

    query = select([table_genremovies]).where(
        table_genremovies.c.genreid == genre_id).limit(max_movies)
    result = list(db_conn.execute(query))

    result_list = []
    for row in result:
        movieid = row['movieid']
        movied_dict = db_parse_movie(db_conn, movieid)
        result_list.append(movied_dict)

    db_conn.close()

    return result_list


def db_get_genres():
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_genres])
    result = list(db_conn.execute(query))

    result_list = []
    for row in result:
        genre_name = row['genre']
        result_list.append(genre_name)

    db_conn.close()

    return result_list


def db_parse_movie(db_conn, movieid):
    movie_dict = dict()
    movieid = str(movieid)

    # get the products associated to this film
    query = select([table_products]).where(
        text("movieid = " + movieid))
    result = list(db_conn.execute(query))
    movie_dict['products'] = []
    for row in result:
        product_id = row['prod_id']
        product_dict = db_parse_product(db_conn, product_id)
        movie_dict['products'].append(product_dict)
        #print(movie_dict['products'])

    # get movie info
    query = select([table_movies]).where(
        text("movieid = " + movieid))
    row = list(db_conn.execute(query))[0]

    movie_dict['movieid'] = row['movieid']
    movie_dict['movietitle'] = row['movietitle']
    movie_dict['image'] = film_image

    # get director
    director_query = select([table_directormovies, table_directors]).where(
        and_(
            table_directormovies.c.movieid == text(movieid),
            table_directormovies.c.directorid == table_directors.c.directorid,
        )
    )
    db_result = list(db_conn.execute(director_query))[0]
    movie_dict['director'] = db_result['directorname']

    # get actors
    actors_query = select([table_actormovies, table_actors]).where(
        and_(
            table_actormovies.c.movieid == text(movieid),
            table_actormovies.c.actorid == table_actors.c.actorid,
        )
    )
    db_result = list(db_conn.execute(actors_query))
    movie_dict['actors'] = []
    for row in db_result:
        movie_dict['actors'].append({
            # 'actorid': row['actorid'],
            'actorname': row['actorname'],
            'character': row['character'],
            'gender': row['gender'],
        })

    # get genres
    genre_query = select([table_genremovies, table_genres]).where(
        and_(
            table_genremovies.c.movieid == text(movieid),
            table_genremovies.c.genreid == table_genres.c.genreid,
        )
    )
    db_result = list(db_conn.execute(genre_query))
    movie_dict['genres'] = []
    for row in db_result:
        movie_dict['genres'].append({
            # 'genreid': row['genreid'],
            'genre': row['genre'],
        })

    return movie_dict


def db_parse_product(db_conn, product_id):
    product_dict = dict()

    query = select([table_products]).where(
        text("prod_id = " + str(product_id)))
    result = list(db_conn.execute(query))[0]

    product_dict['prod_id'] = result['prod_id']
    product_dict['movieid'] = result['movieid']
    product_dict['price'] = result['price']
    product_dict['description'] = result['description']

    # check stocks in inventory
    query = select([table_inventory]).where(
        text("prod_id = " + str(product_id)))
    result = list(db_conn.execute(query))

    if len(result) > 0:
        product_dict['stock'] = result[0]['stock']
        product_dict['sales'] = result[0]['sales']
    else:
        product_dict['stock'] = 0
        product_dict['sales'] = 0

    return product_dict


def db_load_movies(num_films):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_movies]).limit(num_films)
    result = list(db_conn.execute(query))

    movie_list = []
    for row in result:
        movieid = row['movieid']
        movie_dict = db_parse_movie(db_conn, movieid)
        movie_list.append(movie_dict)

    db_conn.close()
    return movie_list


def db_load_movie_by_id(movie_id):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    movie_dict = db_parse_movie(db_conn, movie_id)

    db_conn.close()
    return movie_dict


def db_load_product_by_id(product_id):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    product_dict = db_parse_product(db_conn, product_id)

    db_conn.close()
    return product_dict


def db_user_already_exists(username):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    db_username = select([table_customers]).where(
        text("username = '" + username + "'"))
    db_result = db_conn.execute(db_username)

    db_conn.close()

    users = list(db_result)
    if len(users) == 0:
        return False

    return True


def db_login(username, password):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    db_username = select([table_customers]).where(
        text("username = '" + username + "'"))
    db_result = list(db_conn.execute(db_username))[0]

    db_conn.close()

    if db_result['password'] != password:
        return None

    user = dict()
    user['customerid'] = db_result['customerid']
    user['username'] = db_result['username']
    user['password'] = db_result['password']
    user['email'] = db_result['email']
    user['credit_card'] = db_result['creditcard']
    user['direccion_envio'] = db_result['address1']
    user['balance'] = db_result['balance']
    user['points'] = db_result['loyalty']

    print('LOGGED USER WITH CUSTOMERID: '+str(user['customerid']))

    return user


def db_add_user(username, password, email, credit_card, direccion_envio, balance):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    new_id = list(db_conn.execute(
        "SELECT max(customerid) FROM customers"))[0][0]
    new_id += 1

    query = table_customers.insert().\
        values(
            customerid=new_id, firstname=username, lastname=username,
            address1=direccion_envio, city='Getafe', country='Spain',
            region='Madrid', email=email, creditcardtype='VISA',
            creditcard=credit_card, creditcardexpiration='8/2030',
            username=username, password=password,
            loyalty=0, balance=balance
    )
    db_conn.execute(query)

    db_conn.close()
    return True


def db_add_cart(customerid, prod_id):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_orders]).where(
        text('status is NULL and customerid = '+str(customerid)))
    result = list(db_conn.execute(query))
    if len(result) == 0:
        print('Error, cutomer with customerid' + str(customerid) +
              'does not have an associated order.')
        db_conn.close()
        return False

    orderid = result[0]['orderid']

    query = "select * from orderdetail where orderid="+str(orderid)+" and prod_id="+str(prod_id)+";"
    result = list(db_conn.execute(query))

    if len(result) == 0:
        # create new orderdetail
        query = select([table_products]).where(
            table_products.c.prod_id == prod_id)
        result = list(db_conn.execute(query))
        if len(result) == 0:
            print('There is no product with id ' +
                  str(prod_id) + ' in products table.')
            db_conn.close()
            return False
        price = result[0]['price']

        query = table_orderdetail.insert().\
            values(
                orderid=orderid, prod_id=prod_id,
                price = price, quantity=1,
            )
        db_conn.execute(query)

        query = "select * from orderdetail where orderid="+str(orderid)+" and prod_id="+str(prod_id)+";"
        result = list(db_conn.execute(query))
        print('NO PREVIOUS ORDERDETAIL, NOW:')
        print(result[0])

    elif len(result) >= 1:
        # update orderdetail
        query = table_orderdetail.update()\
            .where(table_orderdetail.c.prod_id == prod_id
                   and table_orderdetail.c.orderid == orderid)\
            .values(quantity=table_orderdetail.c.quantity + 1)

        db_conn.execute(query)
        print('PREVIOUS ORDERDETAIL:')
        print(result[0])
        query = "select * from orderdetail where orderid="+str(orderid)+" and prod_id="+str(prod_id)+";"
        result = list(db_conn.execute(query))
        print('NEW ORDERDETAIL:')
        print(result[0])

    db_conn.close()
    return True


def db_remove_cart(customerid, prod_id):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_orders]).where(
        text('status is NULL and customerid = '+str(customerid)))
    result = list(db_conn.execute(query))
    if len(result) == 0:
        print('Error, cutomer with customerid' + str(customerid) +
              'does not have an associated order.')
        db_conn.close()
        return False

    orderid = result[0]['orderid']

    query = "select * from orderdetail where orderid="+str(orderid)+" and prod_id="+str(prod_id)+";"
    result = list(db_conn.execute(query))

    if len(result) >= 1:
        # update orderdetail
        query = table_orderdetail.update()\
            .where(table_orderdetail.c.prod_id == prod_id
                   and table_orderdetail.c.orderid == orderid)\
            .values(quantity=table_orderdetail.c.quantity - 1)

        db_conn.execute(query)



        query = select([table_orderdetail])\
            .where(table_orderdetail.c.prod_id == prod_id
                   and table_orderdetail.c.orderid == orderid)
        result = list(db_conn.execute(query))[0]['quantity']
        print('RESULT QUANTITY')
        print(result)
        if result == 0:
            # delete order detail
            query = table_orderdetail.delete()\
            .where(table_orderdetail.c.prod_id == prod_id
                   and table_orderdetail.c.orderid == orderid)
            db_conn.execute(query)


    db_conn.close()
    return True


def db_empty_cart(customerid):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_orders]).where(
        text('status is NULL and customerid = '+str(customerid)))
    result = list(db_conn.execute(query))
    if len(result) == 0:
        print('Error, cutomer with customerid' + str(customerid) +
              'does not have an associated order.')
        db_conn.close()
        return False

    orderid = result[0]['orderid']

    query = "select * from orderdetail where orderid="+str(orderid)+";"
    result = list(db_conn.execute(query))

    db_conn.close()
    if len(result) == 0:
        return True
    return False


def db_replace_cart(cart, customerid):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'
    print('LOGGED USER WITH ANON CART. Products:')

    for prod_id in cart.keys():
        for i in range(cart[prod_id]):
            db_add_cart(customerid, prod_id)
    db_conn.close()


def db_product_get_info(prod_id):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    db_username = select([table_products]).where(text('prod_id='+str(prod_id)))
    result = list(db_conn.execute(db_username))[0]
    movieid = result['movieid']

    product_dict = dict()
    product_dict['movie'] = db_parse_movie(db_conn, movieid)
    product_dict['movieid'] = movieid
    product_dict['prod_id'] = prod_id
    product_dict['price'] = result['price']
    product_dict['description'] = result['description']

    db_conn.close()
    return product_dict


def db_get_user_cart(customerid):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_orders]).where(
        text('status is NULL and customerid = '+str(customerid)))
    result = list(db_conn.execute(query))[0]
    orderid = result['orderid']

    db_username = select([table_orderdetail]).where(text('orderid='+str(orderid)))
    result = list(db_conn.execute(db_username))

    product_list = []
    for row in result:
        prod_id = row['prod_id']
        product_dict = db_product_get_info(prod_id)
        product_dict['quantity'] = row['quantity']
        product_dict['total_price'] = product_dict['quantity'] * product_dict['price']
        product_list.append(product_dict)

    db_conn.close()
    return product_list


def db_get_cart_payment(customerid):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_orders]).where(
        text('status is NULL and customerid = '+str(customerid)))
    result = list(db_conn.execute(query))[0]
    return result['totalamount']


def db_check_enough_stock(orderid):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_orderdetail]).where(
        text('orderid = '+str(orderid)))
    result = list(db_conn.execute(query))

    for row in result:
        prod_id = row['prod_id']
        quantity = row['quantity']

        query = select([table_inventory]).where(
            text('prod_id = '+str(prod_id)))
        result = list(db_conn.execute(query))
        if len(result) == 0:
            return False

        if quantity > result[0]['stock']:
            return False
    return True


def db_try_buy_cart(customerid, payment_method, balance, points):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_orders]).where(
        text('status is NULL and customerid = '+str(customerid)))
    result = list(db_conn.execute(query))[0]
    total_payment =  result['totalamount']
    orderid = result['orderid']

    # check if enough points or balance
    if payment_method == 'balance':
        # update order status
        if total_payment > balance:
            return 'no_balance'

        # check there is enough amount of products
        if not db_check_enough_stock(orderid):
            return 'no_stock'

        query = table_orders.update()\
            .where(text("orderid = " + str(orderid)))\
            .values(status="Paid")
        db_conn.execute(query)

        dt = datetime.now(timezone.utc)
        query = 'INSERT INTO orders(orderdate, customerid, netamount, tax, totalamount, status)\
                VALUES (CURRENT_DATE, '+str(customerid)+', 0, 0, 0, NULL);'
        db_conn.execute(query)

        return 'success'

    elif payment_method == 'points':

        payment_in_points = total_payment * 100
        if points < payment_in_points:
            return 'no_points'

        # check there is enough amount of products
        if not db_check_enough_stock(orderid):
            return 'no_stock'

        # update customer's points and restore balance substracted by trigger
        query = table_customers.update()\
            .where(text('customerid = '+ str(customerid)))\
            .values(loyalty=table_customers.c.loyalty - payment_in_points - (total_payment * 5),
            balance=table_customers.c.balance + total_payment)
        db_conn.execute(query)

        query = table_orders.update()\
            .where(text("orderid = " + str(orderid)))\
            .values(status="Paid")
        db_conn.execute(query)

        dt = datetime.now(timezone.utc)
        query = 'INSERT INTO orders(orderdate, customerid, netamount, tax, totalamount, status)\
                VALUES (CURRENT_DATE, '+str(customerid)+', 0, 0, 0, NULL);'
        db_conn.execute(query)

        return 'success'


    else:
        return 'fail'


def db_add_balance(user, extra_money):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    customerid = str(user['customerid'])

    query = table_customers.update()\
            .where(text("customerid = " +customerid))\
            .values(balance=table_customers.c.balance + extra_money)
    db_conn.execute(query)

    db_conn.close()


def db_get_orders(customerid):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = select([table_orders]).where(
        text('status = \'Paid\' and customerid = '+str(customerid)))\
            .order_by(table_orders.c.orderdate)
    orders = db_conn.execute(query)

    order_list = []
    order_number = 1
    for row in orders:
        order = dict()
        order['order_number'] = order_number
        order['orderid'] = row['orderid']
        order['status'] = row['status']
        order['totalamount'] = row['totalamount']
        order['tax'] = row['tax']
        order['netamount'] = row['netamount']
        order['customerid'] = row['customerid']
        order['orderdate'] = row['orderdate']

        # get products for every order
        query = select([table_orderdetail]).where(text('orderid='+str(order['orderid'])))
        result = list(db_conn.execute(query))

        product_list = []
        for row in result:
            prod_id = row['prod_id']
            product_dict = db_product_get_info(prod_id)
            product_dict['quantity'] = row['quantity']
            product_dict['total_price'] = product_dict['quantity'] * product_dict['price']
            product_list.append(product_dict)

        order['product_list'] = product_list

        order_list.append(order)
        order_number += 1

    db_conn.close()
    return order_list

def db_search_movies(title, max_movies):
    db_conn = db_connect()
    if db_conn is None:
        return 'Something is broken'

    query = "select * from imdb_movies"
    query_result = list(db_conn.execute(query))

    db_conn.close()

    result_list = list(query_result)

    result = []
    counter = 0

    for movie in result_list:
        movie_dict = dict()
        if title.lower() in movie['movietitle'].lower() and counter < 20:
            movie_dict['movieid'] = movie['movieid']
            movie_dict['movietitle'] = movie['movietitle']
            movie_dict['image'] = film_image
            result.append(movie_dict)
            counter += 1

    return result
