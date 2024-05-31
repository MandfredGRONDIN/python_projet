from flask import render_template, redirect, url_for
from db_utils import list_clients, get_client_info

def list_clients_utils():
    clients = list_clients()
    return render_template('list_clients.html', clients=clients)

def client_utils(client_id):
    client_info = get_client_info(client_id)

    if client_info:
        return render_template('client.html', client_info=client_info)
    else:
        return redirect(url_for('route.dashboard'))