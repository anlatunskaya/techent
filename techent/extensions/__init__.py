# -*- coding: utf-8 -*-
"""
:Authors:
    - qweqwe
"""

from flask_mongoengine import MongoEngine
from flaskext.mail import Mail


mongoengine = MongoEngine()
mail_ext = Mail()
from techent.extensions.login_manager import login

__all__ = ['login', 'mongoengine', 'mail_ext']