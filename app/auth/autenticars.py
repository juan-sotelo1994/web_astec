from  flask import render_template, abort, session
from . import autenticar
from  flask import Flask, request,url_for,redirect, url_for, flash

@autenticar.route('/')
def login():
    return render_template('login.html')

@autenticar.route('/recupera')
def recupera():
    return render_template('recupera.html')

@autenticar.route('/verificacion')
def verificacion():
    return render_template('verificacion.html')

@autenticar.route('/newp')
def newp():
    return render_template('newp.html')