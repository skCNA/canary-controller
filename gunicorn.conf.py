import multiprocessing

# 基础配置 必须设置1
workers = 1
worker_class = "gevent"
bind = "0.0.0.0:8888"

# 优雅下线相关
graceful_timeout = 30  # 等待在途请求完成的最大秒数
timeout = 60  # 单个请求超时时间
keepalive = 5

# 日志输出到标准输出，便于容器采集
accesslog = "-"
errorlog = "-"
