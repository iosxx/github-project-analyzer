# GitHub 项目分析器 🤖

AI 驱动的 GitHub 项目分析工具，能够自动分析仓库并生成详细的项目报告和 **Hugo 格式的 Markdown 文件**。

## ✨ 功能特性

- 📊 **项目分析**：自动分析 GitHub 项目的结构、技术栈和代码质量
- 📝 **智能报告生成**：使用 AI 生成项目概述、优缺点分析
- 🛠️ **搭建教程生成**：根据技术栈自动生成项目部署教程
- 📄 **Hugo MD 输出**：生成符合 Hugo 格式的 Markdown 文件，可直接用于博客发布
- 🔍 **关键词提取**：自动提取项目相关的关键词和标签
- 🧠 **多 AI 模型支持**：支持 OpenAI GPT 和 Groq 等多种 AI 模型

## 🚀 快速开始（GitHub Actions）

这是**推荐的使用方式**，无需本地环境，在 GitHub 上直接运行。

### 步骤 1：Fork 本仓库

点击右上角 Fork 按钮，将项目复制到你的账户

### 步骤 2：配置 Secrets

前往仓库的 **Settings > Secrets and variables > Actions**，添加以下密钥：

| Secret 名称 | 说明 | 必需 |
|------------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | ✅ 是（或使用 GROQ） |
| `GROQ_API_KEY` | Groq API 密钥（免费） | 可选 |
| `PAT_TOKEN` | GitHub Personal Access Token（用于推送到其他仓库） | 如需发布则必需 |

### 步骤 3：运行 Workflow

1. 前往 **Actions** 标签页
2. 选择 **"Analyze GitHub Repo and Publish"** workflow
3. 点击 **"Run workflow"**
4. 填写参数：
   - `repo_url`：要分析的 GitHub 仓库 URL
   - `title`：文章标题（可选）
   - `openai_model`：使用的 AI 模型
   - `hugo_deploy_repo`：目标 Hugo 仓库（如 `username/blog`）
   - `content_path`：内容保存路径（如 `content/posts`）
   - `publish`：是否自动推送到 Hugo 仓库

### 步骤 4：查看结果

- Workflow 完成后，可在 **Artifacts** 中下载分析结果
- 如果启用了发布，Markdown 文件会自动推送到指定的 Hugo 仓库

## 📁 生成的 Hugo Markdown 格式

```yaml
---
title: "项目分析：example-repo"
date: 2024-01-01
categories:
  - "项目分析"
tags: ["python", "ai", "automation"]
draft: false
slug: "example-repo-analysis"
description: "GitHub 项目分析报告..."
---

## 基本信息
...

## 项目概述
...

## 搭建教程
### 环境准备
### 快速开始
...
```

## 🖥️ 本地运行

```bash
# 克隆仓库
git clone https://github.com/iosxx/github-project-analyzer.git
cd github-project-analyzer

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加 API 密钥

# 运行 Streamlit 应用
streamlit run streamlit_app.py
```

## 🔧 技术栈

- **前端**：Streamlit
- **AI 框架**：LangGraph、LangChain
- **AI 模型**：OpenAI GPT、Groq
- **版本控制**：GitPython
- **配置管理**：PyYAML

## 📂 项目结构

```
.
├── .github/workflows/
│   └── analyze-and-publish.yml  # GitHub Actions 主工作流
├── scripts/
│   └── generate_hugo_markdown.py # Hugo MD 生成脚本
├── streamlit_app.py              # Streamlit 前端应用
├── requirements.txt              # Python 依赖
├── .env.example                  # 环境变量示例
├── API_CONFIG.md                 # API 配置指南
└── README.md                     # 项目说明
```

## ⚠️ 注意事项

### AI 模型限制
- 分析大型仓库可能会受到 token 限制
- 某些私有仓库可能需要额外的访问权限
- API 调用会产生费用，请注意使用频率

### 安全性
- 不要在代码中硬编码 API 密钥
- 使用 GitHub Secrets 安全存储敏感信息
- 定期轮换 API 密钥

### 免费方案
- 使用 **Groq API**（免费额度）进行分析
- 使用 GitHub Actions 免费额度运行

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests！

## 📄 许可证

MIT License

## 🔗 相关链接

- [获取 OpenAI API](https://platform.openai.com/api-keys)
- [获取 Groq API（免费）](https://console.groq.com/keys)
- [API 配置指南](./API_CONFIG.md)
