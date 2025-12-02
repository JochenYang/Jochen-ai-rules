# 安全审计工作流程

## 概述
本工作流程定义了完整的安全审计流程，涵盖 OWASP Top 10、认证授权、数据保护等关键安全领域。

---

## 阶段 1：安全威胁建模

### 1.1 识别资产和数据
**关键问题**：
- 系统处理哪些敏感数据？（用户信息、密码、支付数据）
- 哪些端点需要认证？
- 哪些操作需要授权检查？
- 有哪些外部依赖和第三方库？

**资产清单**：
- [ ] 用户凭据（密码、Token）
- [ ] 个人身份信息（PII）：姓名、邮箱、电话
- [ ] 支付信息：信用卡号、银行账户
- [ ] API 密钥和配置
- [ ] 业务数据：订单、交易记录

### 1.2 攻击面分析
**检查点**：
- [ ] 所有 HTTP 端点（API 路由）
- [ ] 文件上传功能
- [ ] 用户输入字段（表单、搜索框）
- [ ] 认证和会话管理
- [ ] 外部服务集成点

### 1.3 威胁识别（STRIDE 模型）
| 威胁类型 | 描述 | 示例 |
|---------|------|------|
| **S**poofing | 身份伪造 | 未验证 JWT 签名 |
| **T**ampering | 数据篡改 | SQL 注入修改数据 |
| **R**epudiation | 抵赖 | 缺少操作日志 |
| **I**nformation Disclosure | 信息泄露 | 敏感数据明文传输 |
| **D**enial of Service | 拒绝服务 | 无限流，资源耗尽 |
| **E**levation of Privilege | 权限提升 | 水平/垂直越权 |

---

## 阶段 2：OWASP Top 10 审计

### 2.1 A01 - 访问控制失效

#### 检查清单
```javascript
// ❌ 错误：未验证用户对资源的所有权
app.get('/api/orders/:id', async (req, res) => {
  const order = await db.query('SELECT * FROM orders WHERE id = ?', [req.params.id]);
  res.json(order);  // 任何人都能访问任何订单！
});

// ✅ 正确：验证所有权
app.get('/api/orders/:id', authenticateUser, async (req, res) => {
  const order = await db.query(
    'SELECT * FROM orders WHERE id = ? AND user_id = ?',
    [req.params.id, req.user.id]
  );
  
  if (!order) {
    return res.status(404).json({ error: 'Order not found' });
  }
  
  res.json(order);
});
```

**测试方法**：
```bash
# 水平越权测试
# 用户 A 的 Token 访问用户 B 的资源
curl -H "Authorization: Bearer USER_A_TOKEN" \
  https://api.example.com/api/users/USER_B_ID
```

### 2.2 A02 - 加密失败

#### 密码存储检查
```javascript
// ❌ 错误：明文存储密码
const user = { password: req.body.password };

// ❌ 错误：使用弱哈希（MD5/SHA1）
const hash = crypto.createHash('md5').update(password).digest('hex');

// ✅ 正确：bcrypt with salt rounds >= 12
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(password, 12);

// 验证
const isValid = await bcrypt.compare(plainPassword, hash);
```

#### HTTPS 强制
```javascript
// Express 中间件：强制 HTTPS
app.use((req, res, next) => {
  if (req.header('x-forwarded-proto') !== 'https' && process.env.NODE_ENV === 'production') {
    res.redirect(`https://${req.header('host')}${req.url}`);
  } else {
    next();
  }
});

// 添加 HSTS 头部
app.use((req, res, next) => {
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  next();
});
```

### 2.3 A03 - 注入攻击

#### SQL 注入防护
```javascript
// ❌ 危险：字符串拼接
const query = `SELECT * FROM users WHERE email = '${req.body.email}'`;
// 攻击：' OR '1'='1' --

// ✅ 安全：参数化查询
const query = 'SELECT * FROM users WHERE email = ?';
const result = await db.query(query, [req.body.email]);

// 或使用 ORM
const user = await User.findOne({ where: { email: req.body.email } });
```

#### XSS 防护
```javascript
// ❌ 危险：直接渲染用户输入
res.send(`<div>${req.body.comment}</div>`);
// 攻击：<script>alert('XSS')</script>

// ✅ 安全：输出编码
const escapeHtml = (text) => {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
};

res.send(`<div>${escapeHtml(req.body.comment)}</div>`);

// 或使用模板引擎（自动转义）
res.render('comment', { comment: req.body.comment });
```

#### CSP 头部配置
```javascript
// Content Security Policy
app.use((req, res, next) => {
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; " +
    "script-src 'self' https://trusted-cdn.com; " +
    "style-src 'self' 'unsafe-inline'; " +
    "img-src 'self' data: https:;"
  );
  next();
});
```

### 2.4 A04 - 不安全设计

#### API 限流
```javascript
const rateLimit = require('express-rate-limit');

// 登录限流（防止暴力破解）
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 5,                    // 最多 5 次尝试
  message: 'Too many login attempts, please try again later',
  standardHeaders: true,
  legacyHeaders: false
});

app.post('/api/login', loginLimiter, async (req, res) => {
  // 登录逻辑
});

// 账户锁定机制
async function checkAccountLock(email) {
  const attempts = await redis.get(`login_attempts:${email}`);
  
  if (attempts && parseInt(attempts) >= 5) {
    const lockUntil = await redis.ttl(`login_attempts:${email}`);
    throw new Error(`Account locked. Try again in ${Math.ceil(lockUntil / 60)} minutes`);
  }
}
```

#### 验证码保护
```javascript
// 关键操作需要验证码
const requireCaptcha = async (req, res, next) => {
  const { captchaToken } = req.body;
  
  // 验证 reCAPTCHA
  const response = await fetch('https://www.google.com/recaptcha/api/siteverify', {
    method: 'POST',
    body: JSON.stringify({
      secret: process.env.RECAPTCHA_SECRET,
      response: captchaToken
    })
  });
  
  const data = await response.json();
  
  if (!data.success) {
    return res.status(400).json({ error: 'Captcha verification failed' });
  }
  
  next();
};

// 应用于敏感操作
app.post('/api/register', requireCaptcha, registerUser);
app.post('/api/login', requireCaptcha, loginUser);
app.post('/api/reset-password', requireCaptcha, resetPassword);
```

### 2.5 A05 - 安全配置错误

#### 安全 HTTP 头部
```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"]
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));

// 手动配置
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'no-referrer');
  next();
});
```

#### CORS 配置
```javascript
// ❌ 危险：允许所有来源
app.use(cors({ origin: '*' }));

// ✅ 安全：白名单
const allowedOrigins = [
  'https://app.example.com',
  'https://admin.example.com'
];

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true
}));
```

#### 环境配置安全
```javascript
// ❌ 危险：生产环境启用调试
if (process.env.NODE_ENV === 'production') {
  app.set('env', 'development'); // 错误！
}

// ✅ 正确：生产环境配置
if (process.env.NODE_ENV === 'production') {
  app.set('env', 'production');
  app.disable('x-powered-by');  // 隐藏服务器信息
  app.set('trust proxy', 1);     // 信任代理
}

// 敏感信息通过环境变量管理
// .env
DB_PASSWORD=xxxxx
JWT_SECRET=xxxxx
API_KEY=xxxxx

// 永不提交 .env 到版本控制
// .gitignore
.env
.env.local
```

### 2.6 A06 - 易受攻击的组件

#### 依赖扫描
```bash
# npm audit（自动扫描）
npm audit

# 修复已知漏洞
npm audit fix

# 仅修复生产依赖
npm audit fix --only=prod

# Snyk 扫描（更全面）
npx snyk test

# 持续监控
npx snyk monitor
```

#### 依赖更新策略
```json
// package.json - 锁定主版本
{
  "dependencies": {
    "express": "^4.18.2",    // ✅ 允许小版本更新
    "lodash": "~4.17.21",    // ✅ 仅允许补丁更新
    "bcrypt": "4.0.1"        // ✅ 完全锁定版本
  }
}
```

### 2.7 A07 - 身份验证失败

#### JWT 安全实现
```javascript
const jwt = require('jsonwebtoken');

// 生成 Token
function generateToken(user) {
  return jwt.sign(
    {
      sub: user.id,
      email: user.email,
      roles: user.roles
    },
    process.env.JWT_SECRET,  // 强密钥（至少 256 位）
    {
      expiresIn: '1h',        // 短过期时间
      issuer: 'api.example.com',
      audience: 'app.example.com'
    }
  );
}

// 验证 Token
function verifyToken(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET, {
      issuer: 'api.example.com',
      audience: 'app.example.com'
    });
    
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

#### Session 安全配置
```javascript
const session = require('express-session');
const RedisStore = require('connect-redis')(session);

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,    // 防止 XSS 窃取
    secure: true,      // 仅 HTTPS 传输
    sameSite: 'strict', // 防止 CSRF
    maxAge: 3600000    // 1 小时
  }
}));
```

### 2.8 A10 - 服务端请求伪造（SSRF）

#### URL 验证
```javascript
const url = require('url');

// ❌ 危险：未验证 URL
app.post('/fetch', async (req, res) => {
  const data = await fetch(req.body.url);
  res.json(data);
});

// ✅ 安全：白名单验证
const ALLOWED_HOSTS = ['api.trusted.com', 'cdn.trusted.com'];

function validateUrl(inputUrl) {
  try {
    const parsed = new URL(inputUrl);
    
    // 1. 检查协议（只允许 https）
    if (parsed.protocol !== 'https:') {
      throw new Error('Only HTTPS URLs are allowed');
    }
    
    // 2. 检查主机白名单
    if (!ALLOWED_HOSTS.includes(parsed.hostname)) {
      throw new Error('Host not allowed');
    }
    
    // 3. 阻止内网 IP
    const privateIpRanges = [
      /^127\./, /^10\./, /^172\.(1[6-9]|2\d|3[01])\./,
      /^192\.168\./, /^169\.254\./, /^::1$/, /^fc00:/
    ];
    
    if (privateIpRanges.some(pattern => pattern.test(parsed.hostname))) {
      throw new Error('Private IP ranges are not allowed');
    }
    
    return true;
  } catch (err) {
    throw new Error(`Invalid URL: ${err.message}`);
  }
}

app.post('/fetch', async (req, res) => {
  try {
    validateUrl(req.body.url);
    const data = await fetch(req.body.url);
    res.json(data);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});
```

---

## 阶段 3：文件上传安全

### 3.1 文件验证
```javascript
const multer = require('multer');
const path = require('path');
const crypto = require('crypto');

// 文件类型白名单
const ALLOWED_TYPES = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
  'image/webp': 'webp',
  'application/pdf': 'pdf'
};

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    // 存储在 Web 根目录之外
    cb(null, '/var/uploads/');
  },
  filename: (req, file, cb) => {
    // 随机文件名（防止路径遍历）
    const randomName = crypto.randomBytes(16).toString('hex');
    const ext = ALLOWED_TYPES[file.mimetype];
    cb(null, `${randomName}.${ext}`);
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 5 * 1024 * 1024  // 5MB 限制
  },
  fileFilter: (req, file, cb) => {
    // 1. 检查 MIME 类型
    if (!ALLOWED_TYPES[file.mimetype]) {
      return cb(new Error('Invalid file type'));
    }
    
    // 2. 检查文件扩展名
    const ext = path.extname(file.originalname).toLowerCase();
    if (!Object.values(ALLOWED_TYPES).includes(ext.slice(1))) {
      return cb(new Error('Invalid file extension'));
    }
    
    cb(null, true);
  }
});

// 使用
app.post('/upload', upload.single('file'), async (req, res) => {
  // 3. 魔数验证（检查文件真实类型）
  const fileBuffer = await fs.readFile(req.file.path);
  const fileType = await import('file-type');
  const detected = await fileType.fromBuffer(fileBuffer);
  
  if (!detected || !ALLOWED_TYPES[detected.mime]) {
    fs.unlinkSync(req.file.path);  // 删除文件
    return res.status(400).json({ error: 'Invalid file content' });
  }
  
  // 4. 病毒扫描（生产环境）
  // await scanFile(req.file.path);
  
  res.json({ fileId: req.file.filename });
});
```

---

## 阶段 4：日志与监控

### 4.1 安全日志
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'security.log' })
  ]
});

// 记录安全事件
function logSecurityEvent(event, details) {
  logger.info({
    event,
    ...details,
    ip: details.ip,
    userAgent: details.userAgent,
    timestamp: new Date().toISOString()
  });
}

// 应用示例
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  
  const user = await authenticateUser(email, password);
  
  if (!user) {
    // 记录失败的登录尝试
    logSecurityEvent('LOGIN_FAILED', {
      email,
      ip: req.ip,
      userAgent: req.headers['user-agent']
    });
    
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  // 记录成功登录
  logSecurityEvent('LOGIN_SUCCESS', {
    userId: user.id,
    email,
    ip: req.ip
  });
  
  res.json({ token: generateToken(user) });
});

// ⚠️ 日志脱敏：永不记录敏感信息
logger.info({
  event: 'USER_CREATED',
  email: 'user@example.com',
  // ❌ password: req.body.password,  // 永不记录密码
  // ❌ creditCard: req.body.card,    // 永不记录信用卡
});
```

### 4.2 异常告警
```javascript
// 检测异常模式
const ALERT_THRESHOLD = {
  FAILED_LOGINS: 10,      // 10 分钟内 10 次失败登录
  RATE_LIMIT: 100,         // 1 分钟内 100 次请求
};

async function checkAnomalies() {
  const failedLogins = await redis.get('failed_logins_count');
  
  if (failedLogins > ALERT_THRESHOLD.FAILED_LOGINS) {
    await sendAlert({
      type: 'BRUTE_FORCE_ATTACK',
      message: `${failedLogins} failed login attempts detected`,
      severity: 'HIGH'
    });
  }
}
```

---

## 安全审计检查清单

### ✅ 认证授权
- [ ] 密码使用 bcrypt (saltRounds >= 12)
- [ ] JWT 签名验证和过期检查
- [ ] Session 配置 HttpOnly + Secure + SameSite
- [ ] 实现账户锁定机制（5 次失败锁定 30 分钟）
- [ ] RBAC 权限控制完整
- [ ] 验证用户对资源的所有权（防止越权）

### ✅ 输入验证
- [ ] 所有用户输入经过验证
- [ ] SQL 使用参数化查询
- [ ] 输出进行 HTML 编码
- [ ] CSP 头部配置
- [ ] 文件上传类型和大小限制

### ✅ 数据保护
- [ ] 敏感数据加密存储（AES-256-GCM）
- [ ] 强制 HTTPS (HSTS 头部)
- [ ] 日志脱敏（无密码、Token、信用卡）
- [ ] Cookie 安全配置

### ✅ 配置安全
- [ ] 安全 HTTP 头部完整（helmet.js）
- [ ] CORS 白名单配置
- [ ] 生产环境禁用调试模式
- [ ] 环境变量管理密钥

### ✅ 依赖安全
- [ ] 定期运行 npm audit / Snyk
- [ ] 及时更新依赖
- [ ] 无已知高危漏洞

---

## 参考资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
