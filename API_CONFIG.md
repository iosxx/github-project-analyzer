# API 配置指南

## 支持的 API 服务

### 1. OpenAI 官方 API
- **API Base**: `https://api.openai.com/v1`
- **模型**:
  - `gpt-4-turbo-preview` (推荐)
  - `gpt-3.5-turbo`
  - `gpt-4`
  - `gpt-4-32k`
- **获取**: https://platform.openai.com/api-keys

### 2. Groq (免费)
- **特点**: 提供免费额度，速度快，性价比高
- **获取**: https://console.groq.com/keys
- **模型**:
  - `mixtral-8x7b-32768`
  - `llama3-70b-8192`
  - `llama3-8b-8192`

### 3. 第三方 API 代理
- **示例**: `https://api.agentify.top/v1`
- **特点**: 可能更便宜或有特殊优惠
- **示例模型**: `gpt-oss-120b`
- **配置**: 需要设置自定义 API base 和对应的 API key

## 配置方法

### GitHub Secrets 配置

前往 Settings > Secrets and variables > Actions，添加以下 secrets:

```bash
# AI API 密钥（至少配置一个）
OPENAI_API_KEY=sk-...        # OpenAI API 密钥或其他代理的密钥
GROQ_API_KEY=gsk_...         # Groq API 密钥（可选）

# GitHub 访问令牌（必需）
PAT_TOKEN=ghp_...            # Personal Access Token
```

### Workflow 输入参数

手动运行 workflow 时可配置：

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `repo_url` | 要分析的仓库 URL | 必填 | `https://github.com/user/repo` |
| `openai_model` | 模型选择 | gpt-4-turbo-preview | gpt-3.5-turbo, gpt-4, gpt-oss-120b |
| `openai_api_base` | 自定义 API 端点 | https://api.openai.com/v1 | https://api.agentify.top/v1 |
| `title` | 文章标题 | 自动生成 | 项目分析报告 |

## 使用第三方 API 代理

### 示例：使用 agentify

1. **配置 Secrets**:
   ```bash
   OPENAI_API_KEY=your-agentify-key
   GROQ_API_KEY=your-groq-key
   PAT_TOKEN=ghp-your-github-token
   ```

2. **运行 Workflow**:
   - 触发 workflow 时选择：
     - `openai_api_base`: `https://api.agentify.top/v1`
     - `openai_model`: `gpt-oss-120b` 或其他支持的模型

3. **支持的模型**:
   根据代理服务的支持情况选择，例如：
   - `gpt-oss-120b`
   - `gpt-4-turbo`
   - `gpt-3.5-turbo`

### 注意事项

使用第三方 API 代理时：
1. 确认代理服务支持您选择的模型
2. 了解代理的速率限制和使用条款
3. 注意数据隐私和安全性
4. 某些高级功能可能不支持

## 本地开发配置

创建 `.env` 文件：

```bash
# API 密钥
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
GITHUB_TOKEN=ghp_...

# 自定义 API 配置（可选）
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# 如果要使用第三方代理
# OPENAI_API_BASE=https://api.agentify.top/v1
# OPENAI_MODEL=gpt-oss-120b
```

## 故障排除

### API 连接失败

**症状**: Workflow 运行失败，提示 API 连接错误

**解决方案**:
1. 检查 API key 是否正确
2. 确认 API base URL 格式正确（以 `/v1` 结尾）
3. 验证网络连接和代理设置
4. 检查 API 服务状态

### 模型不支持

**症状**: 错误提示模型不存在或不支持

**解决方案**:
1. 确认代理服务支持该模型
2. 联系代理服务提供商获取支持的模型列表
3. 尝试使用通用模型如 `gpt-3.5-turbo`

### 速率限制

**症状**: API 返回 429 错误

**解决方案**:
1. 等待速率限制重置
2. 考虑升级 API 套餐
3. 优化请求频率
4. 使用多个 API key 轮换

## 成本参考

| 服务 | 费用 | 适用场景 |
|------|------|----------|
| OpenAI 官方 | 按 token 计费 | 高质量分析 |
| Groq | 免费额度 | 日常使用 |
| 第三方代理 | 视服务商而定 | 成本优化 |

## 安全性建议

1. **不要在日志中暴露 API key**
2. **定期轮换 API key**
3. **为不同环境使用不同的 key**
4. **设置 API 使用限制和预算警报**
5. **监控异常 API 调用**

## 获取帮助

- GitHub Issues: https://github.com/iosxx/github-project-analyzer/issues
- 项目主页: https://github.com/iosxx/github-project-analyzer
