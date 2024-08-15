from flask import Blueprint

app = Blueprint('welcome', __name__)


@app.route("/", methods=['GET'])
def welcome():
    return 'Welcome to the Kubernetes and Docker management system!'
