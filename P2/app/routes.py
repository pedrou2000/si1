#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
from math import ceil
import json
import os
import sys
from random import *
import random
import hashlib
import string
from app import database


# Global variable
max_movies = 20
movie_catalog = database.db_load_movies(max_movies)

users_directory = os.getcwd() + "/app/users/"

categorias = database.db_get_genres()
product_list = []
total_payment = 0


def create_user(username, password, email, credit_card,
                direccion_envio, balance) -> None:
    user_dict = dict()

    user_dict['username'] = username
    user_dict['password'] = password
    user_dict['email'] = email
    user_dict['credit_card'] = credit_card
    user_dict['direccion_envio'] = direccion_envio
    user_dict['balance'] = balance
    user_dict['points'] = 0

    return user_dict


def update_user_data():
    if 'user' in session:
        user_dict = session['user']
        session['user'] = database.db_login(user_dict['username'], user_dict['password'])
    else:
        print('Error, cannot update user because there is no user')


def get_random_string(length):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(alphabet) for i in range(length))
    return random_string


def get_actual_user():
    if 'user' not in session:
        return None
    return session['user']


def get_cesta_sesion():
    if 'cesta' not in session:
        return None

    return session['cesta']


@app.route('/')
@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    if request.method == 'GET':
        topActors = database.db_getTopActors('Action', 10)
        return render_template('inicio.html', title="Home",
                               movie_catalog=movie_catalog,
                               categorias=categorias,
                               logged_user=get_actual_user(),
                               topActors=topActors)
    else:
        genre = 'Action'
        num_movies = 10

        if request:
            print('REQUEST FORM:')
            print(request.form)
            if 'filter_actors' in request.form.keys():
                form_genre = request.form['filter_actors']
                if form_genre and form_genre != "Filtrar por categoría":
                    genre = form_genre

            if 'number_movies' in request.form.keys():
                form_num_movies = request.form['number_movies']
                if form_num_movies and form_num_movies.isdigit():
                    num_movies = form_num_movies

        topActors = database.db_getTopActors(genre, num_movies)
        return render_template('inicio.html', title="Home",
                               movie_catalog=movie_catalog,
                               categorias=categorias,
                               logged_user=get_actual_user(),
                               topActors=topActors)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not database.db_user_already_exists(username):
            return render_template('login.html', title="Sign In",
                                   logged_user=get_actual_user(),
                                   categorias=categorias,
                                   username_not_exists=True)
        else:
            user = database.db_login(username, password)
            if user is None:
                return render_template('login.html', title="Sign In",
                                       logged_user=get_actual_user(),
                                       categorias=categorias,
                                       incorrect_password=True)
            else:
                cesta = get_cesta_sesion()
                if database.db_empty_cart(user['customerid']) and cesta:
                    database.db_replace_cart(cesta, user['customerid'])
                session['user'] = user
                session.modified = True
                return redirect(url_for('inicio'))

    else:
        return render_template('login.html', title="Sign In",
                               categorias=categorias,
                               logged_user=get_actual_user())


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        credit_card = request.form['credit_card']
        direccion_envio = request.form['direccion_envio']

        # the balance is a random number
        balance = random.random() * 100
        balance = round(balance, 2)

        user = create_user(username, password, email,
                           credit_card, direccion_envio, balance)

        directory = users_directory + user['username'] + "/"

        if not database.db_user_already_exists(username):
            database.db_add_user(username, password, email,
                                 credit_card, direccion_envio, balance)

            if database.db_user_already_exists(username):
                print('User created successfully')
            else:
                print('User not created successfully')
        else:
            return render_template('register.html', title="Register",
                                   categorias=categorias,
                                   logged_user=get_actual_user(),
                                   username_already_exists=True)

        return redirect(url_for('login'))

    else:
        return render_template('register.html', title="Register",
                               categorias=categorias,
                               logged_user=get_actual_user())


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'user' in session:
        session.pop('user', None)

    session['cesta'] = dict()
    session.modified = True
    return redirect(url_for('inicio'))


@app.route('/movie/<id>', methods=['GET'])
def movie(id):
    movie = database.db_load_movie_by_id(id)

    return render_template('movie_detail.html', title="movie", movie=movie,
                           categorias=categorias,
                           logged_user=get_actual_user())


@app.route('/busqueda', methods=['GET', 'POST'])
def buscar():
    busq = request.form['busqueda']
    if not busq:
        return redirect(url_for('inicio'))

    movie_list_result = database.db_search_movies(busq, max_movies)

    if not movie_list_result:
        return render_template('error_busqueda.html',
                               title="Error Searched Film",
                               categorias=categorias,
                               logged_user=get_actual_user())

    return render_template('resultado_busqueda.html', title="Searched Film",
                           movie_list=movie_list_result,
                           categorias=categorias,
                           logged_user=get_actual_user())


@app.route('/filtrado', methods=['GET', 'POST'])
def filtrar():
    movie_list_result = []
    categoria = request.form['filter']
    if categoria == "Filtrar por categoría":
        return redirect(url_for('inicio'))

    movie_list_result = database.db_filter_movies(categoria, max_movies)

    """
    for pelicula in movie_catalog:
        if pelicula['categoria'] == categoria:
            movie_list_result.append(pelicula)
    """

    return render_template('resultado_busqueda.html', title="Filtered Films",
                           movie_list=movie_list_result,
                           categorias=categorias,
                           logged_user=get_actual_user())


@app.route('/anadido_cesta/<id>', methods=['GET'])
def anadir_cesta(id):
    user = get_actual_user()
    if user:
        customerid = user['customerid']
        database.db_add_cart(customerid, id)
    else:
        cesta = get_cesta_sesion()
        if not cesta:
            session['cesta'] = dict()
            cesta = get_cesta_sesion()
        if id in cesta.keys():
            cesta[id] += 1
        else:
            cesta[id] = 1
        session.modified = True

    return render_template('anadido_cesta.html', title="Basket Add",
                           categorias=categorias,
                           logged_user=get_actual_user())


@app.route('/eliminado_cesta/<id>', methods=['GET'])
def eliminado_cesta(id):

    user = get_actual_user()
    if user:
        customerid = user['customerid']
        database.db_remove_cart(customerid, id)
    else:
        cesta = get_cesta_sesion()
        if cesta[id]:
            if cesta[id] == 1:
                cesta.pop(id, 0)
            else:
                cesta[id] -= 1
        session.modified = True
    
    return render_template('eliminado_cesta.html', title="Basket Removed",
                           categorias=categorias,
                           logged_user=get_actual_user())


@app.route('/cesta')
def cesta():
    cesta = get_cesta_sesion()
    user = get_actual_user()
    global product_list
    product_list = []

    if (not cesta and not user) or (user and database.db_empty_cart(user['customerid'])):
        return render_template('cesta_vacia.html', title="Empty Basket",
                               logged_user=get_actual_user())

    elif cesta and not user:
        print('cesta and not user')
        for prod_id in cesta.keys():
            product_info = database.db_product_get_info(prod_id)
            product_info['quantity'] = cesta[prod_id]
            product_info['total_price'] = product_info['quantity'] * product_info['price']
            product_list.append(product_info)

    elif user and not database.db_empty_cart(user['customerid']):
        print('user and not database.db_empty_cart()')
        product_list = database.db_get_user_cart(user['customerid'])
        print(product_list)

    return render_template('cesta.html', title="Basket", product_list=product_list,
                           logged_user=get_actual_user())


@app.route('/comfirmar_cesta')
def comfirmar_cesta():
    global product_list, total_payment
    user = get_actual_user()
    if user is not None:
        total_payment = database.db_get_cart_payment(user['customerid'])
        return render_template('comfirmar_cesta.html', title="Buy Basket",
                                product_list=product_list,
                                logged_user=get_actual_user(), 
                                total_payment=total_payment)
    else:
        return redirect(url_for('login'))


@app.route('/compra_finalizada/<way>', methods=['GET', 'POST'])
def compra_finalizada(way):
    global total_payment, product_list

    if way != 'points' and way != 'balance':
        print('Error, not selected way of payment!')
        return

    user = session['user']

    attempt_result = database.db_try_buy_cart(user['customerid'], way, user['balance'], user['points'])
    if attempt_result == 'success':
        update_user_data()
        return render_template('compra_finalizada.html', title="Buy Basket",
                               product_list=product_list,
                               logged_user=get_actual_user(), 
                               total_payment=total_payment)

    else:
        return render_template('compra_fallida.html', title="Buy Basket",
                            product_list=product_list,
                            logged_user=get_actual_user(), 
                            attempt_result=attempt_result,
                            total_payment=total_payment)

    
@app.route('/historial_compra', methods=['GET', 'POST'])
def historial_compra():
    user = session['user']
    if request.method == 'POST':
        extra_money = request.form['saldo']

        try:
            extra_money = float(extra_money)
        except ValueError:
            return redirect(url_for('historial_compra'))

        if extra_money < 0:
            return redirect(url_for('historial_compra'))

        database.db_add_balance(user, extra_money)        
        update_user_data()
        return redirect(url_for('historial_compra'))

    else:
        order_list = database.db_get_orders(user['customerid'])



        """
        shopping_history = session['user']['shopping_history']
        shopping_list = []
        counter = 1
        for pedido in shopping_history:
            if pedido:
                film_list = []
                dinero_pedido = 0
                for id in pedido.keys():
                    position = int(id) - 1
                    movie = movie_catalog[position]
                    film_list.append((movie, pedido[id]))
                    dinero_pedido += (movie['precio'] * pedido[id])

                shopping_list.append((str(counter), film_list, dinero_pedido))
                print(shopping_list)
                counter += 1
        """

        return render_template('historial_compra.html', title="Historial",
                               order_list=order_list,
                               logged_user=get_actual_user())


@app.route('/online_users', methods=['GET'])
def get_random_number_of_users():
    return str(randint(10, 500))
