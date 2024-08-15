#基于的基础镜像
FROM python:3.6.8

#代码添加文件夹
ADD . /app

# 设置code文件夹是工作目录
WORKDIR /app

# 安装支持
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# 对外暴露的端口号
EXPOSE 31001

CMD ["python", "app.py"]

#docker run -d -p 31001:31001 -v /var/run/docker.sock:/var/run/docker.sock -v ~/.kube/config:/app/app/config/kubeconfig --name kubernets-management kubernetes-management-service
