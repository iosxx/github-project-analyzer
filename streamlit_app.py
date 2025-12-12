import streamlit as st
import subprocess
import os
from pathlib import Path

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# Clone and setup the original project
if not st.session_state.initialized:
    with st.spinner('正在初始化项目分析器...'):
        # Clone the reference repository
        if not Path('RepoMetaAgent--Github-Repo-Analyzer').exists():
            subprocess.run([
                'git', 'clone', 
                'https://github.com/shahzaibsalem/RepoMetaAgent--Github-Repo-Analyzer.git'
            ], check=True, capture_output=True)
        
        # Install requirements
        req_file = Path('RepoMetaAgent--Github-Repo-Analyzer/requirements.txt')
        if req_file.exists():
            subprocess.run(['pip', 'install', '-r', str(req_file)], 
                          check=True, capture_output=True)
        
        st.session_state.initialized = True

# Load environment variables
env_vars = {
    "OPENAI_API_KEY": st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "")),
    "GROQ_API_KEY": st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", "")),
}

missing_keys = [k for k, v in env_vars.items() if not v]
if missing_keys:
    st.warning(f"⚠️ 缺少 API 密钥: {', '.join(missing_keys)}")
    st.info("请在 GitHub Secrets 中配置这些密钥，或在本地使用 .env 文件")

# Main UI
st.title("🤖 GitHub 项目分析器")
st.subheader("基于 AI 的仓库分析报告生成工具")

# Repository URL input
repo_url = st.text_input(
    "GitHub 仓库链接",
    placeholder="https://github.com/username/repository",
    help="输入要分析的 GitHub 仓库的完整 URL"
)

# Analysis options
cols = st.columns(3)
with cols[0]:
    generate_summary = st.checkbox("项目概述", value=True)
with cols[1]:
    generate_pros_cons = st.checkbox("优缺点分析", value=True)
with cols[2]:
    generate_deployment = st.checkbox("部署建议", value=True)

if st.button("🔍 开始分析", type="primary"):
    if not repo_url:
        st.error("请输入 GitHub 仓库链接")
    elif not repo_url.startswith("https://github.com/"):
        st.error("请输入有效的 GitHub 仓库链接")
    else:
        with st.spinner("正在分析仓库..."):
            try:
                # Change to the project directory
                os.chdir('RepoMetaAgent--Github-Repo-Analyzer/code')
                
                # Set environment variables
                for key, value in env_vars.items():
                    if value:
                        os.environ[key] = value
                
                # Import and run the analysis
                import sys
                sys.path.append('.')
                
                from __Runner__ import run_assembly_line_analysis
                
                # Run analysis
                results = run_assembly_line_analysis(repo_url)
                
                # Display results
                st.success("✅ 分析完成！")
                
                # Project Summary
                if generate_summary and results.get("long_summary"):
                    st.subheader("📋 项目概述")
                    st.write(results["long_summary"])
                
                # Pros and Cons
                if generate_pros_cons and results.get("review_report"):
                    st.subheader("⚖️ 优缺点分析")
                    st.write(results["review_report"])
                
                # Keywords and Tags
                if results.get("keywords"):
                    st.subheader("🏷️ 关键词")
                    tags = results["keywords"][:10]  # Show top 10
                    tag_html = " ".join([f'<span style="background-color:#f0f0f0;padding:4px 8px;margin:2px;border-radius:4px;display:inline-block;">{tag}</span>' for tag in tags])
                    st.markdown(tag_html, unsafe_allow_html=True)
                
                # File Structure
                if results.get("file_structure"):
                    with st.expander("📁 项目结构"):
                        st.json(results["file_structure"])
                
                # Suggested Title
                if results.get("suggested_title"):
                    st.subheader("💡 建议标题")
                    st.write(results["suggested_title"])
                
                # GitHub Topics
                if results.get("github_topics"):
                    st.subheader("🔖 GitHub 标签")
                    st.write(", ".join(results["github_topics"]))
                
                # Missing Documentation
                if results.get("missing_documentation"):
                    st.subheader("❓ 缺失的文档")
                    for doc in results["missing_documentation"]:
                        st.write(f"- {doc}")
            
            except Exception as e:
                st.error(f"分析过程中出现错误: {str(e)}")
                st.exception(e)
            finally:
                # Change back to original directory
                os.chdir('../../..')

# Sidebar with info
with st.sidebar:
    st.header("关于")
    st.info("""
    这个工具使用 AI 来分析 GitHub 仓库，生成详细的项目分析报告。
    
    **功能特点：**
    - 项目概述生成
    - 优缺点分析  
    - 关键词提取
    - 部署建议
    - 代码质量评估
    
    **技术栈：**
    - Streamlit
    - LangGraph
    - OpenAI/Groq
    """)
    
    st.header("⚡ 快速链接")
    st.markdown("* [获取 OpenAI API](https://platform.openai.com/api-keys)")
    st.markdown("* [获取 Groq API](https://console.groq.com/keys)")
    st.markdown("* [GitHub Project Analyzer](https://github.com/iosxx/github-project-analyzer)")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ | [GitHub Repository](https://github.com/iosxx/github-project-analyzer)")
