# 如何删除失败的 Workflow Runs

## 方法一：手动删除（推荐）

### 步骤：

1. **访问 Actions 页面**
   ```
   https://github.com/iosxx/github-project-analyzer/actions
   ```

2. **查看所有运行**
   - 点击页面上方的 "All workflows"
   - 或访问：https://github.com/iosxx/github-project-analyzer/actions/runs

3. **筛选失败的运行**
   - 使用下拉菜单筛选：Status → Failure
   - 这会显示所有失败的 workflow runs

4. **删除单个运行**
   - 点击进入要删除的运行详情页
   - 在右上角点击 "..."（更多选项）
   - 选择 "Delete workflow run"
   - 确认删除

5. **批量删除**
   - GitHub 不支持直接批量删除
   - 需要重复步骤 4 对每个失败的运行

## 方法二：使用 GitHub CLI

如果你安装了 GitHub CLI 并有适当的权限：

```bash
# 登录
gh auth login

# 查看失败的 runs
gh run list --repo iosxx/github-project-analyzer --status failure

# 删除特定的 run（需要 run ID）
gh run delete --repo iosxx/github-project-analyzer <run-id>
```

## 方法三：使用 API（需要特殊权限）

```bash
# 注意：这需要 GitHub Enterprise 或特殊权限
# 普通仓库无法通过 API 删除 workflow runs

# 获取失败的 runs
curl -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/iosxx/github-project-analyzer/actions/runs?status=failure"

# 删除日志（不是删除 run）
curl -X DELETE -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/iosxx/github-project-analyzer/actions/runs/<run-id>/logs"
```

## 当前失败的 Workflows

根据最近的运行记录，以下 workflows 失败了：

1. **Deploy to GitHub Pages** (`deploy.yml`)
   - 失败原因：Streamlit 在 GitHub Pages 上无法正常运行
   - 建议：删除这个 workflow，改用 Streamlit Cloud 或 GitHub Codespaces

2. **Analyze GitHub Repo and Publish** (`analyze-and-publish.yml`)
   - 失败原因：缺少 Secrets 配置
   - 建议：配置好 Secrets 后重新运行，手动删除失败的记录

## 如何配置 Secrets 以避免未来失败

1. **设置 API Keys**
   - `OPENAI_API_KEY`: OpenAI 或代理 API 密钥
   - `GROQ_API_KEY`: Groq API 密钥（可选）
   - `PAT_TOKEN`: GitHub Personal Access Token

2. **设置 Token 权限**
   - PAT_TOKEN 需要有 repo 和 workflow 权限
   - 用于推送分析结果到目标 Hugo 仓库

## 推荐操作

1. ✅ 手动删除所有失败的 runs（通过 UI）
2. ✅ 配置所需的 Secrets
3. ✅ 重新触发 workflow 测试
4. ✅ 如果 deploy.yml 不需要，考虑删除该文件

## 辅助脚本

创建了一个简单的脚本来帮助识别失败的 runs：

```bash
#!/bin/bash
# 获取失败的 workflow runs

REPO="iosxx/github-project-analyzer"

echo "🔍 查找失败的 workflow runs..."
echo ""

# 使用 GitHub CLI（如果已安装）
if command -v gh &> /dev/null; then
  echo "使用 GitHub CLI:"
  gh run list --repo "$REPO" --status failure --limit 20
else
  echo "GitHub CLI 未安装，请访问："
  echo "https://github.com/$REPO/actions/runs"
  echo ""
  echo "然后筛选：Status → Failure"
fi
```

保存为 `list-failed-runs.sh`，然后运行：
```bash
bash list-failed-runs.sh
```
