import json
import os

import docker
from flask import jsonify, send_file, Response
from tempfile import NamedTemporaryFile


class DockerClient:
    def __init__(self):
        self.client = docker.from_env()

    # 所有的containers
    def list_containers(self):
        containers = self.client.containers.list(all=True)
        container_list = []
        for container in containers:
            image_tag = container.image.tags[0] if container.image.tags else '<none>'
            container_list.append({
                'id': container.id,
                'name': container.name,
                'image': image_tag,
                'command': container.attrs['Config']['Cmd'],
                'created': container.attrs['Created'],
                'status': container.status,
                'ports': container.attrs['HostConfig']['PortBindings']
            })
        return jsonify(container_list)

    # 所有的images
    def list_images(self):
        images = self.client.images.list()
        image_list = []
        for image in images:
            tags = image.tags
            if not tags:  # 如果没有标签，则设置为 '<none>'
                tags = ['<none>']
            for tag in tags:
                image_list.append({
                    'repository': tag.split(':')[0],
                    'tag': tag.split(':')[1] if len(tag.split(':')) > 1 else '<none>',
                    'image_id': image.id,
                    'created': image.attrs['Created'],
                    'size': image.attrs['Size']
                })
        return jsonify(image_list)

    # 启动指定容器
    def start_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.start()
        return jsonify({'message': 'Container started successfully'})

    # 停止指定容器
    def stop_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.stop()
        return jsonify({'message': 'Container stopped successfully'})

    # 重启指定容器
    def restart_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.restart()
        return jsonify({'message': 'Container restarted successfully'})

    # 指定容器详细信息
    def get_container_details(self, container_id):
        container = self.client.containers.get(container_id)
        return jsonify(container.attrs)

    # 查看docker的健康状况
    def get_container_health(self, container_id):
        container = self.client.containers.get(container_id)
        return jsonify(container.stats(stream=False))

    # 查看容器日志接口
    def get_container_logs(self, container_id):
        container = self.client.containers.get(container_id)
        strLog = str(container.logs(), encoding='utf-8')
        return strLog

    # 删除容器接口
    def delete_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.remove()
        return jsonify({'message': 'Container deleted successfully'})

    # 查看docker网络接口
    def list_networks(self):
        networks = self.client.networks.list()
        return jsonify([network.attrs for network in networks])

    # 增加镜像
    def add_images(self, data):
        if 'tar_file' not in data.files or 'container_name' not in data.form:
            return jsonify({'error': 'No tar file or container name provided'}), 400

        tar_file = data.files['tar_file']
        container_name = data.form['container_name']

        tar_path = os.path.join('./', tar_file.filename)
        tar_file.save(tar_path)

        try:
            with open(tar_path, 'rb') as f:
                self.client.images.load(f)
            os.remove(tar_path)
            # self.client.containers.run(tar_file.filename.split('.')[0], name=container_name, detach=True)
            return jsonify({'message': 'Container added successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def download_image(self, image_id, tar_name):
        if not image_id:
            return jsonify({'error': 'Image name is required'}), 400
        try:
            image = self.client.images.get(image_id)
            image_tar = image.save(named=True)

            def generate():
                for chunk in image_tar:
                    yield chunk

            response = Response(generate(), mimetype='application/x-tar')
            response.headers.set('Content-Disposition', 'attachment', filename=f"{tar_name}.tar")
            return response
        except docker.errors.ImageNotFound:
            return jsonify({"error": "Image not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # 删除镜像
    def delete_image(self, image_id):
        try:
            # 删除镜像之前需要先删除所有使用该镜像的容器
            for container in self.client.containers.list(all=True):
                if container.image.id == image_id:
                    container.remove(force=True)
            # 删除镜像
            self.client.images.remove(image_id)
            return jsonify({'message': 'Image deleted successfully'})
        except docker.errors.ImageNotFound:
            return jsonify({'error': 'Image not found'}), 404
        except docker.errors.APIError as e:
            return jsonify({'error': str(e)}), 500

    def create_container(self, container_info):
        data = container_info
        container_name = data.get('name')
        image_name = data.get('image')
        command = data.get('command')
        port = data.get('port')
        mapping = data.get('mapping')
        environment_variables = data.get('environmentVariables')
        try:
            # Create the container
            container = self.client.containers.create(
                image=image_name,
                name=container_name,
                command=command,
                ports={port: mapping},
                detach=True  # Run container in detached mode
            )
            print(f"Container {container_name} created successfully.")
            # return container
            container.start()
            return "success"
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
