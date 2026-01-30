# 选择轻量级 Python 基础镜像
FROM registry-ze.tencentcloudcr.com/basic/python:3.10.14-uv

#重试次数
ENV UV_HTTP_RETRIES=10
#超时时间
ENV  UV_HTTP_TIMEOUT=120

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/uv \
        uv  pip install  \
       --system \
        -v \
       --no-build-isolation \
      -r requirements.txt \
      -i https://deploy:zmexing@nexus.zmexing.com/repository/pypi_group/simple \

## 使用缓存机制加速依赖包下载
#RUN mount=type=cache,target=/root/pip_cached \
#    pip download -d /root/pip_cached -r requirements.txt -i https://deploy:zmexing@nexus.zmexing.com/repository/pypi_group/simple
#
## 安装依赖包
#RUN mount=type=cache,target=/root/pip_cached \
#    pip install --no-index --find-links=/root/pip_cached --no-build-isolation -r requirements.txt

COPY . .

# 运行端口
EXPOSE 8888

# 使用 Gunicorn 作为生产级 WSGI 服务器
#CMD ["python3", "run.py"]
# production
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]
