#!/usr/bin/env python3
"""
独立的 GitHub 仓库分析脚本
不依赖 RepoMetaAgent，直接使用 GitHub API 和 OpenAI API
"""
import os
import sys
import json
import requests
from datetime import datetime

# GitHub API 配置
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    GITHUB_HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

# OpenAI API 配置
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4-turbo-preview")


def parse_repo_url(url: str) -> tuple:
    """解析 GitHub 仓库 URL"""
    url = url.rstrip("/").replace(".git", "")
    parts = url.split("/")
    owner = parts[-2]
    repo = parts[-1]
    return owner, repo


def fetch_repo_info(owner: str, repo: str) -> dict:
    """获取仓库基本信息"""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=GITHUB_HEADERS)
    response.raise_for_status()
    return response.json()


def fetch_readme(owner: str, repo: str) -> str:
    """获取 README 内容"""
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    response = requests.get(url, headers=GITHUB_HEADERS)
    if response.status_code == 200:
        import base64
        content = response.json().get("content", "")
        try:
            return base64.b64decode(content).decode("utf-8")
        except:
            return ""
    return ""


def fetch_file_tree(owner: str, repo: str, max_depth: int = 3) -> dict:
    """获取文件树结构（限制深度避免速率限制）"""
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    response = requests.get(url, headers=GITHUB_HEADERS)
    if response.status_code != 200:
        return {}
    
    data = response.json()
    tree = {}
    
    for item in data.get("tree", [])[:100]:  # 限制文件数量
        path = item["path"]
        parts = path.split("/")
        if len(parts) <= max_depth:
            tree[path] = item["type"]
    
    return tree


def fetch_languages(owner: str, repo: str) -> dict:
    """获取仓库语言统计"""
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    response = requests.get(url, headers=GITHUB_HEADERS)
    if response.status_code == 200:
        return response.json()
    return {}


def call_openai(prompt: str, system_prompt: str = "", max_tokens: int = 4000) -> str:
    """调用 OpenAI API"""
    if not OPENAI_API_KEY:
        return "未配置 OpenAI API Key"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            f"{OPENAI_API_BASE}/chat/completions",
            headers=headers,
            json=data,
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenAI API 调用失败: {e}")
        return f"AI 分析失败: {str(e)}"


def analyze_repository(repo_url: str) -> dict:
    """分析 GitHub 仓库"""
    print(f"📊 开始分析仓库: {repo_url}")
    print(f"🤖 使用模型: {OPENAI_MODEL}")
    print(f"🔗 API 端点: {OPENAI_API_BASE}")
    
    owner, repo = parse_repo_url(repo_url)
    print(f"📁 仓库: {owner}/{repo}")
    
    # 获取仓库信息
    print("📥 获取仓库信息...")
    try:
        repo_info = fetch_repo_info(owner, repo)
    except Exception as e:
        print(f"❌ 获取仓库信息失败: {e}")
        return generate_fallback_results(repo_url, owner, repo, str(e))
    
    # 获取 README
    print("📄 获取 README...")
    readme = fetch_readme(owner, repo)
    
    # 获取文件结构
    print("📂 获取文件结构...")
    file_tree = fetch_file_tree(owner, repo)
    
    # 获取语言统计
    print("💻 获取语言统计...")
    languages = fetch_languages(owner, repo)
    
    # 准备分析上下文
    context = f"""
仓库名称: {repo_info.get('name', repo)}
描述: {repo_info.get('description', '无描述')}
主要语言: {repo_info.get('language', '未知')}
Star 数: {repo_info.get('stargazers_count', 0)}
Fork 数: {repo_info.get('forks_count', 0)}
主题标签: {', '.join(repo_info.get('topics', []))}
许可证: {repo_info.get('license', {}).get('name', '未知') if repo_info.get('license') else '未知'}

语言统计: {json.dumps(languages, ensure_ascii=False)}

文件结构 (部分):
{json.dumps(list(file_tree.keys())[:50], ensure_ascii=False, indent=2)}

README 内容 (前 3000 字符):
{readme[:3000] if readme else '无 README'}
"""
    
    # AI 分析
    print("🧠 AI 分析中...")
    
    system_prompt = """你是一位资深的开源项目推荐专家，正在为技术周刊撰写项目推荐文章。
你的文章风格：
- 热情洋溢但不失专业
- 深入浅出，让读者快速理解项目价值
- 结合实际使用场景，给出具体的推荐理由
- 内容详实丰富，每个部分都要有足够的信息量
请用中文撰写，语言生动有趣。"""
    
    analysis_prompt = f"""请为以下 GitHub 项目撰写一篇详细的周刊推荐文章：

{context}

请按以下格式撰写（每个部分用 ### 标题分隔，内容要详细丰富）：

### 项目亮点
（用 3-5 句话概括这个项目最吸引人的地方，为什么值得推荐，要有感染力）

### 项目简介
（400-600字的详细介绍，包括项目背景、解决的问题、核心理念等）

### 核心功能
（详细介绍 5-8 个主要功能，每个功能用 **功能名**：描述 的格式，描述要具体）

### 技术架构
（详细分析技术栈选型、架构设计、代码组织等，300-400字）

### 快速上手
（提供详细的安装和使用步骤，包括命令示例）

### 使用场景
（列出 3-5 个具体的使用场景，说明什么样的人/团队适合使用）

### 优势分析
（详细分析 5 个以上的优点，每个优点要有具体说明）

### 待改进
（客观指出 2-3 个可以改进的地方）

### 同类对比
（如果有类似项目，简要对比优劣）

### 推荐理由
（总结为什么推荐这个项目，适合什么读者，100-150字）
"""
    
    ai_response = call_openai(analysis_prompt, system_prompt)
    
    # 解析 AI 响应
    sections = parse_ai_response(ai_response)
    
    # 提取关键词
    topics = repo_info.get('topics', [])
    if not topics:
        topics = list(languages.keys())[:5] if languages else []
    
    # 构建结果
    results = {
        "highlight": sections.get("项目亮点", ""),
        "long_summary": sections.get("项目简介", repo_info.get('description', '暂无描述')),
        "core_features": sections.get("核心功能", ""),
        "tech_architecture": sections.get("技术架构", ""),
        "quick_start": sections.get("快速上手", ""),
        "use_cases": sections.get("使用场景", ""),
        "advantages": sections.get("优势分析", ""),
        "improvements": sections.get("待改进", ""),
        "comparison": sections.get("同类对比", ""),
        "recommendation": sections.get("推荐理由", ""),
        "short_summary": sections.get("项目亮点", repo_info.get('description', '')),
        "review_report": f"## 优势分析\n\n{sections.get('优势分析', '')}\n\n## 待改进\n\n{sections.get('待改进', '')}",
        "keywords": topics + list(languages.keys())[:5],
        "github_topics": topics if topics else list(languages.keys())[:5],
        "file_structure": file_tree,
        "missing_documentation": extract_missing_docs(sections.get("待改进", "")),
        "suggested_title": f"本周推荐：{repo} - {repo_info.get('description', '值得关注的开源项目')[:50]}",
        "tech_analysis": sections.get("技术架构", ""),
        "repo_info": {
            "name": repo_info.get('name'),
            "full_name": repo_info.get('full_name'),
            "description": repo_info.get('description'),
            "stars": repo_info.get('stargazers_count'),
            "forks": repo_info.get('forks_count'),
            "language": repo_info.get('language'),
            "topics": topics,
            "license": repo_info.get('license', {}).get('name') if repo_info.get('license') else None,
            "html_url": f"https://github.com/{owner}/{repo}",
            "created_at": repo_info.get('created_at'),
            "updated_at": repo_info.get('updated_at'),
            "open_issues": repo_info.get('open_issues_count'),
            "watchers": repo_info.get('watchers_count')
        }
    }
    
    print("✅ 分析完成！")
    return results


def parse_ai_response(response: str) -> dict:
    """解析 AI 响应为各个部分"""
    sections = {}
    current_section = None
    current_content = []
    
    for line in response.split('\n'):
        if line.startswith('### '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[4:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def extract_missing_docs(text: str) -> list:
    """从改进建议中提取缺失文档"""
    docs = []
    keywords = ['文档', '说明', 'README', 'API', '示例', '教程', '注释']
    for keyword in keywords:
        if keyword.lower() in text.lower():
            docs.append(f"完善{keyword}")
    return docs if docs else ["暂无明显缺失"]


def generate_fallback_results(repo_url: str, owner: str, repo: str, error: str) -> dict:
    """生成备用结果（当获取仓库信息失败时）"""
    return {
        "long_summary": f"无法获取仓库 {owner}/{repo} 的详细信息。错误: {error}",
        "short_summary": f"{repo} 是一个 GitHub 项目",
        "review_report": "由于 API 限制，无法完成完整分析",
        "keywords": [repo, owner, "github"],
        "github_topics": [],
        "file_structure": {},
        "missing_documentation": ["需要手动查看项目"],
        "suggested_title": f"探索 {repo} 项目"
    }


def main():
    repo_url = os.environ.get("REPO_URL", "")
    if not repo_url:
        print("错误: 未提供 REPO_URL")
        sys.exit(1)
    
    # 运行分析
    results = analyze_repository(repo_url)
    
    # 保存结果
    with open("/tmp/analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存元数据
    meta = {
        "repo_url": repo_url,
        "analyzed_at": datetime.now().isoformat(),
        "title": os.environ.get("ARTICLE_TITLE", ""),
        "openai_model": OPENAI_MODEL,
        "openai_api_base": OPENAI_API_BASE
    }
    with open("/tmp/analysis_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"📁 结果已保存到 /tmp/analysis_results.json")


if __name__ == "__main__":
    main()
