from flask import Flask
from flask_cors import CORS
from app.routes import docker_routes, k8s_routes, welcome_routes

app = Flask(__name__)
CORS(app)
# 注册 Welcome 相关路由
app.register_blueprint(welcome_routes.app, url_prefix='/')

# 注册 Docker 相关路由
app.register_blueprint(docker_routes.app, url_prefix='/docker')

# 注册 Kubernetes 相关路由
app.register_blueprint(k8s_routes.app, url_prefix='/k8s')
