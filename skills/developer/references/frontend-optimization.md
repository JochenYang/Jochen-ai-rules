# Frontend Performance Optimization

Techniques for optimizing web application performance.

## Core Web Vitals

| Metric | Target | Description |
|--------|--------|-------------|
| LCP | < 2.5s | Largest Contentful Paint |
| FID | < 100ms | First Input Delay |
| CLS | < 0.1 | Cumulative Layout Shift |

## Loading Performance

### Code Splitting
```javascript
// Dynamic imports for route-based splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

// Component-level splitting
const HeavyChart = lazy(() => import('./components/HeavyChart'));
```

### Tree Shaking
```javascript
// package.json
{
  "sideEffects": false
}

// Import only what you need
import { useState, useEffect } from 'react';
import { debounce, throttle } from 'lodash-es';
```

### Preloading
```html
<!-- Preload critical assets -->
<link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>

<!-- Prefetch next route -->
<link rel="prefetch" href="/dashboard" as="document">
```

## Runtime Performance

### Memoization
```javascript
import { memo, useMemo, useCallback } from 'react';

const ExpensiveComponent = memo(({ data, onProcess }) => {
  const processed = useMemo(() => {
    return data.reduce((acc, item) => acc + item.value, 0);
  }, [data]);

  const handleClick = useCallback(() => {
    onProcess(processed);
  }, [processed, onProcess]);

  return <div>{processed}</div>;
});
```

### Virtual Scrolling
```javascript
import { FixedSizeList as List } from 'react-window';

const Row = ({ index, style }) => (
  <div style={style}>Row {index}</div>
);

<List
  height={600}
  itemCount={10000}
  itemSize={35}
  width="100%"
>
  {Row}
</List>
```

## Bundle Optimization

### Analyzer
```bash
npx webpack-bundle-analyzer stats.json
```

### Optimization Strategies
- Remove unused code
- Compress images
- Use WebP/AVIF
- Implement lazy loading
- Use CDN for static assets

## Rendering Optimization

### CSS Performance
```css
/* Good: Use transform and opacity for animations */
.element {
  transform: translateX(100px);
  opacity: 0.5;
}

/* Avoid: Layout-triggering properties */
.element {
  width: 100px;
  height: 100px;
  padding: 20px;
  margin: 10px;
}
```

### Batch Updates
```javascript
// Bad: Multiple re-renders
setCount(count + 1);
setName('New Name');
setItems([...items, newItem]);

// Good: Single state object or batched updates
setState(prev => ({
  ...prev,
  count: prev.count + 1,
  name: 'New Name',
  items: [...prev.items, newItem]
}));
```
