#!/bin/zsh
# 一键提交并推送到 GitHub

# 进入脚本所在目录
cd "$(dirname "$0")" || exit 1

# 显示当前状态
echo "===== 当前修改文件 ====="
git status -s

# 添加所有修改
git add .

# 获取提交信息
echo "\n请输入提交信息（直接回车将使用默认信息）："
read "commit_msg?提交信息: "

# 如果没输入，用默认信息
if [[ -z "$commit_msg" ]]; then
    commit_msg="更新代码 $(date '+%Y-%m-%d %H:%M')"
fi

# 提交
git commit -m "$commit_msg"

# 推送到 main 分支
echo "\n正在推送到 GitHub..."
git push origin main

echo "\n✅ 推送完成！"
