from kubernetes import config, client
from flask import jsonify
from kubernetes.client import ApiException


class KubernetesClient:
    # 初始化，需要k8s的配置文件
    # ~/.kube中的config文件
    def __init__(self):
        config.load_kube_config(config_file="app/config/kubeconfig")

    def k8s_core_api(self):
        v1 = client.CoreV1Api()
        return v1

    def k8s_apps_api(self):
        appsv1 = client.AppsV1Api()
        return appsv1

    # 获取所有的pods
    def list_pods(self):
        v1 = self.k8s_core_api()
        pods = []
        pod_list = v1.list_pod_for_all_namespaces().items
        for pod in pod_list:
            pod_info = {
                "namespace": pod.metadata.namespace,
                "name": pod.metadata.name,
                "ready": pod.status.phase,
                "status": pod.status.phase,
                "restarts": pod.status.container_statuses[0].restart_count,
                "age": pod.metadata.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            pods.append(pod_info)
        return jsonify(pods)

    # 获取所有的deployment
    def list_deployments(self):
        appsv1 = self.k8s_apps_api()
        deployments = []
        deployment_list = appsv1.list_deployment_for_all_namespaces().items
        for deployment in deployment_list:
            deployment_info = {
                "namespace": deployment.metadata.namespace,
                "name": deployment.metadata.name,
                "ready": f"{deployment.status.ready_replicas}/{deployment.spec.replicas}",
                "up_to_date": deployment.status.updated_replicas,
                "available": deployment.status.available_replicas,
                "age": deployment.metadata.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            deployments.append(deployment_info)
        return jsonify(deployments)

    # 获取所有的services
    def list_services(self):
        v1 = self.k8s_core_api()
        services = []
        service_list = v1.list_service_for_all_namespaces().items
        for service in service_list:
            service_info = {
                "namespace": service.metadata.namespace,
                "name": service.metadata.name,
                "type": service.spec.type,
                "cluster_ip": service.spec.cluster_ip,
                "ports": [{"port": port.port, "protocol": port.protocol} for port in service.spec.ports]
            }
            services.append(service_info)
        return jsonify(services)

    # 获取所有的namespace
    def list_namespaces(self):
        v1 = self.k8s_core_api()
        namespaces = []
        namespace_list = v1.list_namespace().items
        for namespace in namespace_list:
            namespaces.append(namespace.metadata.name)
        return jsonify(namespaces)

    # 获取指定namespace下的pods
    def list_namespace_pods(self, namespace):
        v1 = self.k8s_core_api()
        pods = []
        pod_list = v1.list_namespaced_pod(namespace).items
        for pod in pod_list:
            pod_info = {
                "namespace": pod.metadata.namespace,
                "name": pod.metadata.name,
                "ready": pod.status.phase,
                "status": pod.status.phase,
                "restarts": pod.status.container_statuses[0].restart_count,
                "age": pod.metadata.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            pods.append(pod_info)
        return jsonify(pods)

    # 获取指定namespace下的deployments
    def list_namespace_deployments(self, namespace):
        appv1 = self.k8s_apps_api()
        deployments = []
        deployment_list = appv1.list_namespaced_deployment(namespace).items
        for deployment in deployment_list:
            deployment_info = {
                "namespace": deployment.metadata.namespace,
                "name": deployment.metadata.name,
                "ready": f"{deployment.status.ready_replicas}/{deployment.spec.replicas}",
                "up_to_date": deployment.status.updated_replicas,
                "available": deployment.status.available_replicas,
                "age": deployment.metadata.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            deployments.append(deployment_info)
        return jsonify(deployments)

    # 获取指定namespace下的services
    def list_namespace_service(self, namespace):
        v1 = self.k8s_core_api()
        services = []
        service_list = v1.list_namespaced_service(namespace).items
        for service in service_list:
            service_info = {
                "namespace": service.metadata.namespace,
                "name": service.metadata.name,
                "type": service.spec.type,
                "cluster_ip": service.spec.cluster_ip,
                "ports": [{"port": port.port, "protocol": port.protocol} for port in service.spec.ports]
            }
            services.append(service_info)
        return jsonify(services)

    # 获取指定pod的详细信息
    def get_pod_details(self, namespace, pod_name):
        v1 = self.k8s_core_api()
        try:
            pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            return jsonify(pod.to_dict())
        except client.exceptions.ApiException as e:
            return jsonify({"error": e.reason}), e.status

    # 获取指定deployment的详细信息
    def get_deployment_details(self, namespace, deployment_name):
        appsv1 = self.k8s_apps_api()
        try:
            deployment = appsv1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
            return jsonify(deployment.to_dict())
        except client.exceptions.ApiException as e:
            return jsonify({"error": e.reason}), e.status

    # 获取指定资源的详细信息
    def describe_resource(self, namespace, resource_type, resource_name):
        v1 = self.k8s_core_api
        appsv1 = self.k8s_apps_api()
        try:
            if resource_type == 'pod':
                resource = v1.read_namespaced_pod(name=resource_name, namespace=namespace)
            elif resource_type == 'deployment':
                resource = appsv1.read_namespaced_deployment(name=resource_name, namespace=namespace)
            elif resource_type == 'service':
                resource = v1.read_namespaced_service(name=resource_name, namespace=namespace)
            else:
                return jsonify({"error": "Invalid resource type"}), 400
            return jsonify(resource.to_dict())
        except client.exceptions.ApiException as e:
            return jsonify({"error": e.reason}), e.status

    # 获取指定pod的日志
    def get_pod_logs(self, namespace, pod_name):
        v1 = self.k8s_core_api()
        try:
            logs = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
            return jsonify({"logs": logs})
        except client.exceptions.ApiException as e:
            return jsonify({"error": e.reason}), e.status

    # 创建资源
    def create_resource(self, resource):
        v1 = self.k8s_core_api()
        appsv1 = self.k8s_apps_api()
        # 根据资源类型创建资源
        if resource['kind'] == 'Pod':
            created_resource = v1.create_namespaced_pod(body=resource, namespace=resource['metadata']['namespace'])
        elif resource['kind'] == 'Deployment':
            created_resource = appsv1.create_namespaced_deployment(body=resource,
                                                                   namespace=resource['metadata']['namespace'])
        elif resource['kind'] == 'Service':
            created_resource = v1.create_namespaced_service(body=resource, namespace=resource['metadata']['namespace'])
        else:
            return jsonify({"error": "Unsupported resource type"}), 400
        return jsonify(created_resource.to_dict()), 201

    def delete_pod(self, pod_id, namespace):
        try:
            v1 = self.k8s_core_api()
            # 删除 Pod
            v1.delete_namespaced_pod(pod_id, namespace)
            return jsonify({'message': 'Pod deleted successfully.'}), 200
        except ApiException as e:
            return jsonify({'error': str(e)}), e.status

    def delete_deployment(self, deployment_id, namespace):
        try:
            v1 = self.k8s_apps_api()
            # 删除 Pod
            v1.delete_namespaced_deployment(deployment_id, namespace)
            return jsonify({'message': 'Pod deleted successfully.'}), 200
        except ApiException as e:
            return jsonify({'error': str(e)}), e.status
