#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
from math import ceil
import json
import os
import sys
import random
import hashlib
import string

#Global variable
film_catalogue = json.loads(open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read())
#LIST o SET????
#cesta_usuario = []



def create_user_dict(username, salt, password, email, credit_card, balance) -> None:
    user_dictionary = dict()
    user_dictionary['username'] = username
    user_dictionary['salt'] = salt
    user_dictionary['password'] = password
    user_dictionary['email'] = email
    user_dictionary['credit_card'] = credit_card
    user_dictionary['balance'] = balance

    return user_dictionary

def update_user_data(user_dict):
    directory = os.getcwd() + "/users/" + user_dict['username'] + "/"
    if not os.path.exists(directory):
        return False

    file = open(directory + "data.json", "w") # erase its previous content  
    json.dump(user_dict, file)
    file.close()

    return True

def load_data_file(directory):
    file = open(directory)
    return json.load(file)

def get_random_string(length):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(alphabet) for i in range(length))
    return random_string





#Sustituir logged_user por get_actual_user()
def get_actual_user():
    if 'user' not in session:
        return None
    return session['user']

def get_cesta_sesion():
    if 'cesta' not in session:
        return None
    #Plantear cesta como diccionario
    return session['cesta']


@app.route('/')
@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    render_template('base.html', title = "Base", movies=film_catalogue['peliculas'], logged_user = get_actual_user())
    return render_template('inicio.html', title = "Home", movies=film_catalogue['peliculas'], logged_user = get_actual_user())

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        directory = os.getcwd() + "/users/" + username + "/"

        if not os.path.exists(directory):
            return render_template('login.html', title = "Sign In", logged_user = get_actual_user(), username_not_exists=True)
        else:
            directory += 'data.json'
            user_dict = load_data_file(directory)
            salt = user_dict['salt']
            hasehed_password = hashlib.blake2b((salt + password).encode('utf-8')).hexdigest()

            if hasehed_password == user_dict['password']:
                session['user'] = user_dict
                session.modified = True
                return redirect(url_for('inicio'))
            else:
                return render_template('login.html', title = "Sign In", logged_user = get_actual_user(), incorrect_password=True)

    else:
        return render_template('login.html', title = "Sign In", logged_user = get_actual_user())

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repeated_password = request.form['repeated_password']
        email = request.form['email']
        credit_card = request.form['credit_card']

        # password hashed before stored
        salt = get_random_string(32)
        password = hashlib.blake2b((salt + password).encode('utf-8')).hexdigest()
        
        # the balance is a random number
        balance = random.random() * 100
        balance = round(balance, 2)

        user_dict = create_user_dict(username, salt, password, email, credit_card, balance)

        directory = os.getcwd() + "/users/" + user_dict['username'] + "/"

        if not os.path.exists(directory):
            # si el directorio users aun no esta creado lo creamos
            if not os.path.exists(os.getcwd() + "/users"):
                os.mkdir(os.getcwd() + "/users")
            os.mkdir(directory)
        else:
            return render_template('register.html', title = "Register", logged_user = get_actual_user(), username_already_exists=True)

        update_user_data(user_dict)

        return redirect(url_for('login'))

    else:
        return render_template('register.html', title = "Register", logged_user = get_actual_user())

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('inicio'))

@app.route('/film/<id>', methods=['GET', 'POST'])
def film(id):
    """suponiendo que los ids de las pelis se dan en orden"""
    position = int(id) - 1
    movie = film_catalogue['peliculas'][position]

    return render_template('film.html', title = "Film", movie = movie, movies=film_catalogue['peliculas'], logged_user = get_actual_user())

@app.route('/busqueda', methods=['GET', 'POST'])
def buscar():
    movie = None
    busq = request.form['busqueda']
    if not busq:
        return render_template('error_busqueda.html', title = "Error Searched Film", movies=film_catalogue['peliculas'], logged_user = get_actual_user())

    movie_list_result = []
    for pelicula in film_catalogue['peliculas']:
        if busq.lower() in pelicula.get("titulo").lower():
            movie_list_result.append(pelicula)

    render_template('base.html', title = "Base", movies=film_catalogue['peliculas'], logged_user = get_actual_user())
    return render_template('resultado_busqueda.html', title = "Searched Film", movie_list = movie_list_result, movies=film_catalogue['peliculas'], logged_user = get_actual_user())

@app.route('/anadido_cesta/<id>', methods=['GET', 'POST'])
def anadir_cesta(id):
    cesta = get_cesta_sesion()
    if not cesta:
        session['cesta'] = dict()
        cesta = get_cesta_sesion()

    if id in cesta.keys():
        cesta[id] += 1

    else:
        cesta[id] =  1

    session.modified = True
    return render_template('anadido_cesta.html', title = "Basket Add", movies=film_catalogue['peliculas'], logged_user = get_actual_user())

@app.route('/cesta', methods=['GET', 'POST'])
def cesta():
    if not get_cesta_sesion():
        return render_template('cesta_vacia.html', title = "Empty Basket", movies=film_catalogue['peliculas'], logged_user = get_actual_user())
    else:
        cesta = get_cesta_sesion()
        lista_cesta = []
        for id in cesta.keys():
            position = int(id) - 1
            movie = film_catalogue['peliculas'][position]
            lista_cesta.append((movie, cesta[id]))
        return render_template('cesta.html', title = "Basket", cesta = lista_cesta, movies=film_catalogue['peliculas'], logged_user = get_actual_user())

@app.route('/comfirmar_cesta', methods=['GET', 'POST'])
def comfirmar_cesta():
    if not get_cesta_sesion():
        return render_template('cesta_vacia.html', title = "Empty Basket", movies=film_catalogue['peliculas'], logged_user = get_actual_user())
    else:
        cesta = get_cesta_sesion()
        lista_cesta = []
        pago = 0
        for id in cesta.keys():
            position = int(id) - 1
            movie = film_catalogue['peliculas'][position]
            pago += cesta[id] * movie['precio']
            lista_cesta.append((movie, cesta[id]))
        return render_template('comfirmar_cesta.html', title = "Buy Basket", cesta = lista_cesta, movies=film_catalogue['peliculas'], 
                                logged_user = get_actual_user(), pago=pago)


@app.route('/compra_finalizada', methods=['GET', 'POST'])
def compra_finalizada():
    cesta = get_cesta_sesion()
    lista_cesta = []
    pago = 0
    for id in cesta.keys():
        position = int(id) - 1
        movie = film_catalogue['peliculas'][position]
        pago += cesta[id] * movie['precio']
        lista_cesta.append((movie, cesta[id]))

    user_dict = session['user']

    if user_dict['balance'] - pago < 0:
        return render_template('comfirmar_cesta.html', title = "Buy Basket", cesta = lista_cesta, movies=film_catalogue['peliculas'], 
                                logged_user = get_actual_user(), pago=pago)

    user_dict['balance'] -= pago 
    user_dict['balance'] = round(user_dict['balance'], 2) 
    update_user_data(user_dict)
    session['cesta'] = dict()
    return render_template('compra_finalizada.html', title = "Buy Basket", cesta = lista_cesta, movies=film_catalogue['peliculas'], 
                            logged_user = get_actual_user(), pago=pago)

@app.route('/eliminado_cesta/<id>', methods=['GET', 'POST'])
def eliminado_cesta(id):
    cesta = get_cesta_sesion()
    if cesta[id] == 1:
        cesta.pop(id, None)
    else:
        cesta[id] -= 1
    session.modified=True
    return render_template('eliminado_cesta.html', title = "Basket Removed", movies=film_catalogue['peliculas'], logged_user = get_actual_user())
