# -*- coding: utf-8 -*-
"""
:Authors:
    - qweqwe
"""

from flask_mongoengine import MongoEngine
from flaskext.mail import Mail
from techent.extensions.login_manager import login


mongoengine = MongoEngine()
mail_ext = Mail()

__all__ = ['login', 'mongoengine', 'mail_ext']