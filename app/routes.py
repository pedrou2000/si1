#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
from math import ceil
import json
import os
import sys
from flask import g

#Global variable
film_catalogue = json.loads(open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read())
#LIST o SET????
cesta_usuario = []

class User:
    def __init__(self, username, password, email, credit_card) -> None:
        self.username = username 
        self.password = password
        self.email = email 
        self.credit_card = credit_card
    
    def __repr__(self) -> str:
        return f'User: {self.username}'

users = []
logged_user = "stringgg"

@app.route('/')
@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    logged_user = None
    if 'username' in session:
        logged_user = session['username']
    render_template('base.html', title = "Base", movies=film_catalogue['peliculas'], logged_user = logged_user)
    return render_template('inicio.html', title = "Home", movies=film_catalogue['peliculas'], logged_user = logged_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        for user in users:
            if user.username == username:
                if user.password == password:
                    session['username'] = username
                    session.modified=True
                    logged_user = user
                    g.user = user
                    return render_template('inicio.html', title = "Home", movies=film_catalogue['peliculas'], logged_user = session['username'])
        
        return redirect(url_for('login'))
                

    else:
        return render_template('login.html', title = "Sign In")

    """
    # doc sobre request object en http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
    if 'username' in request.form:
        # aqui se deberia validar con fichero .dat del usuario
        if request.form['username'] == 'pp':
            session['usuario'] = request.form['username']
            session.modified=True
            # se puede usar request.referrer para volver a la pagina desde la que se hizo login
            return redirect(url_for('index'))
        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return render_template('login.html', title = "Sign In")
    else:
        # se puede guardar la pagina desde la que se invoca
        session['url_origen']=request.referrer
        session.modified=True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
    """

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
            if not os.path.exists(os.getcwd() + "/users"):
                os.mkdir(os.getcwd() + "/users")
            os.mkdir(directory)
            print("Directory " , directory ,  " Created ")
        else:    
            print("Directory " , directory ,  " already exists")

        fptr = open(directory + "data.dat", "w")
        fptr.write(username + '\n')
        fptr.write(password + '\n')
        fptr.write(email + '\n')
        fptr.write(credit_card + '\n')

        for user in users:
            if user.email == email:
                return redirect(url_for('register'))

        user = User(username, password, email, credit_card)
        users.append(user)

        

        return redirect(url_for('login'))
    else:
        return render_template('register.html', title = "Register")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'username' in session:
        session.pop('username', None)
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
