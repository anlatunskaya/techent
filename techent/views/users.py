# -*- coding: utf-8 -*-
from flask import Blueprint, url_for, redirect
from flask_login import logout_user, login_required

users = Blueprint('users', __name__)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.frontpage'))
