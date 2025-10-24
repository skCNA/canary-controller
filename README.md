# Canary Controller

一个用于管理 Kubernetes Ingress Canary 部署的 Web 控制面板。

## 概述

Canary Controller 是一个基于 Flask 的 Web 应用程序，提供直观的界面来管理和配置 Kubernetes Ingress 的 Canary 部署。它支持多种 Canary 策略，包括基于权重、请求头和 Cookie 的流量分割。

## 功能特性

- 🌐 **现代化Web界面** - 响应式设计，支持桌面和移动端
- 🔄 **智能输入框** - 点击展开支持长文本编辑，实时字符计数
- 🔔 **优雅的通知系统** - Toast提示替代传统alert，用户体验友好
- 🔒 **并发控制** - 用户级别的锁机制防止并发修改
- 🎯 **多种策略支持** - 支持权重、请求头、Cookie 等 Canary 策略
- ⚡ **Ajax操作** - 无刷新表单提交，实时反馈
- 🎹 **实时验证** - 前端表单验证，即时错误提示
- ⌨️ **快捷键支持** - Enter保存，Escape取消
- 📱 **响应式设计** - 移动端友好的交互体验

## 支持的 Canary 策略

### 1. 权重分流 (Weight-based)
- 通过 `nginx.ingress.kubernetes.io/canary-weight` 注解设置
- 取值范围：0-100，表示流量百分比

### 2. 请求头分流 (Header-based)
- `nginx.ingress.kubernetes.io/canary-by-header` - 启用基于请求头的分流
- `nginx.ingress.kubernetes.io/canary-by-header-value` - 匹配特定请求头值
- `nginx.ingress.kubernetes.io/canary-by-header-pattern` - 使用正则表达式匹配请求头

### 3. Cookie 分流 (Cookie-based)
- 通过 `nginx.ingress.kubernetes.io/canary-by-cookie` 注解设置
- 基于特定 Cookie 值进行分流

## 项目结构

```
canary-controller/
├── app/
│   ├── __init__.py          # Flask 应用工厂
│   ├── routes.py            # 主要路由和业务逻辑
│   ├── kubectl_utils.py     # Kubernetes API 工具
│   ├── forms.py             # 表单定义
│   ├── templates/
│   │   └── index.html       # 主页面模板
│   └── static/
│       └── js/
│           └── validate.js  # 前端表单验证
├── config.py                # 配置文件
├── run.py                   # 应用入口
└── README.md               # 项目文档
```

## 核心模块

### 1. 应用入口 (`run.py`)
应用程序的启动入口，创建并运行 Flask 应用。

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
```

### 2. 路由控制 (`app/routes.py`)
主要的业务逻辑和 API 端点：

- `GET /` - 主页面，显示所有 Canary Ingress
- `GET /set` - 更新 Ingress 注解
- `POST /lock` - 锁定 Ingress 防止并发修改
- `POST /unlock` - 解锁 Ingress

**关键特性：**
- 使用全局锁表管理并发访问
- 基于用户邮箱的身份识别
- 自动清理过期锁（24小时TTL）

### 3. Kubernetes 工具 (`app/kubectl_utils.py`)
封装 Kubernetes API 操作：

- `get_ingresses()` - 获取所有 Canary Ingress
- `set_ingress_annotations()` - 更新 Ingress 注解

**配置加载优先级：**
1. In-cluster 配置（集群内运行时）
2. 本地 kubeconfig 文件（开发环境）

### 4. 前端验证 (`app/static/js/validate.js`)
客户端表单验证逻辑：

- 验证权重范围（0-100）
- 检查请求头配置冲突
- 正则表达式格式验证

## 安装和部署

### 前置要求

- Python 3.7+
- Kubernetes 集群
- NGINX Ingress Controller
- kubectl 配置

### 依赖安装

```bash
pip install flask kubernetes
```

### 配置文件

确保 Kubernetes 配置文件路径正确：
- 默认路径：`/Users/admin/.kube/config-devops`
- 可在 `app/kubectl_utils.py` 中修改

### 运行应用

```bash
python run.py
```

应用将在 `http://0.0.0.0:8888` 启动。

## API 文档

### 认证

应用通过请求头 `X-Auth-Request-Email` 识别用户身份，支持：

- 集群内 OIDC 认证集成
- 匿名访问（用户名为 "anonymous"）

### 端点详情

#### GET /
**描述**：获取主页面，显示所有 Canary Ingress

**响应**：HTML 页面，包含：
- Ingress 列表表格
- 当前配置的注解信息
- 锁状态显示

#### GET /set
**描述**：更新 Ingress 的 Canary 注解

**参数**：
- `namespace` (string) - Ingress 命名空间
- `ingress` (string) - Ingress 名称
- `weight` (string, 可选) - 权重值 (0-100)
- `header` (string, 可选) - 请求头名称
- `header_value` (string, 可选) - 请求头匹配值
- `header_pattern` (string, 可选) - 请求头正则表达式
- `cookie` (string, 可选) - Cookie 名称

**响应**：重定向到主页面

**错误**：
- `403 Forbidden` - 未锁定或被其他用户锁定

#### POST /lock
**描述**：锁定 Ingress 以进行修改

**参数**：
- `namespace` (string) - Ingress 命名空间
- `ingress` (string) - Ingress 名称

**响应**：
```json
{
  "status": "locked"
}
```

**错误**：
- `403 Forbidden` - 已被其他用户锁定

#### POST /unlock
**描述**：解锁 Ingress

**参数**：
- `namespace` (string) - Ingress 命名空间
- `ingress` (string) - Ingress 名称

**响应**：
```json
{
  "status": "unlocked"
}
```

## 安全考虑

1. **锁机制**：防止多用户同时修改同一 Ingress
2. **用户身份**：基于邮箱的用户识别
3. **输入验证**：前后端双重验证确保配置安全
4. **权限控制**：依赖 Kubernetes RBAC 进行权限管理

## 故障排除

### 常见问题

1. **无法连接 Kubernetes**
   - 检查 kubeconfig 文件路径
   - 验证集群连接权限

2. **页面显示 "No canary ingresses found"**
   - 确保有带有 `nginx.ingress.kubernetes.io/canary: "true"` 注解的 Ingress
   - 检查 NGINX Ingress Controller 状态

3. **无法修改 Ingress**
   - 确保已锁定对应的 Ingress
   - 检查是否有其他用户已锁定

### 日志查看

应用日志会显示关键操作信息：
- 用户操作记录
- 锁获取/释放
- Kubernetes API 调用

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。