# -*- coding: utf-8 -*-
__author__ = 'alatynskaya'

from flask import Blueprint, url_for
from flaskext.mail import Message
from techent.extensions import *

mail = Blueprint("mail", __name__)

def send_event_invitation(event):
    msg = Message(
        'Invitation',
        sender='anlatunskaya@gmail.com',
        recipients=
        event.attendees)
    msg.body = "Hello! We invite you to come to the event in Grid Dynamics company. More information about this event you can get if follow the link." +\
               "http://www.techent.ru:5002" +url_for('event.show_event', event_id = event.id)
    mail_ext.send(msg)