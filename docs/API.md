# API 参考文档

本文档详细描述了 Canary Controller 的 API 接口和核心函数。

## 核心函数

### kubectl_utils.py

#### `get_ingresses()`

获取集群中所有标记为 Canary 的 Ingress 资源。

**返回值：**
```python
List[Ingress]  # 包含以下属性的对象列表
```

**Ingress 对象属性：**
- `namespace` (str): Ingress 所在命名空间
- `name` (str): Ingress 名称
- `weight` (str): Canary 权重配置
- `header` (str): 请求头名称
- `header_value` (str): 请求头匹配值
- `header_pattern` (str): 请求头正则表达式
- `cookie` (str): Cookie 名称
- `hosts` (List[str]): 关联的主机列表

**示例：**
```python
ingresses = get_ingresses()
for ing in ingresses:
    print(f"{ing.namespace}/{ing.name}: weight={ing.weight}")
```

#### `set_ingress_annotations(ns, name, annotations)`

更新指定 Ingress 的注解。

**参数：**
- `ns` (str): 命名空间
- `name` (str): Ingress 名称
- `annotations` (dict): 要设置的注解字典

**支持的注解：**
```python
{
    "nginx.ingress.kubernetes.io/canary-weight": "50",
    "nginx.ingress.kubernetes.io/canary-by-header": "Canary",
    "nginx.ingress.kubernetes.io/canary-by-header-value": "true",
    "nginx.ingress.kubernetes.io/canary-by-header-pattern": "^test.*",
    "nginx.ingress.kubernetes.io/canary-by-cookie": "canary"
}
```

**示例：**
```python
annotations = {
    "nginx.ingress.kubernetes.io/canary-weight": "30"
}
set_ingress_annotations("production", "my-ingress", annotations)
```

### routes.py

#### `cleanup_locks()`

清理过期的锁记录（内部函数）。

**逻辑：**
- 遍历锁表，删除超过 24 小时（86400 秒）的锁
- 使用线程锁确保操作原子性

#### 锁管理机制

**锁表结构：**
```python
lock_table = {
    (namespace, ingress): {
        "user": str,      # 用户名
        "timestamp": float # 锁定时间戳
    }
}
```

**锁的生命周期：**
- 创建：通过 `/lock` 端点
- 检查：修改前验证锁状态
- 清理：24小时后自动过期
- 手动释放：通过 `/unlock` 端点

## HTTP API 端点

### 认证机制

所有 API 端点都通过以下方式识别用户：

```http
X-Auth-Request-Email: user@example.com
```

- 如果未提供邮箱，用户名为 "anonymous"
- 用户名从邮箱中提取（@ 符号前的部分）

### GET /

获取主页面，显示所有 Canary Ingress 的当前状态。

**请求头：**
```http
X-Auth-Request-Email: user@example.com  # 可选
```

**响应：**
- Content-Type: text/html
- 包含 Ingress 表格和锁状态的完整页面

**处理流程：**
1. 清理过期锁
2. 获取所有 Canary Ingress
3. 识别当前用户
4. 渲染模板

### GET /set

更新 Ingress 的 Canary 配置注解。

**查询参数：**
- `namespace` (str, 必需): Ingress 命名空间
- `ingress` (str, 必需): Ingress 名称
- `weight` (str, 可选): 流量权重 (0-100)
- `header` (str, 可选): 请求头名称
- `header_value` (str, 可选): 请求头匹配值
- `header_pattern` (str, 可选): 请求头正则表达式
- `cookie` (str, 可选): Cookie 名称

**请求示例：**
```http
GET /set?namespace=prod&ingress=my-app&weight=50&header=Canary&header_value=true
```

**安全检查：**
1. 验证 Ingress 是否已被当前用户锁定
2. 检查锁的所有权

**响应：**
- 成功: 302 重定向到主页面
- 失败: 403 JSON 错误响应

**错误响应示例：**
```json
{
  "error": "Ingress must be locked before modifying"
}
```

### POST /lock

锁定指定的 Ingress 以进行修改。

**请求体：** application/x-www-form-urlencoded
- `namespace` (str, 必需): Ingress 命名空间
- `ingress` (str, 必需): Ingress 名称

**请求示例：**
```http
POST /lock
Content-Type: application/x-www-form-urlencoded

namespace=prod&ingress=my-app
```

**处理逻辑：**
1. 清理过期锁
2. 检查是否已被其他用户锁定
3. 创建或更新锁记录

**响应：**
```json
{
  "status": "locked"
}
```

**错误响应：**
```json
{
  "error": "Already locked"
}
```

### POST /unlock

解锁指定的 Ingress。

**请求体：** application/x-www-form-urlencoded
- `namespace` (str, 必需): Ingress 命名空间
- `ingress` (str, 必需): Ingress 名称

**处理逻辑：**
1. 验证锁的所有权
2. 删除锁记录（仅限锁的所有者）

**响应：**
```json
{
  "status": "unlocked"
}
```

**注意：** 无论是否成功，都返回 "unlocked" 状态，避免泄露锁的存在信息。

## 前端验证

### validate.js 表单验证

#### `CanaryFormValidator.validate(form)`

验证 Canary 配置表单的输入。

**验证规则：**

1. **请求头冲突检查**
   - `header_value` 和 `header_pattern` 不能同时设置

2. **正则表达式验证**
   - `header_pattern` 必须是有效的正则表达式

3. **权重范围验证**
   - 权重必须是 0-100 之间的整数

**错误提示：**
```javascript
// 冲突错误
"canary-by-header-value 和 canary-by-header-pattern 不能同时设置"

// 正则错误
"canary-by-header-pattern 正则格式错误: [错误信息]"

// 权重错误
"canary-weight 必须是 0-100 的整数"
```

**使用示例：**
```html
<form onsubmit="return CanaryFormValidator.validate(this)">
  <!-- 表单字段 -->
</form>
```

## 错误处理

### HTTP 状态码

- **200 OK**: 请求成功
- **302 Found**: 重定向（成功操作后）
- **403 Forbidden**: 权限不足或锁冲突
- **500 Internal Server Error**: 服务器内部错误

### 错误响应格式

```json
{
  "error": "错误描述信息"
}
```

### 常见错误场景

1. **未锁定修改**
   - 尝试修改未锁定的 Ingress
   - 返回 403 和相应错误信息

2. **锁冲突**
   - 其他用户已锁定目标 Ingress
   - 返回 403 和 "Already locked" 错误

3. **输入验证失败**
   - 前端验证拦截，阻止提交
   - 显示友好的错误提示

## 使用示例

### 完整工作流

1. **查看 Ingress 列表**
```bash
curl -H "X-Auth-Request-Email: user@company.com" http://localhost:8888/
```

2. **锁定 Ingress**
```bash
curl -X POST \
  -H "X-Auth-Request-Email: user@company.com" \
  -d "namespace=prod&ingress=my-app" \
  http://localhost:8888/lock
```

3. **更新配置**
```bash
curl -X GET \
  -H "X-Auth-Request-Email: user@company.com" \
  "http://localhost:8888/set?namespace=prod&ingress=my-app&weight=50"
```

4. **解锁 Ingress**
```bash
curl -X POST \
  -H "X-Auth-Request-Email: user@company.com" \
  -d "namespace=prod&ingress=my-app" \
  http://localhost:8888/unlock
```

### Python 客户端示例

```python
import requests

class CanaryClient:
    def __init__(self, base_url, email):
        self.base_url = base_url
        self.headers = {"X-Auth-Request-Email": email}

    def lock_ingress(self, namespace, name):
        response = requests.post(
            f"{self.base_url}/lock",
            data={"namespace": namespace, "ingress": name},
            headers=self.headers
        )
        return response.json()

    def set_weight(self, namespace, name, weight):
        params = {
            "namespace": namespace,
            "ingress": name,
            "weight": weight
        }
        response = requests.get(
            f"{self.base_url}/set",
            params=params,
            headers=self.headers,
            allow_redirects=False
        )
        return response.status_code == 302

    def unlock_ingress(self, namespace, name):
        response = requests.post(
            f"{self.base_url}/unlock",
            data={"namespace": namespace, "ingress": name},
            headers=self.headers
        )
        return response.json()

# 使用示例
client = CanaryClient("http://localhost:8888", "user@company.com")
client.lock_ingress("prod", "my-app")
client.set_weight("prod", "my-app", "30")
client.unlock_ingress("prod", "my-app")
```