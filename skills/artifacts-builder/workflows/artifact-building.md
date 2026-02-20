# 原型构建工作流

## 流程概览

```
需求理解 → 技术方案 → 初始化项目 → 开发组件 → 打包部署 → 验证效果
```

---

## 阶段 1：需求理解

### 明确目标
- 原型用途（演示/验证/测试）
- 目标用户（客户/团队/测试用户）
- 核心功能（必须展示的功能点）
- 技术限制（浏览器兼容性、性能要求）

### 设计确认
- 交互流程
- 视觉风格
- 响应式需求
- 动画效果

---

## 阶段 2：技术方案

### 组件选择
根据需求选择合适的 shadcn/ui 组件：
- **表单**：Input、Select、Checkbox、Radio
- **展示**：Card、Table、Badge、Avatar
- **交互**：Button、Dialog、Dropdown、Tabs
- **反馈**：Toast、Alert、Progress

### 状态管理
- 简单状态：useState
- 复杂状态：useReducer 或 Context
- 表单状态：React Hook Form

---

## 阶段 3：初始化项目

### 执行初始化脚本
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

### 项目结构
```
<project-name>/
├── src/
│   ├── App.tsx          # 主组件
│   ├── components/      # 业务组件
│   └── lib/            # 工具函数
├── index.html
├── package.json
└── tailwind.config.js
```

---

## 阶段 4：开发组件

### 组件开发顺序
1. **布局组件**：定义整体结构
2. **展示组件**：静态内容展示
3. **交互组件**：添加用户交互
4. **状态管理**：连接数据流

### 代码规范
- 使用 TypeScript 类型定义
- 组件拆分合理（单一职责）
- 使用 Tailwind CSS 工具类
- 遵循 shadcn/ui 组件规范

---

## 阶段 5：打包部署

### 执行打包脚本
```bash
bash scripts/bundle-artifact.sh
```

### 输出
生成 `bundle.html` 文件，包含：
- 所有 JavaScript 代码（内联）
- 所有 CSS 样式（内联）
- 所有依赖库（内联）

---

## 阶段 6：验证效果

### 功能验证
- 核心功能是否正常
- 交互是否流畅
- 样式是否正确
- 响应式是否适配

### 性能验证
- 加载速度
- 交互响应
- 动画流畅度

---

## 常见场景

### 场景 1：表单原型
```typescript
// 快速创建表单原型
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

function LoginForm() {
  const { register, handleSubmit } = useForm();
  
  return (
    <form onSubmit={handleSubmit(console.log)}>
      <Input {...register('email')} placeholder="邮箱" />
      <Input {...register('password')} type="password" placeholder="密码" />
      <Button type="submit">登录</Button>
    </form>
  );
}
```

### 场景 2：数据展示
```typescript
// 快速创建数据展示原型
import { Card } from '@/components/ui/card';
import { Table } from '@/components/ui/table';

function Dashboard() {
  const data = [/* 模拟数据 */];
  
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Card>统计卡片 1</Card>
      <Card>统计卡片 2</Card>
      <Card>统计卡片 3</Card>
      <Table data={data} />
    </div>
  );
}
```

---

## 质量标准

### 代码质量
- TypeScript 类型完整
- 组件可读性好
- 无 console 错误
- 性能无明显问题

### 用户体验
- 交互符合预期
- 加载速度快
- 视觉效果好
- 响应式适配

---

## 快速参考

### shadcn/ui 组件文档
https://ui.shadcn.com/docs/components

### Tailwind CSS 文档
https://tailwindcss.com/docs

### React 文档
https://react.dev
