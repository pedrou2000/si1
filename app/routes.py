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

#Global variable
film_catalogue = json.loads(open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read())
#LIST o SET????
#cesta_usuario = []

class User:
    def __init__(self, username, password, email, credit_card, balance) -> None:
        self.username = username
        self.password = password
        self.email = email
        self.credit_card = credit_card
        self.balance = balance
        #self.basket = dict()

    def __repr__(self) -> str:
        return f'User: {self.username}'

#logged_user = None

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
            file = open(directory + 'data.dat',"r")
            lines = file.read().split('\n')
            hash = ""
            hasehed_password = hashlib.blake2b((hash + password).encode('utf-8')).hexdigest()

            if hasehed_password == lines[1]:
                session['username'] = username
                session.modified=True
                session['user'] = User(lines[0], lines[1], lines[2], lines[3], lines[4])
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

        directory = os.getcwd() + "/users/" + username + "/"

        if not os.path.exists(directory):
            # si el directorio users aun no esta creado lo creamos
            if not os.path.exists(os.getcwd() + "/users"):
                os.mkdir(os.getcwd() + "/users")

            os.mkdir(directory)
        else:
            return render_template('register.html', title = "Register", logged_user = get_actual_user(), username_already_exists=True)

        #salt = os.urandom(32).hexdigest()
        #salt = str(bcrypt.gensalt())
        salt = ""
        hasehed_password = hashlib.blake2b((salt + password).encode('utf-8')).hexdigest()

        file = open(directory + "data.dat", "w")
        file.write(username + '\n')

        file.write(hasehed_password + '\n')

        file.write(email + '\n')
        file.write(credit_card + '\n')

        balance = random.random() * 100
        file.write(str(balance) + '\n')

        file.close()


        return redirect(url_for('login'))

    else:
        return render_template('register.html', title = "Register", logged_user = get_actual_user())

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'username' in session:
        session.pop('username', None)
    session['user'] = None
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
        print("mas pelis ")
        print(cesta[id])
        session['cesta'][id] += 1

    else:
        print("nueva peli")
        session['cesta'][id] =  1
        print(cesta[id])

    print("cestita:")
    print(cesta)
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

@app.route('/eliminado_cesta/<id>', methods=['GET', 'POST'])
def eliminado_cesta(id):
    cesta = get_cesta_sesion()
    if cesta[id] == 1:
        cesta.pop(id, None)
    else:
        cesta[id] -= 1
    return render_template('eliminado_cesta.html', title = "Basket Removed", movies=film_catalogue['peliculas'], logged_user = get_actual_user())
