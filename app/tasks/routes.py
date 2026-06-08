from flask import render_template

from app.tasks import bp


@bp.route('/')
def home():
        return render_template('home.html')