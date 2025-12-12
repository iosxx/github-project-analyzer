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


def call_openai(prompt: str, system_prompt: str = "") -> str:
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
        "max_tokens": 2000
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
    
    system_prompt = """你是一个专业的 GitHub 项目分析师。请根据提供的仓库信息，生成详细的项目分析报告。
请用中文回答，分析要客观、专业、有深度。"""
    
    analysis_prompt = f"""请分析以下 GitHub 仓库并提供详细报告：

{context}

请按以下格式提供分析（每个部分用 ### 标题分隔）：

### 项目概述
（200-300字的项目介绍）

### 核心功能
（列出 3-5 个主要功能）

### 技术特点
（分析技术栈和架构特点）

### 优点
（列出 3-5 个优点）

### 不足与改进建议
（列出 2-3 个可改进的地方）

### 适用场景
（说明项目适合的使用场景）
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
        "long_summary": sections.get("项目概述", repo_info.get('description', '暂无描述')),
        "short_summary": sections.get("核心功能", "请查看项目 README"),
        "review_report": f"{sections.get('优点', '')}\n\n{sections.get('不足与改进建议', '')}",
        "keywords": topics + list(languages.keys())[:5],
        "github_topics": topics if topics else list(languages.keys())[:5],
        "file_structure": file_tree,
        "missing_documentation": extract_missing_docs(sections.get("不足与改进建议", "")),
        "suggested_title": sections.get("适用场景", f"使用 {repo} 提升开发效率"),
        "tech_analysis": sections.get("技术特点", ""),
        "repo_info": {
            "name": repo_info.get('name'),
            "full_name": repo_info.get('full_name'),
            "description": repo_info.get('description'),
            "stars": repo_info.get('stargazers_count'),
            "forks": repo_info.get('forks_count'),
            "language": repo_info.get('language'),
            "topics": topics,
            "license": repo_info.get('license', {}).get('name') if repo_info.get('license') else None
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
