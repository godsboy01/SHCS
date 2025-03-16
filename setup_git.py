import os
import subprocess
import sys

def run_command(command):
    """运行命令并打印输出"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(f"执行命令: {command}")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: 执行命令 {command} 失败")
        print(f"错误信息: {e.stderr}")
        return False

def setup_git():
    """设置 Git 环境"""
    print("开始设置 Git 环境...")
    
    # 检查 Git 是否已安装
    if not run_command("git --version"):
        print("请先安装 Git: https://git-scm.com/downloads")
        return False
    
    # 配置用户信息
    name = input("请输入您的名字: ")
    email = input("请输入您的邮箱: ")
    
    commands = [
        f'git config --global user.name "{name}"',
        f'git config --global user.email "{email}"',
        'git config --global core.autocrlf true',  # Windows 换行符设置
        'git config --global init.defaultBranch main',  # 默认分支名设置
    ]
    
    # 执行 Git 配置命令
    for command in commands:
        if not run_command(command):
            return False
    
    # 初始化 Git 仓库
    if not run_command("git init"):
        return False
    
    # 创建首次提交
    commands = [
        "git add .",
        'git commit -m "初始化提交：添加基础项目结构"'
    ]
    
    for command in commands:
        if not run_command(command):
            return False
    
    print("\nGit 环境设置完成！")
    print("\n下一步操作建议：")
    print("1. 在 GitHub/GitLab 创建远程仓库")
    print("2. 运行以下命令添加远程仓库：")
    print("   git remote add origin <repository_url>")
    print("3. 推送代码到远程仓库：")
    print("   git push -u origin main")
    
    return True

if __name__ == "__main__":
    setup_git() 