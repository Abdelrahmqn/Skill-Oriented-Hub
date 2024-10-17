from flask import Blueprint, render_template
from app.models import User

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    NbUsers = User.query.count()
    return render_template('index.html', NbUsers=NbUsers)
