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
from datetime import datetime


# Global variable
film_catalogue = json.loads(open(os.path.join(
    app.root_path, 'catalogue/catalogue.json'), encoding="utf-8").read())


def create_user(username, salt, password, email, credit_card,
                direccion_envio, balance) -> None:
    user_dictionary = dict()

    data = dict()
    data['username'] = username
    data['salt'] = salt
    data['password'] = password
    data['email'] = email
    data['credit_card'] = credit_card
    data['direccion_envio'] = direccion_envio
    data['balance'] = balance
    data['points'] = 0

    user_dictionary['data'] = data
    user_dictionary['shopping_history'] = [dict()]

    return user_dictionary


def update_user_data(user):
    directory = os.getcwd() + "/users/" + user['data']['username'] + "/"
    if not os.path.exists(directory):
        return False

    file = open(directory + "data.dat", "w")  # erase its previous content
    json.dump(user['data'], file)
    file.close()

    # erase its previous content
    file = open(directory + "historial.json", "w")
    json.dump(user['shopping_history'], file)
    file.close()

    return True


def load_user(directory):
    user = dict()

    file = open(directory + 'data.dat')
    user['data'] = json.load(file)
    file.close()

    file = open(directory + 'historial.json')
    user['shopping_history'] = json.load(file)
    file.close()

    return user


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
    return render_template('inicio.html', title="Home",
                           movies=film_catalogue['peliculas'],
                           logged_user=get_actual_user())


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        directory = os.getcwd() + "/users/" + username + "/"

        if not os.path.exists(directory):
            return render_template('login.html', title="Sign In",
                                   logged_user=get_actual_user(),
                                   username_not_exists=True)
        else:
            user = load_user(directory)
            user_data = user['data']
            salt = user_data['salt']
            hasehed_password = hashlib.blake2b(
                (salt + password).encode('utf-8')).hexdigest()

            if hasehed_password == user_data['password']:
                session['user'] = user
                session.modified = True
                return redirect(url_for('inicio'))
            else:
                return render_template('login.html', title="Sign In",
                                       logged_user=get_actual_user(),
                                       incorrect_password=True)

    else:
        return render_template('login.html', title="Sign In",
                               logged_user=get_actual_user())


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repeated_password = request.form['repeated_password']
        email = request.form['email']
        credit_card = request.form['credit_card']
        direccion_envio = request.form['direccion_envio']

        # password hashed before stored
        salt = get_random_string(32)
        password = hashlib.blake2b(
            (salt + password).encode('utf-8')).hexdigest()

        # the balance is a random number
        balance = random.random() * 100
        balance = round(balance, 2)

        user = create_user(username, salt, password, email,
                           credit_card, direccion_envio, balance)

        directory = os.getcwd() + "/users/" + user['data']['username'] + "/"

        if not os.path.exists(directory):
            # si el directorio users aun no esta creado lo creamos
            if not os.path.exists(os.getcwd() + "/users"):
                os.mkdir(os.getcwd() + "/users")
            os.mkdir(directory)
        else:
            return render_template('register.html', title="Register",
                                   logged_user=get_actual_user(),
                                   username_already_exists=True)

        update_user_data(user)

        return redirect(url_for('login'))

    else:
        return render_template('register.html', title="Register",
                               logged_user=get_actual_user())


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'user' in session:
        session.pop('user', None)

    session['cesta'] = dict()
    session.modified = True
    return redirect(url_for('inicio'))


@app.route('/film/<id>', methods=['GET'])
def film(id):
    """suponiendo que los ids de las pelis se dan en orden"""
    position = int(id) - 1
    movie = film_catalogue['peliculas'][position]

    return render_template('film.html', title="Film", movie=movie,
                           movies=film_catalogue['peliculas'],
                           logged_user=get_actual_user())


@app.route('/busqueda', methods=['GET', 'POST'])
def buscar():
    movie = None
    busq = request.form['busqueda']
    if not busq:
        return render_template('error_busqueda.html',
                               title="Error Searched Film",
                               movies=film_catalogue['peliculas'],
                               logged_user=get_actual_user())

    movie_list_result = []
    for pelicula in film_catalogue['peliculas']:
        if busq.lower() in pelicula.get("titulo").lower():
            movie_list_result.append(pelicula)

    if not movie_list_result:
        return render_template('error_busqueda.html',
                               title="Error Searched Film",
                               movies=film_catalogue['peliculas'],
                               logged_user=get_actual_user())

    return render_template('resultado_busqueda.html', title="Searched Film",
                           movie_list=movie_list_result,
                           movies=film_catalogue['peliculas'],
                           logged_user=get_actual_user())


@app.route('/anadido_cesta/<id>', methods=['GET'])
def anadir_cesta(id):
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
                           movies=film_catalogue['peliculas'],
                           logged_user=get_actual_user())


@app.route('/cesta')
def cesta():
    if not get_cesta_sesion():
        return render_template('cesta_vacia.html', title="Empty Basket",
                               movies=film_catalogue['peliculas'],
                               logged_user=get_actual_user())
    else:
        cesta = get_cesta_sesion()
        lista_cesta = []
        for id in cesta.keys():
            position = int(id) - 1
            movie = film_catalogue['peliculas'][position]
            lista_cesta.append((movie, cesta[id]))
        return render_template('cesta.html', title="Basket", cesta=lista_cesta,
                               movies=film_catalogue['peliculas'],
                               logged_user=get_actual_user())


@app.route('/historial_compra', methods=['GET', 'POST'])
def historial_compra():
    if request.method == 'POST':
        extra_money = request.form['saldo']
        user_data = session['user']['data']

        try:
            extra_money = float(extra_money)
        except ValueError:
            return redirect(url_for('historial_compra'))

        if extra_money < 0:
            return redirect(url_for('historial_compra'))

        user_data['balance'] += float(extra_money)
        user_data['balance'] = round(user_data['balance'], 2)
        update_user_data(session['user'])
        session.modified = True
        return redirect(url_for('historial_compra'))

    else:
        shopping_history = session['user']['shopping_history']
        shopping_list = []
        counter = 1
        for pedido in shopping_history:
            if pedido:
                film_list = []
                dinero_pedido = 0
                for id in pedido.keys():
                    position = int(id) - 1
                    movie = film_catalogue['peliculas'][position]
                    film_list.append((movie, pedido[id]))
                    dinero_pedido += (movie['precio'] * pedido[id])

                shopping_list.append((str(counter), film_list, dinero_pedido))
                print(shopping_list)
                counter += 1

        return render_template('historial_compra.html', title="Basket",
                               shopping_list=shopping_list,
                               movies=film_catalogue['peliculas'],
                               logged_user=get_actual_user())


@app.route('/comfirmar_cesta')
def comfirmar_cesta():
    if not get_cesta_sesion():
        return render_template('cesta_vacia.html', title="Empty Basket",
                               movies=film_catalogue['peliculas'],
                               logged_user=get_actual_user())
    else:
        if 'user' in session:
            cesta = get_cesta_sesion()
            lista_cesta = []
            pago = 0
            for id in cesta.keys():
                position = int(id) - 1
                movie = film_catalogue['peliculas'][position]
                pago += cesta[id] * movie['precio']
                lista_cesta.append((movie, cesta[id]))
            return render_template('comfirmar_cesta.html', title="Buy Basket",
                                   cesta=lista_cesta,
                                   movies=film_catalogue['peliculas'],
                                   logged_user=get_actual_user(), pago=pago)
        else:
            return redirect(url_for('login'))


@app.route('/compra_finalizada/<way>', methods=['GET', 'POST'])
def compra_finalizada(way):
    if way != 'points' and way != 'balance':
        return

    buy = False

    cesta = get_cesta_sesion()
    lista_cesta = []
    pago = 0
    for id in cesta.keys():
        position = int(id) - 1
        movie = film_catalogue['peliculas'][position]
        pago += cesta[id] * movie['precio']
        lista_cesta.append((movie, cesta[id]))

    user = session['user']
    user_data = user['data']
    aux = (user_data['balance'] - pago)

    if way == 'balance':
        if (user_data['balance'] - pago) >= 0:
            user_data['balance'] -= pago
            user_data['balance'] = round(user_data['balance'], 2)

            points = (pago * 100) * 0.05
            points = round(points)
            user_data['points'] += points
            buy = True

    elif way == 'points':
        pago_en_puntos = round(pago * 100)
        if (user_data['points'] - pago_en_puntos) >= 0:
            user_data['points'] -= pago_en_puntos
            buy = True

    if buy:
        # actualizar historial de compras
        shopping_history = user['shopping_history']
        shopping_history.append(session['cesta'])

        update_user_data(user)
        session['cesta'] = dict()

        session.modified = True

        return render_template('compra_finalizada.html', title="Buy Basket",
                               cesta=lista_cesta,
                               movies=film_catalogue['peliculas'],
                               logged_user=get_actual_user(), pago=pago)

    return render_template('compra_fallida.html', title="Buy Basket",
                           cesta=lista_cesta,
                           movies=film_catalogue['peliculas'],
                           logged_user=get_actual_user(), way=way)


@app.route('/eliminado_cesta/<id>', methods=['GET'])
def eliminado_cesta(id):
    cesta = get_cesta_sesion()
    if cesta[id]:
        if cesta[id] == 1:
            cesta.pop(id, 0)
        else:
            cesta[id] -= 1
    session.modified = True
    return render_template('eliminado_cesta.html', title="Basket Removed",
                           movies=film_catalogue['peliculas'],
                           logged_user=get_actual_user())


@app.route('/online_users', methods=['GET'])
def get_random_number_of_users():
    return str(randint(10, 500))
