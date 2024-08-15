import socket
import threading
import time

import requests
from app import app
from skywalking import agent, config

# Nacos服务端注册地址
nacos_login_url = 'http://192.168.186.1:8848/nacos/v1/auth/login'

namespace_id = '3d2a526c-a80d-40d7-8754-3e9870b0b41b'

# 请求参数
login_data = {
    'username': 'nacos',
    'password': 'nacos'
}

# 全局变量，存储accessToken
access_token = None
access_token_expiration = 0  # 存储accessToken过期的时间戳


# 更新accessToken的函数
def update_access_token():
    global access_token, access_token_expiration
    response = requests.post(nacos_login_url, data=login_data)
    response_json = response.json()
    access_token = response_json.get('accessToken')
    # 假设accessToken有效期为18000秒，这里设置每16000秒就更新一次token，确保能一直发送心跳
    access_token_expiration = time.time() + 16000


# nacos服务注册
def service_register():
    global access_token
    update_access_token()  # 确保在注册之前有有效的accessToken
    ip = socket.gethostbyname(socket.gethostname())
    url = "http://192.168.186.1:8848/nacos/v1/ns/instance"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "serviceName": "kubernetes-management-service",
        # "ip": "192.168.186.109",
        "ip": ip,
        "port": 31001,
        "namespaceId": namespace_id
    }
    res = requests.post(url, headers=headers, params=params)
    print("向nacos注册中心，发起服务注册请求，注册响应状态： {}".format(res.status_code))


# 服务心跳检测
def service_beat():
    global access_token, access_token_expiration
    ip = socket.gethostbyname(socket.gethostname())
    while True:
        if time.time() > access_token_expiration:
            update_access_token()
        url = "http://192.168.186.1:8848/nacos/v1/ns/instance/beat"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "serviceName": "kubernetes-management-service",
            # "ip": "192.168.186.109",
            "ip": ip,
            "port": 31001,
            "namespaceId": namespace_id
        }
        res = requests.put(url, headers=headers, params=params)
        print("已注册服务，执行心跳服务，续期服务响应状态： {}".format(res.status_code))
        time.sleep(5)


if __name__ == '__main__':
    service_register()
    beat_thread = threading.Thread(target=service_beat)
    beat_thread.daemon = True
    beat_thread.start()
    # skywalking相关配置
    config.init(collector='192.168.186.1:11800', service="kubernetes-management-service")
    agent.start()
    app.run(host="0.0.0.0", port=31001, debug=False)
