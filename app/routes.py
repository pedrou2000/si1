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

@app.route('/')
@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    print (url_for('static', filename='/static/css/estilo.css'), file=sys.stderr)
    print(len(film_catalogue['peliculas']))
    return render_template('inicio.html', title = "Home", movies=film_catalogue['peliculas'])

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    return render_template('login.html', title = "Sign In")

@app.route('/register')
def register():
    return render_template('register.html', title = "Register")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

@app.route('/film/<id>', methods=['GET', 'POST'])
def film(id):
    """suponiendo que los ids de las pelis se dan en orden"""
    position = int(id) - 1
    movie = film_catalogue['peliculas'][position]
    return render_template('film.html', title = "Film", movie=movie)
