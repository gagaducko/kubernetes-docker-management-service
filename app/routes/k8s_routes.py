from app.kubernetes.k8s_client import KubernetesClient
import yaml
from flask import Flask, jsonify, Blueprint, request

k8s_client = KubernetesClient()

app = Blueprint('k8s', __name__)


# get到所有的k8s中的pods
@app.route('/pods', methods=['GET'])
def list_pods():
    pods = k8s_client.list_pods()
    return pods


# get到所有的k8s中的deployment
@app.route('/deployments', methods=['GET'])
def list_deployments():
    deployments = k8s_client.list_deployments()
    return deployments


# get到所有的k8s中的services
@app.route('/services', methods=['GET'])
def list_services():
    services = k8s_client.list_services()
    return services


# get到所有k8s中的namespace
@app.route('/namespaces', methods=['GET'])
def list_namespaces():
    namespaces = k8s_client.list_namespaces()
    return namespaces


# get到指定namespace下面的pods
@app.route('/<namespace>/pods', methods=['GET'])
def list_namespace_pods(namespace):
    pods = k8s_client.list_namespace_pods(namespace)
    return pods


# get到指定namespace下面的deployments
@app.route('/<namespace>/deployments', methods=['GET'])
def list_namespace_deployments(namespace):
    deployments = k8s_client.list_namespace_deployments(namespace)
    return deployments


# get到指定namespace下面的services
@app.route('/<namespace>/services', methods=['GET'])
def list_namespace_services(namespace):
    services = k8s_client.list_namespace_deployments(namespace)
    return services


# get到指定pod的详细信息
@app.route('/<namespace>/<pod_name>', methods=['GET'])
def get_pod_details(namespace, pod_name):
    pod_details = k8s_client.get_pod_details(namespace, pod_name)
    return pod_details


# get到指定deployment的详细信息
@app.route('/<namespace>/<deployment_name>', methods=['GET'])
def get_deployment_details(namespace, deployment_name):
    deployment_details = k8s_client.get_deployment_details(namespace, deployment_name)
    return deployment_details


# 获取指定资源的describe信息
@app.route('/describe/<resource_type>/<namespace>/<resource_name>', methods=['GET'])
def describe_resource(namespace, resource_type, resource_name):
    resource_description = k8s_client.describe_resource(namespace, resource_type, resource_name)
    return resource_description


# 获取指定pod的logs信息
@app.route('/logs/<namespace>/<pod_name>', methods=['GET'])
def get_pod_logs(namespace, pod_name):
    pod_logs = k8s_client.get_pod_logs(namespace, pod_name)
    return pod_logs


# 根据yaml来创建资源
@app.route('/create', methods=['POST'])
def create_resource():
    try:
        data = request.get_data().decode('utf-8')
        resource = yaml.safe_load(data)
        # 检查 YAML 文件的正确性
        if not resource:
            return jsonify({"error": "Invalid YAML"}), 400
        return k8s_client.create_resource(resource)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/deletePod', methods=['POST'])
def delete_pod():
    data = request.get_json()
    namespace = data.get('namespace')
    pod_id = data.get("pod_id")
    return k8s_client.delete_pod(pod_id, namespace)


@app.route('/deleteDeployment', methods=['POST'])
def delete_deployment():
    data = request.get_json()
    namespace = data.get('namespace')
    deployment_id = data.get("deployment_id")
    return k8s_client.delete_deployment(deployment_id, namespace)
