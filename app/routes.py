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
cesta_usuario = []

class User:
    def __init__(self, username, password, email, credit_card, balance) -> None:
        self.username = username 
        self.password = password
        self.email = email 
        self.credit_card = credit_card
        self.balance = balance
    
    def __repr__(self) -> str:
        return f'User: {self.username}'

logged_user = None

@app.route('/')
@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    global logged_user

    render_template('base.html', title = "Base", movies=film_catalogue['peliculas'], logged_user = logged_user)
    return render_template('inicio.html', title = "Home", movies=film_catalogue['peliculas'], logged_user = logged_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_user

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        directory = os.getcwd() + "/users/" + username + "/"

        if not os.path.exists(directory):
            return render_template('login.html', title = "Sign In", logged_user = logged_user, username_not_exists=True)
        else:
            file = open(directory + 'data.dat',"r")
            lines = file.read().split('\n')

            if lines[1] == password:
                session['username'] = username
                session.modified=True
                logged_user = User(lines[0], lines[1], lines[2], lines[3], lines[4])
                return redirect(url_for('inicio'))
            else:
                print(lines[1])
                print(password)
                return render_template('login.html', title = "Sign In", logged_user = logged_user, incorrect_password=True)
                
    else:
        return render_template('login.html', title = "Sign In", logged_user = logged_user)

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
            return render_template('register.html', title = "Register", logged_user = logged_user, username_already_exists=True)

        salt = 
        password = hashlib.blake2b((salt+password).encode('utf-8')).hexdigest()

        file = open(directory + "data.dat", "w")
        file.write(username + '\n')
        file.write(password + '\n')
        file.write(email + '\n')
        file.write(credit_card + '\n')

        balance = random.random() * 100
        file.write(balance + '\n')


        return redirect(url_for('login'))
    
    else:
        return render_template('register.html', title = "Register", logged_user = logged_user)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global logged_user    
    if 'username' in session:
        session.pop('username', None)
    logged_user = None
    return redirect(url_for('inicio'))

@app.route('/film/<id>', methods=['GET', 'POST'])
def film(id):
    """suponiendo que los ids de las pelis se dan en orden"""
    position = int(id) - 1
    movie = film_catalogue['peliculas'][position]

    return render_template('film.html', title = "Film", movie = movie, movies=film_catalogue['peliculas'], logged_user = logged_user)

@app.route('/busqueda', methods=['GET', 'POST'])
def buscar():
    movie = None
    busq = request.form['busqueda']
    if not busq:
        return render_template('error_busqueda.html', title = "Error Searched Film", movies=film_catalogue['peliculas'], logged_user = logged_user)

    movie_list_result = []
    for pelicula in film_catalogue['peliculas']:
        if busq.lower() in pelicula.get("titulo").lower():
            movie_list_result.append(pelicula)

    render_template('base.html', title = "Base", movies=film_catalogue['peliculas'], logged_user = logged_user)
    return render_template('resultado_busqueda.html', title = "Searched Film", movie_list = movie_list_result, movies=film_catalogue['peliculas'], logged_user = logged_user)

@app.route('/anadido_cesta/<id>', methods=['GET', 'POST'])
def anadir_cesta(id):
    position = int(id) - 1
    movie = film_catalogue['peliculas'][position]
    cesta_usuario.append(movie)
    return render_template('anadido_cesta.html', title = "Basket Add", movies=film_catalogue['peliculas'], logged_user = logged_user)

@app.route('/cesta', methods=['GET', 'POST'])
def cesta():
    if not cesta_usuario:
        return render_template('cesta_vacia.html', title = "Empty Basket", movies=film_catalogue['peliculas'], logged_user = logged_user)
    return render_template('cesta.html', title = "Basket", cesta = cesta_usuario, movies=film_catalogue['peliculas'], logged_user = logged_user)

@app.route('/eliminado_cesta/<id>', methods=['GET', 'POST'])
def eliminado_cesta(id):
    position = int(id) - 1
    movie = film_catalogue['peliculas'][position]
    cesta_usuario.remove(movie)
    return render_template('eliminado_cesta.html', title = "Basket Removed", movies=film_catalogue['peliculas'], logged_user = logged_user)
