# 选择轻量级 Python 基础镜像
FROM registry-ze.tencentcloudcr.com/basic/python:3.10.14-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（kubectl + curl + bash）
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates bash \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && rm -f kubectl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 运行端口
EXPOSE 8888

# 使用 Gunicorn 作为生产级 WSGI 服务器
CMD ["gunicorn", "-b", "0.0.0.0:8888", "run:app"]