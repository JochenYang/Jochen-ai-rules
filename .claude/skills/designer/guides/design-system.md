# 设计系统指南

## 设计系统核心

设计系统是一套可复用的组件、样式和规范，确保产品的一致性和可维护性。

---

## 颜色系统

### 主色调
```
Primary: #3B82F6 (蓝色)
Secondary: #8B5CF6 (紫色)
Accent: #10B981 (绿色)
```

### 语义色
```
Success: #10B981 (绿色)
Warning: #F59E0B (橙色)
Error: #EF4444 (红色)
Info: #3B82F6 (蓝色)
```

### 中性色
```
Gray-50: #F9FAFB
Gray-100: #F3F4F6
Gray-200: #E5E7EB
Gray-300: #D1D5DB
Gray-400: #9CA3AF
Gray-500: #6B7280
Gray-600: #4B5563
Gray-700: #374151
Gray-800: #1F2937
Gray-900: #111827
```

### 使用原则
- **主色调**：品牌识别、主要操作
- **语义色**：状态反馈、提示信息
- **中性色**：文本、背景、边框
- **对比度**：文本对比度 ≥ 4.5:1

---

## 字体系统

### 字体家族
```
Sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
Mono: "SF Mono", Monaco, "Cascadia Code", monospace
```

### 字号层级
```
xs: 12px / 0.75rem
sm: 14px / 0.875rem
base: 16px / 1rem
lg: 18px / 1.125rem
xl: 20px / 1.25rem
2xl: 24px / 1.5rem
3xl: 30px / 1.875rem
4xl: 36px / 2.25rem
```

### 字重
```
Light: 300
Regular: 400
Medium: 500
Semibold: 600
Bold: 700
```

### 行高
```
Tight: 1.25
Normal: 1.5
Relaxed: 1.75
```

---

## 间距系统

### 基准间距（8px 基准）
```
0: 0px
1: 4px
2: 8px
3: 12px
4: 16px
5: 20px
6: 24px
8: 32px
10: 40px
12: 48px
16: 64px
20: 80px
```

### 使用原则
- **内边距**：组件内部间距
- **外边距**：组件之间间距
- **栅格**：布局网格间距
- **一致性**：使用统一的间距值

---

## 组件库

### 按钮（Button）

**变体**
- Primary：主要操作
- Secondary：次要操作
- Outline：边框按钮
- Ghost：透明按钮
- Link：链接样式

**尺寸**
- Small：32px 高度
- Medium：40px 高度（默认）
- Large：48px 高度

**状态**
- Default：默认状态
- Hover：悬停状态
- Active：激活状态
- Disabled：禁用状态
- Loading：加载状态

---

### 输入框（Input）

**类型**
- Text：文本输入
- Email：邮箱输入
- Password：密码输入
- Number：数字输入
- Search：搜索输入

**状态**
- Default：默认状态
- Focus：聚焦状态
- Error：错误状态
- Disabled：禁用状态

**附加元素**
- Label：标签
- Placeholder：占位符
- Helper Text：帮助文本
- Error Message：错误提示
- Icon：图标

---

### 卡片（Card）

**结构**
- Header：标题区域
- Body：内容区域
- Footer：底部区域

**变体**
- Default：默认卡片
- Outlined：边框卡片
- Elevated：阴影卡片

**交互**
- Static：静态卡片
- Clickable：可点击卡片
- Hoverable：悬停效果

---

### 模态框（Modal）

**尺寸**
- Small：400px 宽度
- Medium：600px 宽度
- Large：800px 宽度
- Full：全屏

**结构**
- Header：标题和关闭按钮
- Body：内容区域
- Footer：操作按钮

**行为**
- 点击遮罩关闭
- ESC 键关闭
- 滚动锁定
- 焦点管理

---

### 通知（Toast/Alert）

**类型**
- Success：成功提示
- Warning：警告提示
- Error：错误提示
- Info：信息提示

**位置**
- Top：顶部
- Bottom：底部
- Top Right：右上角
- Bottom Right：右下角

**行为**
- 自动消失（3-5 秒）
- 手动关闭
- 堆叠显示

---

## 图标系统

### 图标库
- **Heroicons**：简洁现代
- **Lucide**：轻量级
- **Feather**：极简风格
- **Material Icons**：丰富全面

### 使用原则
- **尺寸一致**：16px、20px、24px
- **风格统一**：使用同一图标库
- **语义明确**：图标含义清晰
- **可访问性**：提供替代文本

---

## 响应式设计

### 断点
```
sm: 640px   (手机横屏)
md: 768px   (平板)
lg: 1024px  (小屏笔记本)
xl: 1280px  (桌面)
2xl: 1536px (大屏)
```

### 布局策略
- **移动优先**：从小屏开始设计
- **流式布局**：使用百分比和 flex
- **响应式图片**：使用 srcset
- **触摸友好**：按钮至少 44x44px

---

## 动画和过渡

### 过渡时间
```
Fast: 150ms
Normal: 300ms
Slow: 500ms
```

### 缓动函数
```
Ease: cubic-bezier(0.4, 0, 0.2, 1)
Ease In: cubic-bezier(0.4, 0, 1, 1)
Ease Out: cubic-bezier(0, 0, 0.2, 1)
Ease In Out: cubic-bezier(0.4, 0, 0.2, 1)
```

### 使用原则
- **有意义**：动画应有目的
- **流畅**：60fps 流畅度
- **适度**：避免过度动画
- **可关闭**：尊重用户偏好

---

## 可访问性

### WCAG 标准
- **对比度**：文本对比度 ≥ 4.5:1
- **键盘导航**：所有功能可键盘操作
- **屏幕阅读器**：提供 ARIA 标签
- **焦点指示**：清晰的焦点样式

### 语义化 HTML
- 使用正确的 HTML 标签
- 提供 alt 文本
- 使用 label 关联表单
- 使用 heading 层级

---

## 设计 Token

### CSS 变量示例
```css
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-success: #10B981;
  --color-error: #EF4444;
  
  /* Spacing */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-4: 16px;
  
  /* Typography */
  --font-sans: -apple-system, sans-serif;
  --font-size-base: 16px;
  --line-height-normal: 1.5;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

