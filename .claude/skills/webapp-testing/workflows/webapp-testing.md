# Web 应用测试工作流程

本文档描述了使用 Playwright 进行本地 Web 应用自动化测试的完整工作流程。

## 工作流程总览

```
1. 任务分析
   ├─ 识别应用类型（静态/动态）
   ├─ 确认服务器状态
   └─ 选择测试策略

2. 环境准备
   ├─ 静态应用 → 准备 HTML 文件路径
   └─ 动态应用 → 启动服务器（如未运行）

3. 侦察阶段
   ├─ 导航到目标 URL
   ├─ 等待页面完全加载（networkidle）
   ├─ 截图 / 检查 DOM 结构
   └─ 识别目标元素选择器

4. 执行阶段
   ├─ 编写 Playwright 脚本
   ├─ 执行 UI 交互操作
   ├─ 捕获运行时信息（console、网络）
   └─ 验证预期结果

5. 结果分析
   ├─ 检查截图 / 日志
   ├─ 排查失败原因
   └─ 迭代优化脚本
```

---

## 阶段 1：任务分析与策略选择

### 1.1 应用类型判断

**静态 HTML 应用**：
- 特征：纯 HTML/CSS，无后端服务器，无动态 JS 渲染
- 测试方法：直接读取 HTML 文件 → 识别选择器 → 使用 `file://` URL
- 示例：`file:///path/to/index.html`

**动态 Web 应用**：
- 特征：需要运行服务器（Node.js、Python、Go 等），JS 动态渲染 DOM
- 测试方法：启动服务器 → 访问 `http://localhost:PORT` → 等待 JS 完成

### 1.2 服务器状态确认

| 状态 | 处理方式 |
|------|----------|
| **未运行** | 使用 `scripts/with_server.py` 自动管理生命周期 |
| **已运行** | 直接编写 Playwright 脚本访问 URL |
| **多服务** | 用 `with_server.py` 同时启动多个服务（后端+前端） |

---

## 阶段 2：环境准备

### 2.1 静态应用准备

```bash
# 无需额外准备，直接使用 file:// URL
ls /path/to/static/app/index.html
```

### 2.2 动态应用准备

#### 方式 1：手动启动服务器

```bash
# 前端开发服务器
cd frontend && npm run dev

# 后端服务
cd backend && python server.py
```

#### 方式 2：使用 with_server.py（推荐）

**单服务器示例**：
```bash
python scripts/with_server.py \
  --server "npm run dev" \
  --port 5173 \
  -- python test_script.py
```

**多服务器示例**：
```bash
python scripts/with_server.py \
  --server "cd backend && uvicorn main:app --port 3000" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python test_fullstack.py
```

> **优势**：
> - 自动启动/停止服务器
> - 自动等待服务器就绪
> - 测试脚本更简洁（无需服务器管理代码）

---

## 阶段 3：侦察阶段（Reconnaissance）

### 3.1 基础侦察脚本

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 导航
    page.goto('http://localhost:5173')
    
    # 关键：等待 JS 完成（动态应用必须）
    page.wait_for_load_state('networkidle')
    
    # 截图
    page.screenshot(path='/tmp/recon.png', full_page=True)
    
    # 获取 DOM 结构
    html_content = page.content()
    print(html_content[:500])  # 打印前 500 字符
    
    # 发现按钮
    buttons = page.locator('button').all()
    print(f"发现 {len(buttons)} 个按钮：")
    for i, btn in enumerate(buttons):
        text = btn.inner_text() if btn.is_visible() else "[隐藏]"
        print(f"  [{i}] {text}")
    
    browser.close()
```

### 3.2 元素发现技巧

| 目标元素 | 推荐方法 | 示例代码 |
|---------|---------|---------|
| 按钮 | `locator('button')` | `page.locator('button').all()` |
| 链接 | `locator('a[href]')` | `page.locator('a[href]').all()` |
| 输入框 | `locator('input, textarea')` | `page.locator('input').all()` |
| 特定文本 | `text=` 选择器 | `page.locator('text=提交').click()` |
| ARIA 角色 | `role=` 选择器 | `page.locator('role=button[name="登录"]')` |

### 3.3 常见陷阱

❌ **错误**：动态应用未等待就检查 DOM
```python
page.goto('http://localhost:5173')
page.screenshot(path='wrong.png')  # ❌ JS 可能还没执行完
```

✅ **正确**：先等待 networkidle
```python
page.goto('http://localhost:5173')
page.wait_for_load_state('networkidle')  # ✅ 等待 JS 完成
page.screenshot(path='correct.png')
```

---

## 阶段 4：执行阶段

### 4.1 基础交互操作

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')
    
    # 点击按钮（使用文本选择器）
    page.locator('text=登录').click()
    
    # 填写表单
    page.fill('input[name="username"]', 'test_user')
    page.fill('input[name="password"]', 'secure_pass')
    
    # 选择下拉框
    page.select_option('select#city', 'beijing')
    
    # 复选框
    page.check('input#agree-terms')
    
    # 提交表单
    page.click('button[type="submit"]')
    
    # 等待导航
    page.wait_for_url('**/dashboard')
    
    # 验证结果
    assert page.locator('text=欢迎回来').is_visible()
    
    browser.close()
```

### 4.2 捕获运行时信息

#### 捕获 Console 日志

```python
console_logs = []

def handle_console(msg):
    console_logs.append(f"[{msg.type}] {msg.text}")
    print(f"Console: [{msg.type}] {msg.text}")

page.on("console", handle_console)
page.goto('http://localhost:5173')

# ... 执行操作 ...

# 保存日志
with open('console.log', 'w') as f:
    f.write('\n'.join(console_logs))
```

#### 捕获网络请求

```python
network_logs = []

def handle_request(request):
    network_logs.append(f"→ {request.method} {request.url}")

def handle_response(response):
    network_logs.append(f"← {response.status} {response.url}")

page.on("request", handle_request)
page.on("response", handle_response)

page.goto('http://localhost:5173')
```

### 4.3 等待策略

| 等待类型 | 使用场景 | 示例代码 |
|---------|---------|---------|
| `networkidle` | 页面完全加载（动态应用） | `page.wait_for_load_state('networkidle')` |
| `selector` | 等待特定元素出现 | `page.wait_for_selector('button#submit')` |
| `timeout` | 固定延迟（不推荐） | `page.wait_for_timeout(1000)` |
| `url` | 等待 URL 改变 | `page.wait_for_url('**/success')` |

---

## 阶段 5：结果分析与故障排查

### 5.1 常见问题诊断

| 症状 | 可能原因 | 解决方案 |
|------|---------|---------|
| 元素未找到 | JS 未执行完 | 添加 `wait_for_load_state('networkidle')` |
| 选择器失效 | DOM 结构动态变化 | 使用语义化选择器（`text=`、`role=`） |
| 操作无响应 | 元素被遮挡/不可见 | 检查 `.is_visible()`，使用 `force=True` |
| 服务器未就绪 | 启动时间过长 | 用 `with_server.py` 自动检测就绪 |
| 截图为空白 | 未等待渲染 | 检查 `wait_for_load_state()` |

### 5.2 调试技巧

#### 可视化调试（非 headless）

```python
browser = p.chromium.launch(headless=False, slow_mo=500)  # 放慢 500ms
```

#### 详细日志

```python
page.on("pageerror", lambda e: print(f"页面错误: {e}"))
page.on("console", lambda msg: print(f"Console: {msg.text}"))
```

#### 元素高亮

```python
page.locator('button#submit').highlight()
```

### 5.3 成功标准检查表

- [ ] 页面完全加载（networkidle）
- [ ] 目标元素正确识别
- [ ] 操作执行成功（无异常）
- [ ] 预期结果验证通过
- [ ] Console 无严重错误
- [ ] 截图符合预期

---

## 完整示例：端到端测试

```python
from playwright.sync_api import sync_playwright
import sys

def test_login_flow():
    """测试登录流程"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 1. 导航到登录页
            print("1. 导航到登录页...")
            page.goto('http://localhost:5173/login')
            page.wait_for_load_state('networkidle')
            
            # 2. 侦察阶段
            print("2. 截图保存初始状态...")
            page.screenshot(path='/tmp/login_page.png')
            
            # 3. 填写表单
            print("3. 填写登录表单...")
            page.fill('input[name="username"]', 'admin')
            page.fill('input[name="password"]', 'admin123')
            
            # 4. 提交
            print("4. 提交表单...")
            page.click('button:has-text("登录")')
            
            # 5. 等待跳转
            print("5. 等待跳转到 Dashboard...")
            page.wait_for_url('**/dashboard', timeout=5000)
            
            # 6. 验证结果
            print("6. 验证登录成功...")
            page.wait_for_selector('text=欢迎回来', timeout=3000)
            page.screenshot(path='/tmp/dashboard.png')
            
            print("✅ 测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            page.screenshot(path='/tmp/error.png')
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_login_flow()
    sys.exit(0 if success else 1)
```

**使用 with_server.py 执行**：

```bash
python scripts/with_server.py \
  --server "npm run dev" --port 5173 \
  -- python test_login.py
```

---

## 最佳实践总结

1. **总是先侦察**：截图 + DOM 检查 → 识别选择器 → 编写脚本
2. **等待策略优先**：动态应用必须 `wait_for_load_state('networkidle')`
3. **语义化选择器**：`text=`、`role=` 优于脆弱的 CSS 选择器
4. **黑盒化工具**：先用 `scripts/with_server.py --help`，避免读源码
5. **错误处理**：try-finally 确保 `browser.close()`
6. **调试友好**：保存截图、console 日志，方便问题复现
