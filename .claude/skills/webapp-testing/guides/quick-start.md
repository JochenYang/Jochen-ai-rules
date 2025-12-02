# Web 应用测试快速上手

本指南帮助你快速掌握 Playwright 自动化测试的核心操作。

---

## 安装与环境检查

### 1. 安装 Playwright

```bash
# 安装 Python Playwright 库
pip install playwright

# 安装浏览器驱动
playwright install chromium
```

### 2. 验证安装

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    print("✅ Playwright 安装成功")
    browser.close()
```

---

## 快速开始：5 分钟上手

### 示例 1：测试静态 HTML 页面

```python
from playwright.sync_api import sync_playwright

# 假设你有一个静态 HTML 文件
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 使用 file:// URL 打开本地文件
    page.goto('file:///Users/username/project/index.html')
    
    # 截图
    page.screenshot(path='/tmp/static_page.png')
    
    # 点击按钮
    page.click('button#submit')
    
    browser.close()
```

### 示例 2：测试本地开发服务器

**前提**：服务器已运行在 `http://localhost:5173`

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 访问本地服务器
    page.goto('http://localhost:5173')
    
    # 关键步骤：等待 JS 完成
    page.wait_for_load_state('networkidle')
    
    # 截图查看页面
    page.screenshot(path='/tmp/app.png', full_page=True)
    
    # 点击登录按钮
    page.click('text=登录')
    
    # 填写表单
    page.fill('input[name="username"]', 'testuser')
    page.fill('input[name="password"]', 'password123')
    
    # 提交
    page.click('button[type="submit"]')
    
    # 等待页面跳转
    page.wait_for_url('**/dashboard')
    
    browser.close()
```

---

## 使用 with_server.py：自动管理服务器

### 为什么使用 with_server.py？

❌ **手动方式**（麻烦）：
```bash
# 终端 1
npm run dev

# 终端 2
python test.py

# 测试完成后手动停止服务器
```

✅ **自动方式**（推荐）：
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python test.py
```

**优势**：
- ✅ 自动启动服务器
- ✅ 自动等待服务器就绪
- ✅ 测试完成后自动停止服务器
- ✅ 支持多个服务器同时运行

---

## with_server.py 使用指南

### 1. 查看帮助

```bash
python scripts/with_server.py --help
```

### 2. 单服务器示例

```bash
# 启动 Vite 前端服务器并运行测试
python scripts/with_server.py \
  --server "npm run dev" \
  --port 5173 \
  -- python test_frontend.py
```

**参数说明**：
- `--server`：启动服务器的命令
- `--port`：服务器端口（用于健康检查）
- `--`：分隔符，后面是测试脚本

### 3. 多服务器示例（前后端分离项目）

```bash
python scripts/with_server.py \
  --server "cd backend && uvicorn main:app --port 3000" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python test_fullstack.py
```

**场景**：
- 后端 API 运行在 `http://localhost:3000`
- 前端 UI 运行在 `http://localhost:5173`
- 测试脚本需要两者都就绪

### 4. 测试脚本示例（配合 with_server.py）

`test_fullstack.py`：
```python
from playwright.sync_api import sync_playwright

# 服务器已由 with_server.py 启动并就绪
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 前端访问（调用后端 API）
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')
    
    # 测试操作...
    page.click('text=获取用户列表')
    
    # 验证 API 调用成功
    page.wait_for_selector('text=用户加载成功')
    
    browser.close()
```

---

## 核心操作速查表

### 导航与等待

| 操作 | 代码 | 说明 |
|------|------|------|
| 访问 URL | `page.goto('http://localhost:5173')` | 导航到指定页面 |
| 等待加载完成 | `page.wait_for_load_state('networkidle')` | 等待网络空闲（动态应用必须） |
| 等待元素出现 | `page.wait_for_selector('button#submit')` | 等待特定元素可见 |
| 等待 URL 改变 | `page.wait_for_url('**/success')` | 等待页面跳转 |
| 固定延迟 | `page.wait_for_timeout(1000)` | 等待 1 秒（不推荐） |

### 元素操作

| 操作 | 代码 | 说明 |
|------|------|------|
| 点击按钮 | `page.click('button#submit')` | CSS 选择器 |
| 点击文本 | `page.click('text=登录')` | 文本选择器 |
| 点击角色元素 | `page.click('role=button[name="提交"]')` | ARIA 角色选择器 |
| 填写输入框 | `page.fill('input[name="username"]', 'admin')` | 清空并输入 |
| 输入文本（追加） | `page.type('textarea', '追加内容')` | 逐字符输入 |
| 选择下拉框 | `page.select_option('select#city', 'beijing')` | 选择选项 |
| 勾选复选框 | `page.check('input#agree-terms')` | 勾选 |
| 取消勾选 | `page.uncheck('input#subscribe')` | 取消勾选 |

### 信息获取

| 操作 | 代码 | 说明 |
|------|------|------|
| 截图 | `page.screenshot(path='/tmp/page.png')` | 保存当前视口截图 |
| 全页截图 | `page.screenshot(path='/tmp/full.png', full_page=True)` | 保存完整页面 |
| 获取 HTML | `html = page.content()` | 获取 DOM 结构 |
| 获取元素文本 | `text = page.locator('h1').inner_text()` | 获取元素内容 |
| 获取属性 | `href = page.locator('a').get_attribute('href')` | 获取 HTML 属性 |
| 检查元素可见性 | `is_visible = page.locator('button').is_visible()` | 返回 True/False |

### 元素查找（侦察阶段）

```python
# 发现所有按钮
buttons = page.locator('button').all()
for btn in buttons:
    print(btn.inner_text())

# 发现所有链接
links = page.locator('a[href]').all()
for link in links:
    print(f"{link.inner_text()} -> {link.get_attribute('href')}")

# 发现所有输入框
inputs = page.locator('input, textarea, select').all()
for inp in inputs:
    name = inp.get_attribute('name') or '[unnamed]'
    print(name)
```

---

## 选择器指南

### 1. 文本选择器（推荐）

最稳定，适用于按钮、链接等文本元素。

```python
page.click('text=登录')
page.click('text=提交订单')
page.click('text="精确匹配"')  # 精确匹配（含引号）
```

### 2. ARIA 角色选择器（推荐）

适用于符合无障碍标准的元素。

```python
page.click('role=button[name="提交"]')
page.click('role=link[name="首页"]')
page.fill('role=textbox[name="用户名"]', 'admin')
```

### 3. CSS 选择器

精确但脆弱（DOM 结构改变时易失效）。

```python
page.click('button#submit')
page.fill('input[name="username"]', 'admin')
page.click('.btn-primary')
```

### 4. XPath 选择器

强大但复杂，不推荐日常使用。

```python
page.click('//button[text()="提交"]')
```

### 选择器优先级

1. **优先**：`text=`、`role=`（语义化、稳定）
2. **次选**：`id`、`data-testid`（明确标记）
3. **避免**：复杂的 CSS 类选择器（易变）

---

## 等待策略详解

### 1. networkidle（动态应用必须）

等待网络请求完成（JS 加载、API 调用）。

```python
page.goto('http://localhost:5173')
page.wait_for_load_state('networkidle')  # 关键！
```

**适用场景**：
- React、Vue、Angular 等 SPA 应用
- 动态加载数据的页面

### 2. 等待特定元素

```python
# 等待登录按钮出现（最多等 5 秒）
page.wait_for_selector('button#login', timeout=5000)

# 等待加载动画消失
page.wait_for_selector('.loading-spinner', state='hidden')
```

### 3. 等待 URL 改变

```python
page.click('button#submit')
page.wait_for_url('**/success')  # 等待跳转到成功页面
```

### 4. 固定延迟（不推荐）

```python
# 仅在无法使用其他等待策略时使用
page.wait_for_timeout(2000)  # 等待 2 秒
```

**缺点**：
- ❌ 无法根据实际加载速度调整
- ❌ 要么等待过长，要么不够稳定

---

## 常见问题与解决方案

### 问题 1：元素未找到

**错误信息**：
```
playwright._impl._api_types.TimeoutError: Timeout 30000ms exceeded.
```

**原因**：元素不存在或页面未完全加载。

**解决方案**：
```python
# 1. 确保页面加载完成
page.goto('http://localhost:5173')
page.wait_for_load_state('networkidle')  # 添加这一行

# 2. 使用截图检查页面状态
page.screenshot(path='/tmp/debug.png', full_page=True)

# 3. 检查元素是否存在
print(page.content())  # 打印 HTML 结构
```

### 问题 2：点击无响应

**原因**：元素被遮挡或不可见。

**解决方案**：
```python
# 1. 检查元素可见性
is_visible = page.locator('button#submit').is_visible()
print(f"按钮可见: {is_visible}")

# 2. 强制点击（忽略遮挡）
page.click('button#submit', force=True)

# 3. 等待元素可点击
page.wait_for_selector('button#submit', state='visible')
page.click('button#submit')
```

### 问题 3：服务器未就绪

**现象**：测试失败，提示连接被拒绝。

**解决方案**：使用 `with_server.py`
```bash
# 自动等待服务器就绪
python scripts/with_server.py \
  --server "npm run dev" --port 5173 \
  -- python test.py
```

### 问题 4：截图为空白

**原因**：JS 未执行完成。

**解决方案**：
```python
page.goto('http://localhost:5173')
page.wait_for_load_state('networkidle')  # 必须等待
page.screenshot(path='/tmp/page.png')
```

---

## 完整示例：端到端测试模板

### 模板 1：表单提交测试

```python
from playwright.sync_api import sync_playwright
import sys

def test_form_submission():
    """测试表单提交流程"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 1. 导航
            print("1. 打开表单页...")
            page.goto('http://localhost:5173/form')
            page.wait_for_load_state('networkidle')
            
            # 2. 填写表单
            print("2. 填写表单...")
            page.fill('input[name="name"]', '张三')
            page.fill('input[name="email"]', 'zhangsan@example.com')
            page.select_option('select[name="city"]', 'beijing')
            page.check('input[name="agree"]')
            
            # 3. 截图（提交前）
            page.screenshot(path='/tmp/form_before.png')
            
            # 4. 提交
            print("3. 提交表单...")
            page.click('button:has-text("提交")')
            
            # 5. 验证结果
            print("4. 验证提交成功...")
            page.wait_for_selector('text=提交成功', timeout=5000)
            page.screenshot(path='/tmp/form_after.png')
            
            print("✅ 测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            page.screenshot(path='/tmp/error.png')
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_form_submission()
    sys.exit(0 if success else 1)
```

### 模板 2：侦察脚本（元素发现）

```python
from playwright.sync_api import sync_playwright

def discover_page_elements(url):
    """侦察页面元素"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"正在侦察: {url}")
        page.goto(url)
        page.wait_for_load_state('networkidle')
        
        # 截图
        page.screenshot(path='/tmp/discover.png', full_page=True)
        print("截图已保存: /tmp/discover.png")
        
        # 发现按钮
        buttons = page.locator('button').all()
        print(f"\n发现 {len(buttons)} 个按钮:")
        for i, btn in enumerate(buttons):
            text = btn.inner_text() if btn.is_visible() else "[隐藏]"
            print(f"  [{i}] {text}")
        
        # 发现链接
        links = page.locator('a[href]').all()
        print(f"\n发现 {len(links)} 个链接:")
        for link in links[:10]:  # 只显示前 10 个
            text = link.inner_text().strip()[:30]
            href = link.get_attribute('href')
            print(f"  - {text} -> {href}")
        
        # 发现输入框
        inputs = page.locator('input, textarea, select').all()
        print(f"\n发现 {len(inputs)} 个输入框:")
        for inp in inputs:
            name = inp.get_attribute('name') or inp.get_attribute('id') or "[unnamed]"
            inp_type = inp.get_attribute('type') or 'text'
            print(f"  - {name} ({inp_type})")
        
        browser.close()

if __name__ == "__main__":
    discover_page_elements('http://localhost:5173')
```

**使用方式**：
```bash
python scripts/with_server.py \
  --server "npm run dev" --port 5173 \
  -- python discover.py
```

---

## 调试技巧

### 1. 可视化调试（查看浏览器）

```python
# 设置 headless=False 查看浏览器窗口
browser = p.chromium.launch(headless=False, slow_mo=500)  # 放慢 500ms
```

### 2. 保存失败时的截图

```python
try:
    page.click('button#submit')
except Exception as e:
    page.screenshot(path='/tmp/error.png')
    print(f"错误截图已保存: {e}")
    raise
```

### 3. 打印 Console 日志

```python
page.on("console", lambda msg: print(f"[Console] {msg.text}"))
page.on("pageerror", lambda e: print(f"[Error] {e}"))
```

### 4. 网络请求监控

```python
page.on("request", lambda req: print(f"→ {req.method} {req.url}"))
page.on("response", lambda res: print(f"← {res.status} {res.url}"))
```

---

## 下一步

- **深入学习**：阅读 `workflows/webapp-testing.md` 了解完整测试流程
- **查看示例**：参考 `examples/` 目录中的实战案例
- **使用工具**：熟练掌握 `scripts/with_server.py` 自动化服务器管理
- **最佳实践**：遵循"侦察-执行"模式，优先使用语义化选择器

**祝你测试愉快！** 🚀
