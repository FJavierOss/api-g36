from flask import Flask, render_template, request, abort, json, redirect, flash
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import os
import atexit
import subprocess
import datetime


USERS_KEYS = ['nombre', 'nacimiento', 'correo', 'nacionalidad', 'clave']
MESSAGE_KEYS = ['message', 'sender', 'receptant', 'lat', 'long', 'date']

#mongod = subprocess.Popen('mongod', stdout=subprocess.DEVNULL)
#atexit.register(mongod.kill)

app = Flask(__name__)
uri = "mongodb://grupo20:grupo20@146.155.13.149/grupo20?authSource=admin"
client = MongoClient(uri)
db = client.get_database()
mensajes = db.messages
usuarios = db.users


def manage_messages(jobj, paint=[]):
    mmlist = [char for char in jobj.get_json()]
    if not mmlist:
        return 'No hay mensajes que cumplan los requisitos pedidos'
    rstring = ''
    for char in mmlist:
        sub_rstring = '{'
        for par in char.items():
            if "date" in par:
                rstring += f'{sub_rstring}\"{par[0]}\": {par[1]}'
                #elif True in [check in par for check in paint]:
                #    rstring += f', <font color="red">\"{par[0]}\":</font> {par[1]}'
            else:
                rstring += f', \"{par[0]}\": {par[1]}'
        rstring += '}<br>'
    return rstring


@app.route("/")
def home():
    home_string =   "<h1> APPI's Main Page </h1>" + \
                    "<p> Welcome to our APPI, sadly until now we dont have " + \
                    "an user friendly insterface, so you must manualy " + \
                    "input the variables in the URL, follow this rules:</p>" + \
                    "<p> Use slash (/) to move between questions and at the " + \
                    "final one input your variables</p>" + \
                    "<p> Use double and sings (&&) to separate between variables. " + \
                    "for example: /dog&&cat&&mouse</p>"
    return home_string


@app.route("/messages/<int:mid>")
def get_message(mid):
    messages = list(mensajes.find({"mid" : mid}, {"_id" : 0}))
    return manage_messages(json.jsonify(messages), ["mid"])

@app.route("/users_messages/<int:uid>")
def get_users_messages(uid):
    u_messages = list(mensajes.find({"sender" : uid}, {"_id" : 0}))
    return manage_messages(json.jsonify(u_messages), ["sender"])

@app.route("/chat/<string:uids>")
def get_chat_between(uids):
    uids = uids.split('&&')
    uid_1 = int(uids[0])
    uid_2 = int(uids[1])
    chat_messages = list(mensajes.find({"sender" : uid_1, "receptant" : uid_2}, {"_id" : 0}))
    return manage_messages(json.jsonify(chat_messages), ["sender", "receptant"])

@app.route("/mustb_in_message/<string:unique_characters>")
def get_unique_message(unique_characters):
    unique_characters = unique_characters.split('&&')
    find_text = [f'\\"{char}"\\' for char in unique_characters]
    search_text = ' '.join(find_text)
    unique_messages = list(mensajes.find({"$text" : {"$search" : f'{search_text}'}}, {"_id" : 0}))
    return manage_messages(json.jsonify(unique_messages), ["message"])

@app.route("/muybe_in_message/<string:maybe_characters>")
def get_alike_message(maybe_characters):
    maybe_characters = maybe_characters.split('&&')
    search_text = ' '.join(maybe_characters)
    unique_messages = list(mensajes.find({"$text" : {"$search" : f'{search_text}'}}, {"_id" : 0}))
    return manage_messages(json.jsonify(unique_messages), ["message"])

@app.route("/not_in_message/<string:not_characters>")
def get_diff_message(not_characters):
    all_messages = list(mensajes.find({}, {"_id" : 0}))
    not_characters = not_characters.split('&&')
    find_text = [f'{char}' for char in not_characters]
    search_text = ' '.join(find_text)
    not_messages = list(mensajes.find({"$text" : {"$search" : f'{search_text}'}}, {"_id" : 0}))
    unique_messages = [char for char in all_messages if char not in not_messages]
    return manage_messages(json.jsonify(unique_messages), ["message"])


if os.name == 'nt':
    app.run(debug=True)
