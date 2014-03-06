# -*- coding: utf-8 -*-
"""
    tailormade.api
    ~~~~~~~~~~~~~

    Server API for the game Tailormade

    :copyright: (c) 2013 by Saeed Abdullah.
"""

import tailormade
from tailormade import app
from flask import Blueprint, request, jsonify,\
        flash, render_template, redirect, url_for
from werkzeug import secure_filename
import flask_login

# View function for index

#@app.route("/shut")
#def shut():
#    return "shut"

def index():
    if request.method == 'OPTIONS':
        # custom options handling here
        a=0
    return 'Hello World!'
index.provide_automatic_options = False
index.methods = ['GET', 'OPTIONS']

app.add_url_rule('/', index)


"""
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")
"""

app.run()
