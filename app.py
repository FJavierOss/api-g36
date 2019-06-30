from flask import Flask, render_template, request, abort, json, redirect, flash
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import os
import atexit
import subprocess
import datetime
import json as json2


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
    return json2.dumps(jobj.get_json())
    for char in mmlist:
        sub_rstring = '{'
        for par in char.items():
            if "date" in par:
                if isinstance(par[1], str):
                    rstring += f'{sub_rstring}\"{par[0]}\": \"{par[1]}\"'

                else:
                    rstring += f'{sub_rstring}\"{par[0]}\": {par[1]}'

                #elif True in [check in par for check in paint]:
                #    rstring += f', <font color="red">\"{par[0]}\":</font> {par[1]}'

            elif "message" in par:
                if isinstance(par[1], str):
                    rstring += f',\"{par[0]}\": \"{par[1]}\"'

                else:
                    rstring += f',\"{par[0]}\": {par[1]}'
            else:
                rstring += f',\"{par[0]}\": {par[1]}'
        rstring += '}'
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

@app.route("/users_messages_rec/<int:uid>")
def get_users_messages_rec(uid):
    u_messages = list(mensajes.find({"receptant" : uid}, {"_id" : 0}))
    return manage_messages(json.jsonify(u_messages), ["receptant"])

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

@app.route("/msgs_location/<string:msg_info>")
def get_messages_location(msg_info):
    msg_info = msg_info.split('&&')
    uid = int(msg_info[0])
    return(str(uid))
    all_msgs = list(mensajes.find({"sender":uid},{}))
    date_min = datetime.datetime.strptime(msg_info[1][2:],"%y-%m-%d")
    date_max = datetime.datetime.strptime(msg_info[2][2:],"%y-%m-%d")
    res_msgs = [x for x in all_msgs if date_min < datetime.datetime.strptime(x["date"][2:],"%y-%m-%d") and date_max > datetime.datetime.strptime(x["date"][2:],"%y-%m-%d") ]
    print(type(res_msgs))
    return manage_messages(json.jsonify(res_msgs), ["message"])

@app.route("/add_message/<string:attrs>", methods=['GET', 'POST'])
def add_message(attrs):
    #print(id_1, id_2, contenido, mensajes.count_documents({}) + 1, datetime.datetime.now().date())
    attrs = attrs.split('&&')
    dict_message = {"mid": mensajes.count_documents({}) + 1 , "sender": int(attrs[0]),
    "receptant": int(attrs[1]), "date": str(datetime.datetime.now().date()),
    "lat": float(attrs[2]), "long": float(attrs[3]),
    "message": attrs[4]}
    check = True
    if not(attrs[0].isdigit() and attrs[1].isdigit()):
        check = False

    if check and mensajes.insert_one(dict_message):
        mensajje = "Mensaje creado"
        success = True

    else:
        mensajje = "No se pudo crear el mensaje"
        success = False

    resultado = [{"mensaje": mensajje, "resultado": success}]


    return manage_messages(json.jsonify(resultado), ["add_message"])


@app.route('/pop_message/<int:mid>', methods=['POST', 'GET', 'DELETE'])
def delete_message(mid):
    #print("Entra")
    #print(mid)
    resp = mensajes.delete_one({"mid" : int(mid)})

    if resp.deleted_count:
        messaje = f'Mensaje con id={mid} ha sido eliminado'
    else:
        messaje = f'No se han eliminado mensajes'
    #print(resp)

    resultado = [{"mensaje": messaje}]
    return manage_messages(json.jsonify(resultado), ["pop_message"])


if os.name == 'nt':
    app.run(debug=True)
