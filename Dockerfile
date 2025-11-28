# 选择轻量级 Python 基础镜像
FROM registry-ze.tencentcloudcr.com/basic/python:3.10.14-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 使用缓存机制加速依赖包下载
RUN mount=type=cache,target=/root/pip_cached \
    pip download -d /root/pip_cached -r requirements.txt -i https://deploy:zmexing@nexus.zmexing.com/repository/pypi_group/simple

# 安装依赖包
RUN mount=type=cache,target=/root/pip_cached \
    pip install --no-index --find-links=/root/pip_cached --no-build-isolation -r requirements.txt

COPY . .

# 运行端口
EXPOSE 8888

# 使用 Gunicorn 作为生产级 WSGI 服务器
#CMD ["python3", "run.py"]
# production
CMD ["gunicorn", "-w", "1","-k","gevent", "-b", "0.0.0.0:8888", "--access-logfile", "-", "--error-logfile", "-", "app:create_app()"]
