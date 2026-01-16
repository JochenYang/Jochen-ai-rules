# Web Vitals Optimization Guide

Best practices for optimizing Core Web Vitals.

## Core Web Vitals Overview

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | ≤ 2.5s | ≤ 4s | > 4s |
| FID | ≤ 100ms | ≤ 300ms | > 300ms |
| CLS | ≤ 0.1 | ≤ 0.25 | > 0.25 |

## LCP (Largest Contentful Paint)

### Optimization Strategies

#### 1. Optimize Server Response Time
```javascript
// Cache responses
app.get('/api/data', cache('1 minute'), (req, res) => {
  res.json(database.query());
});
```

#### 2. Optimize Resource Loading
```html
<!-- Preload critical resources -->
<link rel="preload" href="hero-image.jpg" as="image">

<!-- Preconnect to origins -->
<link rel="preconnect" href="https://cdn.example.com">
```

#### 3. Optimize Images
```javascript
// Next.js Image component
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority  // Preload for LCP
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>
```

#### 4. Remove Unused CSS/JS
```javascript
// Dynamic imports for non-critical code
const HeavyComponent = dynamic(
  () => import('./HeavyComponent'),
  { loading: () => <p>Loading...</p> }
);
```

## FID (First Input Delay) / INP (Interaction to Next Paint)

### Optimization Strategies

#### 1. Minimize JavaScript Execution
```javascript
// Break up long tasks
function processItems(items) {
  const chunkSize = 100;
  let index = 0;

  function processNextChunk() {
    const end = Math.min(index + chunkSize, items.length);
    for (; index < end; index++) {
      processItem(items[index]);
    }
    if (index < items.length) {
      requestIdleCallback(processNextChunk);
    }
  }

  requestIdleCallback(processNextChunk);
}
```

#### 2. Defer Non-Critical JavaScript
```html
<script src="analytics.js" defer></script>
<script src="third-party.js" defer></script>
```

#### 3. Use Web Workers
```javascript
// Offload heavy computation
const worker = new Worker('processor.js');

worker.postMessage(heavyData);
worker.onmessage = (e) => {
  displayResults(e.data);
};
```

## CLS (Cumulative Layout Shift)

### Optimization Strategies

#### 1. Reserve Space for Images
```css
/* Aspect ratio boxes */
.image-container {
  aspect-ratio: 16 / 9;
  width: 100%;
}

/* Placeholder for ads */
.ad-slot {
  min-height: 250px;
  background: #f0f0f0;
}
```

#### 2. Preload Fonts
```html
<link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
```

#### 3. Avoid Animations That Trigger Layout
```css
/* Good: Transform and opacity don't trigger layout */
.element {
  transform: translateX(100px);
  opacity: 0.5;
}

/* Bad: Triggers layout */
.element {
  width: 100px;
  height: 100px;
}
```

#### 4. Dynamically Injected Content
```javascript
// Reserve space before inserting
const container = document.getElementById('container');
container.style.minHeight = '200px';

fetchData().then(data => {
  container.innerHTML = renderContent(data);
  container.style.minHeight = '';
});
```

## Monitoring

### Real User Monitoring (RUM)
```javascript
// Web Vitals API
import { getCLS, getFID, getLCP } from 'web-vitals';

function sendToAnalytics({ name, delta, id }) {
  gtag('event', name, {
    event_category: 'Web Vitals',
    event_label: id,
    value: Math.round(name === 'CLS' ? delta * 1000 : delta),
    non_interaction: true,
  });
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getLCP(sendToAnalytics);
```

### Synthetic Monitoring
```bash
# Lighthouse CI
npm install -D @lhci/cli

lhci autorun --collect-url https://example.com
```

## Budgets

### Performance Budgets
```json
{
  "budgets": [
    {
      "resourceSizes": [
        { "resourceType": "total", "budget": 300 },
        { "resourceType": "script", "budget": 100 },
        { "resourceType": "css", "budget": 20 },
        { "resourceType": "image", "budget": 150 }
      ],
      "resourceCounts": [
        { "resourceType": "third-party", "budget": 10 }
      ]
    }
  ]
}
```
