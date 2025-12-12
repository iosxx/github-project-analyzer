#!/usr/bin/env python3
"""
Generate Hugo-compatible markdown from analysis results.
"""
import json
import sys
import os

def generate_deployment_tutorial(topics, file_struct, repo_url, repo_name):
    """Generate deployment tutorial based on detected tech stack."""
    tutorial = []
    topics_lower = [t.lower() for t in topics] if topics else []
    file_struct_str = str(file_struct).lower()
    
    # Detect project type
    is_python = 'python' in topics_lower or 'requirements.txt' in file_struct_str or 'setup.py' in file_struct_str
    is_node = 'javascript' in topics_lower or 'nodejs' in topics_lower or 'package.json' in file_struct_str
    is_docker = 'docker' in topics_lower or 'dockerfile' in file_struct_str or 'docker-compose' in file_struct_str
    is_go = 'go' in topics_lower or 'golang' in topics_lower or 'go.mod' in file_struct_str
    is_rust = 'rust' in topics_lower or 'cargo.toml' in file_struct_str
    is_java = 'java' in topics_lower or 'pom.xml' in file_struct_str or 'build.gradle' in file_struct_str
    
    tutorial.append('### 环境准备\n')
    tutorial.append('在开始之前，请确保您的系统已安装以下工具：\n')
    
    if is_python:
        tutorial.append('- Python 3.8+ ([下载地址](https://www.python.org/downloads/))')
        tutorial.append('- pip (Python 包管理器)')
    if is_node:
        tutorial.append('- Node.js 16+ ([下载地址](https://nodejs.org/))')
        tutorial.append('- npm 或 yarn 包管理器')
    if is_docker:
        tutorial.append('- Docker ([下载地址](https://www.docker.com/get-started))')
        tutorial.append('- Docker Compose (可选)')
    if is_go:
        tutorial.append('- Go 1.19+ ([下载地址](https://go.dev/dl/))')
    if is_rust:
        tutorial.append('- Rust ([安装指南](https://www.rust-lang.org/tools/install))')
    if is_java:
        tutorial.append('- JDK 11+ ([下载地址](https://adoptium.net/))')
        tutorial.append('- Maven 或 Gradle')
    
    tutorial.append('- Git\n')
    
    tutorial.append('### 快速开始\n')
    tutorial.append('#### 1. 克隆仓库\n')
    tutorial.append(f'```bash\ngit clone {repo_url}\ncd {repo_name}\n```\n')
    
    if is_python:
        tutorial.append('#### 2. 创建虚拟环境（推荐）\n')
        tutorial.append('```bash\npython -m venv venv\n# Windows\nvenv\\Scripts\\activate\n# Linux/Mac\nsource venv/bin/activate\n```\n')
        tutorial.append('#### 3. 安装依赖\n')
        tutorial.append('```bash\npip install -r requirements.txt\n```\n')
        tutorial.append('#### 4. 运行项目\n')
        tutorial.append('```bash\n# 根据项目类型选择运行方式\npython main.py  # 或 python app.py\n```\n')
    
    if is_node:
        tutorial.append('#### 2. 安装依赖\n')
        tutorial.append('```bash\nnpm install\n# 或使用 yarn\nyarn install\n```\n')
        tutorial.append('#### 3. 运行项目\n')
        tutorial.append('```bash\nnpm start\n# 或开发模式\nnpm run dev\n```\n')
    
    if is_docker:
        tutorial.append('#### Docker 部署方式\n')
        tutorial.append(f'```bash\n# 构建镜像\ndocker build -t {repo_name} .\n\n# 运行容器\ndocker run -p 8080:8080 {repo_name}\n```\n')
        if 'docker-compose' in file_struct_str:
            tutorial.append('#### 使用 Docker Compose\n')
            tutorial.append('```bash\ndocker-compose up -d\n```\n')
    
    if is_go:
        tutorial.append('#### 2. 下载依赖\n')
        tutorial.append('```bash\ngo mod download\n```\n')
        tutorial.append('#### 3. 编译运行\n')
        tutorial.append('```bash\ngo build -o app\n./app\n```\n')
    
    if is_rust:
        tutorial.append('#### 2. 编译运行\n')
        tutorial.append(f'```bash\ncargo build --release\n./target/release/{repo_name}\n```\n')
    
    if is_java:
        tutorial.append('#### 2. 编译项目\n')
        if 'pom.xml' in file_struct_str:
            tutorial.append('```bash\nmvn clean install\nmvn spring-boot:run  # 如果是 Spring Boot 项目\n```\n')
        else:
            tutorial.append('```bash\ngradle build\ngradle bootRun  # 如果是 Spring Boot 项目\n```\n')
    
    tutorial.append('### 配置说明\n')
    tutorial.append('1. 检查项目中的 `.env.example` 或 `config.example` 文件\n')
    tutorial.append('2. 复制示例配置并修改为您的实际配置\n')
    tutorial.append('3. 确保所有必需的环境变量已正确设置\n')
    
    tutorial.append('### 常见问题\n')
    tutorial.append('- **依赖安装失败**：检查网络连接，尝试使用镜像源\n')
    tutorial.append('- **端口被占用**：修改配置文件中的端口号\n')
    tutorial.append('- **权限问题**：确保有足够的文件读写权限\n')
    
    return '\n'.join(tutorial)


def main():
    # Read analysis results
    with open('analysis_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    with open('analysis_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    # Generate markdown content
    repo_url = meta['repo_url']
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    owner = repo_url.split('/')[-2] if len(repo_url.split('/')) > 1 else 'unknown'
    analyzed_date = meta['analyzed_at'][:10]
    title = meta.get('title') or f'项目分析：{repo_name}'
    model = meta.get('openai_model', 'unknown')
    api_base = meta.get('openai_api_base', 'https://api.openai.com/v1')
    
    # Create valid filename
    filename = f'{analyzed_date}-{repo_name}-analysis.md'
    
    # Format tags properly for Hugo
    keywords = results.get('keywords', [])
    tags_list = keywords[:5] if keywords else ['项目分析']
    tags_str = json.dumps(tags_list, ensure_ascii=False)
    
    # Get file structure summary
    file_structure = results.get('file_structure', {})
    file_structure_str = json.dumps(file_structure, ensure_ascii=False, indent=2)
    if len(file_structure_str) > 2000:
        file_structure_str = file_structure_str[:2000] + '\n... (结构过长已截断)'
    
    # Format missing documentation
    missing_docs = results.get('missing_documentation', [])
    if isinstance(missing_docs, list):
        missing_docs_str = '\n'.join([f'- {doc}' for doc in missing_docs]) if missing_docs else '暂无缺失文档信息'
    else:
        missing_docs_str = str(missing_docs)
    
    # Get tech stack
    github_topics = results.get('github_topics', [])
    tech_stack = ', '.join(github_topics) if github_topics else '未识别'
    
    # Generate deployment tutorial
    deployment_tutorial = generate_deployment_tutorial(github_topics, file_structure, repo_url, repo_name)
    
    # Generate Hugo markdown
    markdown = f'''---
title: "{title}"
date: {analyzed_date}
categories:
  - "项目分析"
tags: {tags_str}
draft: false
slug: "{repo_name}-analysis"
description: "GitHub 项目 {repo_name} 的 AI 分析报告，包含项目概述、技术栈分析、优缺点评价和搭建教程"
---

## 基本信息

| 属性 | 值 |
|------|----|
| 仓库地址 | [{repo_url}]({repo_url}) |
| 仓库所有者 | {owner} |
| 项目名称 | {repo_name} |
| 分析时间 | {analyzed_date} |
| AI 模型 | {model} |

## 项目概述

{results.get('long_summary', '暂无项目概述')}

## 核心功能

{results.get('short_summary', '暂无功能描述')}

## 技术栈

**主要技术**：{tech_stack}

**关键词**：{', '.join(keywords[:10]) if keywords else '未提取'}

## 项目结构

<details>
<summary>点击展开项目结构</summary>

```json
{file_structure_str}
```

</details>

## 优缺点分析

{results.get('review_report', '暂无分析结果')}

## 待改进项

{missing_docs_str}

## 搭建教程

{deployment_tutorial}

## 推荐用途

{results.get('suggested_title', '请参考项目 README 了解具体用途')}

## 许可证

请查看项目仓库中的 LICENSE 文件了解详细信息。

---

> 📝 **声明**：本分析由 AI（{model}）自动生成，仅供参考。建议结合项目官方文档进行验证。
>
> 🔗 **生成工具**：[GitHub Project Analyzer](https://github.com/iosxx/github-project-analyzer)
'''
    
    with open('analysis.md', 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    with open('filename.txt', 'w') as f:
        f.write(filename)
    
    print(f'Generated markdown file: {filename}')


if __name__ == '__main__':
    main()
