# -*- coding: utf-8 -*-
from techent import create_app
from techent.extensions import mongoengine, login, mail_ext
from techent.views.users import users
from techent.views.main import main
from techent.views.event import event
from techent.views.mail import mail
from techent import config
from techent.views.oauth import oauth

views = [
    (users, ''),
    (oauth, ''),
    (main, ''),
    (event, ''),
    (mail, '')
]
extensions = [
    mongoengine,
    login,
    mail_ext
]

def app_factory(extensions=extensions,
                views=views,
                config=config):

    app = create_app(extensions=extensions,
                     modules=views,
                     config=config)
    return app
