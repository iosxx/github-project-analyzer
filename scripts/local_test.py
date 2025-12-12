#!/usr/bin/env python3
"""
本地测试脚本 - 模拟 GitHub Actions 的分析流程
"""
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

def clone_repo_meta_agent():
    """克隆 RepoMetaAgent 项目"""
    repo_path = PROJECT_ROOT / "RepoMetaAgent--Github-Repo-Analyzer"
    if not repo_path.exists():
        print("📦 正在克隆 RepoMetaAgent 项目...")
        subprocess.run([
            "git", "clone",
            "https://github.com/shahzaibsalem/RepoMetaAgent--Github-Repo-Analyzer.git"
        ], check=True)
        print("✅ 克隆完成")
    else:
        print("✅ RepoMetaAgent 已存在")
    return repo_path

def install_dependencies(repo_path):
    """安装 RepoMetaAgent 的依赖"""
    req_file = repo_path / "requirements.txt"
    if req_file.exists():
        print("📦 正在安装 RepoMetaAgent 依赖...")
        subprocess.run(["pip", "install", "-r", str(req_file)], 
                      capture_output=True)
        print("✅ 依赖安装完成")

def run_analysis(repo_url: str):
    """运行仓库分析"""
    print(f"\n🔍 开始分析仓库: {repo_url}")
    
    # 检查 API 密钥
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    
    if not openai_key and not groq_key:
        print("⚠️  未配置 API 密钥，将使用模拟数据进行测试")
        return generate_mock_results(repo_url)
    
    # 尝试运行真实分析
    try:
        repo_path = clone_repo_meta_agent()
        install_dependencies(repo_path)
        
        sys.path.insert(0, str(repo_path / "code"))
        os.chdir(repo_path / "code")
        
        from __Runner__ import run_assembly_line_analysis
        results = run_assembly_line_analysis(repo_url)
        
        os.chdir(PROJECT_ROOT)
        return results
        
    except Exception as e:
        print(f"⚠️  分析失败: {e}")
        print("📝 使用模拟数据继续测试...")
        os.chdir(PROJECT_ROOT)
        return generate_mock_results(repo_url)

def generate_mock_results(repo_url: str):
    """生成模拟分析结果用于测试"""
    repo_name = repo_url.rstrip('/').split('/')[-1]
    
    return {
        "long_summary": f"""这是一个 GitHub 项目分析的模拟结果。

{repo_name} 是一个开源项目，包含了完整的代码实现和文档。该项目采用现代化的开发实践，具有良好的代码结构和可维护性。

主要特点：
- 清晰的项目结构
- 完善的文档说明
- 活跃的社区支持""",
        
        "short_summary": f"{repo_name} 是一个功能完善的开源项目，提供了便捷的开发体验。",
        
        "keywords": ["开源", "GitHub", "项目分析", "自动化", "Python"],
        
        "github_topics": ["python", "automation", "github", "analysis"],
        
        "file_structure": {
            "README.md": "项目说明",
            "requirements.txt": "Python 依赖",
            "src/": "源代码目录",
            "tests/": "测试代码"
        },
        
        "review_report": """### 优点

1. **代码结构清晰**：项目采用模块化设计，易于理解和维护
2. **文档完善**：README 详细说明了项目用途和使用方法
3. **测试覆盖**：包含单元测试，保证代码质量

### 需要改进

1. 可以添加更多的使用示例
2. 建议增加 CI/CD 配置
3. 可以考虑添加 Docker 支持""",
        
        "missing_documentation": [
            "API 文档",
            "贡献指南",
            "更新日志"
        ],
        
        "suggested_title": f"推荐使用 {repo_name} 来提升开发效率"
    }

def generate_hugo_markdown(results: dict, repo_url: str):
    """生成 Hugo 格式的 Markdown"""
    # 保存分析结果
    with open("analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存元数据
    meta = {
        "repo_url": repo_url,
        "analyzed_at": datetime.now().isoformat(),
        "title": "",
        "openai_model": "local-test",
        "openai_api_base": "local"
    }
    with open("analysis_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    # 运行 Hugo Markdown 生成脚本
    print("\n📝 生成 Hugo Markdown...")
    subprocess.run([sys.executable, "scripts/generate_hugo_markdown.py"], check=True)
    
    # 读取生成的文件
    with open("analysis.md", "r", encoding="utf-8") as f:
        markdown = f.read()
    
    with open("filename.txt", "r", encoding="utf-8") as f:
        filename = f.read().strip()
    
    return markdown, filename

def main():
    print("=" * 60)
    print("🤖 GitHub 项目分析器 - 本地测试")
    print("=" * 60)
    
    # 获取要分析的仓库 URL
    if len(sys.argv) > 1:
        repo_url = sys.argv[1]
    else:
        repo_url = input("\n请输入要分析的 GitHub 仓库链接: ").strip()
    
    if not repo_url:
        repo_url = "https://github.com/microsoft/vscode"
        print(f"使用默认仓库: {repo_url}")
    
    if not repo_url.startswith("https://github.com/"):
        print("❌ 请输入有效的 GitHub 仓库链接")
        return
    
    # 运行分析
    results = run_analysis(repo_url)
    
    # 生成 Hugo Markdown
    markdown, filename = generate_hugo_markdown(results, repo_url)
    
    # 输出结果
    print("\n" + "=" * 60)
    print(f"✅ 分析完成！")
    print(f"📄 生成的文件: {filename}")
    print("=" * 60)
    
    print("\n📋 Markdown 预览 (前 50 行):")
    print("-" * 40)
    lines = markdown.split('\n')[:50]
    print('\n'.join(lines))
    print("-" * 40)
    print(f"... (共 {len(markdown.split(chr(10)))} 行)")
    
    print(f"\n📁 完整文件已保存到: {PROJECT_ROOT / 'analysis.md'}")

if __name__ == "__main__":
    main()
