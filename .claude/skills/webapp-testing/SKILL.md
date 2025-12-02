---
name: webapp-testing
description: 本地 Web 应用自动化测试：Playwright 脚本编写、服务器生命周期管理、UI 交互验证、截图捕获与日志查看。支持静态 HTML 和动态应用，包含服务器管理脚本和测试示例
---

# Web 应用自动化测试

基于 Playwright 的本地 Web 应用测试工具，用于前端功能验证和 UI 调试。

## 核心能力

- Playwright Python 同步 API 测试脚本
- 服务器生命周期自动管理
- 侦察-执行模式（先截图识别，后操作）
- 浏览器日志和网络请求捕获

## 技术栈

- **Playwright**：Python 同步 API
- **浏览器**：Chromium（headless）
- **服务器管理**：`scripts/with_server.py`

## 可执行工具

以下脚本可直接运行（使用 `--help` 查看用法）：

- `scripts/with_server.py` - 服务器生命周期管理

```bash
# 单服务器
python scripts/with_server.py --server "npm run dev" --port 5173 -- python test.py

# 多服务器
python scripts/with_server.py \
  --server "python server.py" --port 3000 \
  --server "npm run dev" --port 5173 \
  -- python test.py
```

## 快速开始

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')
    # 测试逻辑...
    browser.close()
```

## 设计原则

1. **侦察-执行分离**：先截图/DOM 识别，再操作
2. **等待策略**：动态应用必须 `wait_for_load_state('networkidle')`
3. **语义化选择器**：优先 `text=`、`role=` 而非 CSS 选择器
4. **资源清理**：始终调用 `browser.close()`

## 边界

专注于本地 localhost 功能验证和 UI 自动化，不处理远程应用测试和性能基准测试。

## 详细参考

- `workflows/webapp-testing.md` - 完整测试流程
- `guides/quick-start.md` - 快速上手指南
- `examples/` - 测试示例代码
