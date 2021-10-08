#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
from math import ceil
import json
import os
import sys

#Global variable
film_catalogue = json.loads(open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read())
#LIST o SET????
cesta_usuario = []

@app.route('/')
@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    render_template('base.html', title = "Base", movies=film_catalogue['peliculas'])
    return render_template('inicio.html', title = "Home", movies=film_catalogue['peliculas'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return try_login()
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

def try_login():
    return

@app.route('/register')
def register():
    if request.method == 'POST':
        return try_register()
    else:
        return render_template('register.html', title = "Register")

def try_register():
    print("Trying to register!")
    return

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

@app.route('/film/<id>', methods=['GET', 'POST'])
def film(id):
    """suponiendo que los ids de las pelis se dan en orden"""
    position = int(id) - 1
    movie = film_catalogue['peliculas'][position]

    return render_template('film.html', title = "Film", movie = movie, movies=film_catalogue['peliculas'])

@app.route('/busqueda', methods=['GET', 'POST'])
def buscar():
    movie = None
    busq = request.form['busqueda']
    if not busq:
        return render_template('error_busqueda.html', title = "Error Searched Film", movies=film_catalogue['peliculas'])

    movie_list_result = []
    for pelicula in film_catalogue['peliculas']:
        if busq.lower() in pelicula.get("titulo").lower():
            movie_list_result.append(pelicula)

    render_template('base.html', title = "Base", movies=film_catalogue['peliculas'])
    return render_template('resultado_busqueda.html', title = "Searched Film", movie_list = movie_list_result, movies=film_catalogue['peliculas'])

@app.route('/anadido_cesta/<id>', methods=['GET', 'POST'])
def anadir_cesta(id):
    position = int(id) - 1
    movie = film_catalogue['peliculas'][position]
    cesta_usuario.append(movie)
    return render_template('anadido_cesta.html', title = "Basket Add", movies=film_catalogue['peliculas'])

@app.route('/cesta', methods=['GET', 'POST'])
def cesta():
    if not cesta_usuario:
        return render_template('cesta_vacia.html', title = "Empty Basket", movies=film_catalogue['peliculas'])
    return render_template('cesta.html', title = "Basket", cesta = cesta_usuario, movies=film_catalogue['peliculas'])

@app.route('/eliminado_cesta/<id>', methods=['GET', 'POST'])
def eliminado_cesta(id):
    position = int(id) - 1
    movie = film_catalogue['peliculas'][position]
    cesta_usuario.remove(movie)
    return render_template('eliminado_cesta.html', title = "Basket Removed", movies=film_catalogue['peliculas'])
