# 快速开始指南

## 5 分钟创建第一个原型

### 步骤 1：初始化项目

```bash
bash scripts/init-artifact.sh my-first-prototype
cd my-first-prototype
```

**发生了什么**：
- 创建 React + TypeScript + Vite 项目
- 安装 Tailwind CSS 和 shadcn/ui
- 配置 40+ UI 组件
- 设置打包工具

---

### 步骤 2：编辑 App.tsx

```typescript
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

function App() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-4">我的第一个原型</h1>
      <Card className="p-6">
        <p className="mb-4">这是一个快速原型演示</p>
        <Button onClick={() => alert('点击成功!')}>
          点击我
        </Button>
      </Card>
    </div>
  );
}

export default App;
```

---

### 步骤 3：打包

```bash
bash scripts/bundle-artifact.sh
```

**输出**：生成 `bundle.html` 文件

---

### 步骤 4：分享

将 `bundle.html` 发送给任何人，他们用浏览器打开即可看到效果！

---

## 常用组件速查

### 按钮
```typescript
import { Button } from '@/components/ui/button';

<Button>默认按钮</Button>
<Button variant="destructive">危险按钮</Button>
<Button variant="outline">轮廓按钮</Button>
<Button variant="ghost">幽灵按钮</Button>
```

### 卡片
```typescript
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>标题</CardTitle>
  </CardHeader>
  <CardContent>
    内容区域
  </CardContent>
</Card>
```

### 表单输入
```typescript
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

<div>
  <Label htmlFor="email">邮箱</Label>
  <Input id="email" type="email" placeholder="your@email.com" />
</div>
```

### 对话框
```typescript
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

<Dialog>
  <DialogTrigger asChild>
    <Button>打开对话框</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>对话框标题</DialogTitle>
    </DialogHeader>
    <p>对话框内容</p>
  </DialogContent>
</Dialog>
```

### 下拉选择
```typescript
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

<Select>
  <SelectTrigger>
    <SelectValue placeholder="选择选项" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">选项 1</SelectItem>
    <SelectItem value="option2">选项 2</SelectItem>
  </SelectContent>
</Select>
```

---

## 常见布局

### 居中容器
```typescript
<div className="container mx-auto max-w-4xl p-8">
  {/* 内容 */}
</div>
```

### 网格布局
```typescript
<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
  <Card>卡片 1</Card>
  <Card>卡片 2</Card>
  <Card>卡片 3</Card>
</div>
```

### Flex 布局
```typescript
<div className="flex items-center justify-between gap-4">
  <div>左侧</div>
  <div>右侧</div>
</div>
```

---

## 状态管理示例

### 简单状态
```typescript
import { useState } from 'react';
import { Button } from '@/components/ui/button';

function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>计数: {count}</p>
      <Button onClick={() => setCount(count + 1)}>
        增加
      </Button>
    </div>
  );
}
```

### 表单状态
```typescript
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  const onSubmit = (data) => {
    console.log(data);
    alert('提交成功！');
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Input 
          {...register('email', { required: '邮箱必填' })} 
          placeholder="邮箱" 
        />
        {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
      </div>
      
      <div>
        <Input 
          {...register('password', { required: '密码必填', minLength: 6 })} 
          type="password" 
          placeholder="密码" 
        />
        {errors.password && <p className="text-red-500 text-sm">{errors.password.message}</p>}
      </div>
      
      <Button type="submit">登录</Button>
    </form>
  );
}
```

---

## 响应式设计

### Tailwind 响应式断点
```
sm: 640px   # 手机横屏
md: 768px   # 平板
lg: 1024px  # 笔记本
xl: 1280px  # 桌面
2xl: 1536px # 大屏
```

### 示例
```typescript
<div className="text-sm md:text-base lg:text-lg">
  响应式文字大小
</div>

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  响应式网格布局
</div>
```

---

## 调试技巧

### 查看组件状态
```typescript
console.log('当前状态:', { count, user, data });
```

### 实时预览
```bash
npm run dev  # 开发模式，实时预览
```

### 浏览器开发工具
- F12 打开开发者工具
- Console 查看日志
- Elements 检查样式
- Network 查看请求

---

## 完整示例：待办事项

```typescript
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';

function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');
  
  const addTodo = () => {
    if (input.trim()) {
      setTodos([...todos, { id: Date.now(), text: input, done: false }]);
      setInput('');
    }
  };
  
  const toggleTodo = (id) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, done: !todo.done } : todo
    ));
  };
  
  return (
    <div className="container mx-auto max-w-2xl p-8">
      <h1 className="text-3xl font-bold mb-6">待办事项</h1>
      
      <div className="flex gap-2 mb-6">
        <Input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="添加新任务..."
          onKeyPress={(e) => e.key === 'Enter' && addTodo()}
        />
        <Button onClick={addTodo}>添加</Button>
      </div>
      
      <div className="space-y-2">
        {todos.map(todo => (
          <Card key={todo.id} className="p-4">
            <div className="flex items-center gap-3">
              <Checkbox 
                checked={todo.done}
                onCheckedChange={() => toggleTodo(todo.id)}
              />
              <span className={todo.done ? 'line-through text-gray-400' : ''}>
                {todo.text}
              </span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default TodoApp;
```

---

## 下一步

- 查看 `workflows/artifact-building.md` 了解完整开发流程
- 访问 https://ui.shadcn.com/docs/components 查看所有组件
- 访问 https://tailwindcss.com/docs 学习 Tailwind CSS
