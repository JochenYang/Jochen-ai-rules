#全局规范

AI 助手应该在每次代码编辑后立即调用 `record_context` 工具，确保所有变更都被正确记录到项目记忆中。

## Git 提交规范

**格式**：`<type>(<scope>): <subject>`

**类型**：feat（新功能）、fix（修复）、refactor（重构）、docs（文档）、style（格式）、test（测试）、chore（构建）

**规则**：动词开头、小写、≤50 字符、无句号；Body 可选（≤72 字符/行）；Footer 标注 BREAKING CHANGE

## 时间管理

调用：`current_time({format: "YYYY-MM-DD HH:mm:ss", timezone: "Asia/Shanghai"})`

## 开发指导

根据当前任务需求，使用合适的skill进行编码工作，提交git commit时不要添加“🤖 Generated with [Claude Code](https://claude.com/claude-code)”

## 设计规范

禁止使用渐变色，优先设计符合当前项目应用的主题色彩或者符合当前UI组件库，若未指定则参考shadcn官网等优秀网站