import docker
from flask import jsonify, Blueprint, request
from app.docker.docker_client import DockerClient

app = Blueprint('docker', __name__)

docker_client = DockerClient()


# get到所有的container
@app.route('/containers', methods=['GET'])
def list_containers():
    return docker_client.list_containers()


# get到所有images
@app.route('/images', methods=['GET'])
def get_images():
    return docker_client.list_images()


# 启动指定容器
@app.route('/start/<container_id>', methods=['POST'])
def start_container(container_id):
    return docker_client.start_container(container_id)


# 停止指定容器
@app.route('/stop/<container_id>', methods=['POST'])
def stop_container(container_id):
    return docker_client.stop_container(container_id)


# 重启指定容器
@app.route('/restart/<container_id>', methods=['POST'])
def restart_container(container_id):
    return docker_client.restart_container(container_id)


# 查看指定容器的详细信息
@app.route('/<container_id>', methods=['GET'])
def get_container_details(container_id):
    return docker_client.get_container_details(container_id)


# 查看 Docker 容器健康状态
@app.route('/health/<container_id>', methods=['GET'])
def get_container_health(container_id):
    return docker_client.get_container_health(container_id)


# 查看容器日志接口
@app.route('/logs/<container_id>', methods=['GET'])
def get_container_logs(container_id):
    return docker_client.get_container_logs(container_id)


# 删除容器接口
@app.route('/delete/<container_id>', methods=['DELETE'])
def delete_container(container_id):
    return docker_client.delete_container(container_id)


# 查看docker网络接口
@app.route('/networks', methods=['GET'])
def list_networks():
    return docker_client.list_networks()


# 下载镜像接口
@app.route('/images/download', methods=['POST'])
def download_image():
    data = request.get_json()
    image_id = data.get('image_id')
    tar_name = data.get("tar_name")
    if not image_id:
        return jsonify({"error": "Image ID is required"}), 400
    try:
        # 保存镜像到本地路径
        return docker_client.download_image(image_id, tar_name)
    except docker.errors.ImageNotFound:
        return jsonify({'error': 'Image not found'}), 404


# 删除镜像接口
@app.route('/deleteImg/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    return docker_client.delete_image(image_id)


@app.route('/create', methods=['POST'])
def create_container():
    data = request.get_json()
    return docker_client.create_container(data)


@app.route('/addImg', methods=['POST'])
def add_container():
    data = request
    return docker_client.add_images(data)
