# 前端性能优化指南

## Core Web Vitals 优化

### 1. LCP (Largest Contentful Paint) - 最大内容绘制

**目标**: < 2.5 秒

**优化策略**：

```typescript
// ✅ 图片优化
import Image from 'next/image';

// Next.js Image 组件自动优化
<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority  // 关键图片预加载
  quality={85}
/>

// ✅ 使用现代图片格式
<picture>
  <source srcSet="/hero.avif" type="image/avif" />
  <source srcSet="/hero.webp" type="image/webp" />
  <img src="/hero.jpg" alt="Hero" />
</picture>

// ✅ 预加载关键资源
<link rel="preload" as="image" href="/hero.jpg" />
<link rel="preload" as="font" href="/font.woff2" crossOrigin="anonymous" />

// ❌ 避免大型未优化图片
<img src="/huge-image.png" />  // 5MB 原图
```

### 2. FID (First Input Delay) - 首次输入延迟

**目标**: < 100 毫秒

**优化策略**：

```typescript
// ✅ 代码分割和懒加载
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}

// ✅ 使用 Web Workers 处理密集计算
// worker.ts
self.onmessage = (e) => {
  const result = heavyComputation(e.data);
  self.postMessage(result);
};

// main.ts
const worker = new Worker('worker.ts');
worker.postMessage(data);
worker.onmessage = (e) => {
  console.log('Result:', e.data);
};

// ✅ 防抖和节流
import { debounce } from 'lodash-es';

const handleSearch = debounce((query: string) => {
  // 搜索逻辑
}, 300);

// ❌ 避免长任务阻塞主线程
function processLargeArray(arr: any[]) {
  // 同步处理 10000 个元素 - 会阻塞 UI
  return arr.map(item => heavyProcess(item));
}
```

### 3. CLS (Cumulative Layout Shift) - 累积布局偏移

**目标**: < 0.1

**优化策略**：

```typescript
// ✅ 为图片和视频指定尺寸
<img 
  src="/image.jpg" 
  width={800} 
  height={600}  // 防止加载时布局偏移
  alt="Description"
/>

// ✅ 为动态内容预留空间
<div className="skeleton h-64 w-full mb-4">
  {/* 骨架屏占位 */}
</div>

// ✅ 使用 CSS aspect-ratio
.video-container {
  aspect-ratio: 16 / 9;
  width: 100%;
}

// ❌ 避免在已渲染内容上方插入内容
// 不要在顶部动态插入广告或通知
```

## 代码分割策略

### 路由级别分割（Next.js）

```typescript
// app/dashboard/page.tsx
import { lazy } from 'react';

// 自动代码分割
export default function DashboardPage() {
  return <div>Dashboard</div>;
}

// 动态导入
const Analytics = lazy(() => import('@/components/Analytics'));
```

### 组件级别分割

```typescript
// ✅ 按需加载大型组件
import dynamic from 'next/dynamic';

const Chart = dynamic(() => import('@/components/Chart'), {
  loading: () => <p>Loading chart...</p>,
  ssr: false  // 仅客户端渲染
});

// ✅ 条件加载
function App() {
  const [showModal, setShowModal] = useState(false);
  
  const Modal = lazy(() => import('./Modal'));
  
  return (
    <>
      <button onClick={() => setShowModal(true)}>Open</button>
      {showModal && (
        <Suspense fallback={null}>
          <Modal />
        </Suspense>
      )}
    </>
  );
}
```

## 资源优化

### 1. 字体优化

```typescript
// next.config.js
module.exports = {
  optimizeFonts: true,  // 自动优化字体
};

// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',  // 使用 font-display: swap
  variable: '--font-inter',
});

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}

// CSS
.text {
  font-family: var(--font-inter);
}
```

### 2. 图片优化

```typescript
// ✅ 响应式图片
<Image
  src="/hero.jpg"
  alt="Hero"
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  fill
  style={{ objectFit: 'cover' }}
/>

// ✅ 懒加载
<Image
  src="/below-fold.jpg"
  alt="Below fold"
  loading="lazy"
  width={800}
  height={600}
/>

// ✅ 占位符
<Image
  src="/image.jpg"
  alt="Image"
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
  width={800}
  height={600}
/>
```

### 3. CSS 优化

```css
/* ✅ 使用 CSS 变量 */
:root {
  --primary: #3b82f6;
  --secondary: #8b5cf6;
}

/* ✅ 避免复杂选择器 */
.button { }  /* 好 */
div > ul > li > a { }  /* 避免 */

/* ✅ 使用 will-change 提示浏览器 */
.animated {
  will-change: transform;
}

/* ✅ 使用 contain 优化渲染 */
.card {
  contain: layout style paint;
}
```

## 渲染优化

### 1. React 性能优化

```typescript
// ✅ 使用 memo 避免不必要的重渲染
import { memo } from 'react';

const ExpensiveComponent = memo(({ data }) => {
  return <div>{/* 复杂渲染 */}</div>;
});

// ✅ 使用 useMemo 缓存计算结果
const sortedData = useMemo(() => {
  return data.sort((a, b) => a.value - b.value);
}, [data]);

// ✅ 使用 useCallback 缓存函数
const handleClick = useCallback(() => {
  console.log('Clicked');
}, []);

// ✅ 虚拟滚动（大列表）
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={1000}
  itemSize={50}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>Item {index}</div>
  )}
</FixedSizeList>
```

### 2. 状态管理优化

```typescript
// ✅ 使用 Zustand（轻量级状态管理）
import create from 'zustand';

const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));

// ✅ 选择性订阅
function Counter() {
  const count = useStore((state) => state.count);  // 只订阅 count
  return <div>{count}</div>;
}

// ❌ 避免全局订阅
function Counter() {
  const store = useStore();  // 订阅整个 store
  return <div>{store.count}</div>;
}
```

## 网络优化

### 1. 预加载和预连接

```typescript
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <head>
        {/* 预连接到 API 域名 */}
        <link rel="preconnect" href="https://api.example.com" />
        <link rel="dns-prefetch" href="https://api.example.com" />
        
        {/* 预加载关键资源 */}
        <link rel="preload" href="/critical.css" as="style" />
        <link rel="preload" href="/font.woff2" as="font" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

### 2. 数据获取优化

```typescript
// ✅ 使用 SWR 缓存和重新验证
import useSWR from 'swr';

function Profile() {
  const { data, error } = useSWR('/api/user', fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 60000,  // 60秒内去重
  });
  
  if (error) return <div>Failed to load</div>;
  if (!data) return <div>Loading...</div>;
  return <div>Hello {data.name}!</div>;
}

// ✅ 并行请求
const [user, posts] = await Promise.all([
  fetch('/api/user').then(r => r.json()),
  fetch('/api/posts').then(r => r.json()),
]);
```

## 监控和测试

### 使用 Lighthouse

```bash
# 安装 Lighthouse CI
npm install -g @lhci/cli

# 运行 Lighthouse
lhci autorun --collect.url=http://localhost:3000
```

### Web Vitals 监控

```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

## 最佳实践清单

- ✅ 使用 Next.js Image 组件优化图片
- ✅ 启用代码分割和懒加载
- ✅ 为图片和视频指定尺寸
- ✅ 使用现代图片格式（WebP/AVIF）
- ✅ 预加载关键资源
- ✅ 使用 memo/useMemo/useCallback
- ✅ 实现虚拟滚动（大列表）
- ✅ 启用 gzip/brotli 压缩
- ✅ 使用 CDN 分发静态资源
- ✅ 监控 Core Web Vitals

