## Git 提交规范

**格式**：`<type>(<scope>): <subject>`

**类型**：feat（新功能）、fix（修复）、refactor（重构）、docs（文档）、style（格式）、test（测试）、chore（构建）

**规则**：
- **必须使用标准英文**（不使用中文或拼音）
- 动词开头、小写、≤50 字符、无句号
- Body 可选（≤72 字符/行）
- Footer 标注 BREAKING CHANGE
- **禁止添加** "Generated with Claude Code" 签名

**示例**：
```
feat(auth): add JWT authentication
fix(api): resolve user creation validation error
refactor(database): optimize query performance
docs(readme): update installation instructions
```

## 时间管理

调用：`current_time({format: "YYYY-MM-DD HH:mm:ss", timezone: "Asia/Shanghai"})`

## 开发指导

**自动选择合适的 Skill**：根据任务需求，主动调用对应的 skill 进行开发工作。

### Skill 选择决策树

根据任务类型选择对应的 skill：

- **新项目开发 / 全栈开发** → developer skill
- **后端开发 / API** → backend skill
- **前端开发 / UI / 性能优化** → frontend skill
- **移动应用开发** → mobile skill
- **数据库设计 / 优化 / 迁移** → database-engineer skill
- **API 设计** → api-designer skill
- **UI/UX 设计** → designer skill
- **测试工程** → test-engineer skill
- **安全审计** → security-auditor skill
- **性能优化** → performance-optimizer skill
- **DevOps / 部署** → devops-engineer skill
- **MCP 工具开发** → mcp-builder skill
- **Artifacts 应用开发** → artifacts-builder skill
- **代码审查** → code-reviewer skill
- **产品管理** → product-manager skill

### 使用流程

1. 分析任务类型，选择对应的 skill
2. 查看 skill 的 SKILL.md 了解能力范围
3. 使用 scripts/ 中的辅助脚本（先运行 --help）
4. 参考 references/ 中的详细文档
5. 按照 skill 规范执行开发

## 设计规范

禁止使用渐变色，优先设计符合当前项目应用的主题色彩或者符合当前UI组件库，若未指定则参考shadcn官网等优秀网站
