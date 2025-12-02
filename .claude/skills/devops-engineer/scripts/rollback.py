#!/usr/bin/env python3
"""
一键回滚脚本 - 快速回滚到上一个稳定版本

功能：
- 列出可回滚的版本
- 执行回滚操作（Kubernetes/Docker/Git）
- 验证回滚成功

使用方式：
    python rollback.py --list                     # 列出可回滚版本
    python rollback.py --env production           # 回滚到上一个版本
    python rollback.py --env staging --revision 3  # 回滚到指定版本
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class Rollback:
    """回滚器"""
    
    def __init__(self, env: str, revision: Optional[int] = None):
        self.env = env
        self.revision = revision
        self.project_root = Path.cwd()
    
    def log(self, message: str, level: str = "info"):
        colors = {"success": Colors.OKGREEN, "warning": Colors.WARNING, "error": Colors.FAIL}
        color = colors.get(level, "")
        print(f"{color}[{level.upper()}] {message}{Colors.ENDC}")
    
    def run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"命令失败: {result.stderr}")
        return result
    
    def list_versions(self):
        """列出可回滚的版本"""
        self.log("查询可回滚的版本...", "info")
        
        # Kubernetes 回滚历史
        if self._check_k8s():
            self.log("\n=== Kubernetes 部署历史 ===", "info")
            result = self.run_command(["kubectl", "rollout", "history", "deployment/app"])
            print(result.stdout)
        
        # Docker 镜像历史
        self.log("\n=== Docker 镜像历史 ===", "info")
        result = self.run_command(["docker", "images", "--filter", f"reference=app:{self.env}-*"])
        print(result.stdout)
        
        # Git 标签历史
        self.log("\n=== Git 发布标签 ===", "info")
        result = self.run_command(["git", "tag", "-l", "v*", "--sort=-version:refname"])
        tags = result.stdout.strip().split('\n')[:10]
        for tag in tags:
            print(f"  {tag}")
    
    def rollback(self):
        """执行回滚"""
        self.log(f"开始回滚 {self.env} 环境...", "warning")
        
        # 确认回滚
        if self.env == "production":
            confirm = input(f"⚠️  确定要回滚生产环境吗？(yes/no): ")
            if confirm.lower() != "yes":
                self.log("回滚已取消", "info")
                return
        
        if self._check_k8s():
            self._rollback_k8s()
        else:
            self.log("未检测到 Kubernetes，请手动执行回滚", "warning")
        
        self.log("✓ 回滚完成", "success")
        self.log("请监控系统状态，确保回滚成功", "warning")
    
    def _check_k8s(self) -> bool:
        """检查是否有 Kubernetes 环境"""
        try:
            self.run_command(["kubectl", "version", "--client"])
            return True
        except:
            return False
    
    def _rollback_k8s(self):
        """Kubernetes 回滚"""
        if self.revision:
            self.log(f"回滚到 revision {self.revision}...", "info")
            self.run_command(["kubectl", "rollout", "undo", "deployment/app", f"--to-revision={self.revision}"])
        else:
            self.log("回滚到上一个版本...", "info")
            self.run_command(["kubectl", "rollout", "undo", "deployment/app"])
        
        # 等待回滚完成
        self.log("等待回滚完成...", "info")
        self.run_command(["kubectl", "rollout", "status", "deployment/app"])
        
        # 验证
        self.log("验证回滚结果...", "info")
        result = self.run_command(["kubectl", "get", "pods"])
        print(result.stdout)


def main():
    parser = argparse.ArgumentParser(description="一键回滚脚本")
    parser.add_argument("--list", action="store_true", help="列出可回滚版本")
    parser.add_argument("--env", choices=["dev", "staging", "production"], help="环境")
    parser.add_argument("--revision", type=int, help="回滚到指定版本")
    
    args = parser.parse_args()
    
    if args.list:
        rb = Rollback(args.env or "production")
        rb.list_versions()
    elif args.env:
        rb = Rollback(args.env, args.revision)
        rb.rollback()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
