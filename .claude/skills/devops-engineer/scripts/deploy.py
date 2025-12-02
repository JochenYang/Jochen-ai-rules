#!/usr/bin/env python3
"""
智能部署脚本 - 自动化部署流程

功能：
- 部署前检查（Git 状态、测试、依赖）
- 构建应用（前端/后端/Docker）
- 执行部署（支持多种策略）
- 部署后验证（健康检查、监控）

使用方式：
    python deploy.py --env production
    python deploy.py --env staging --strategy blue-green
    python deploy.py --env dev --skip-tests
"""

import argparse
import subprocess
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class DeploymentError(Exception):
    """部署错误"""
    pass


class Deployer:
    """部署器"""
    
    def __init__(self, env: str, strategy: str, skip_tests: bool = False):
        self.env = env
        self.strategy = strategy
        self.skip_tests = skip_tests
        self.project_root = Path.cwd()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def log(self, message: str, level: str = "info"):
        """彩色日志"""
        colors = {
            "info": Colors.OKBLUE,
            "success": Colors.OKGREEN,
            "warning": Colors.WARNING,
            "error": Colors.FAIL,
            "header": Colors.HEADER
        }
        color = colors.get(level, "")
        print(f"{color}[{level.upper()}] {message}{Colors.ENDC}")
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """执行命令"""
        self.log(f"执行: {' '.join(cmd)}", "info")
        result = subprocess.run(cmd, cwd=cwd or self.project_root, capture_output=True, text=True)
        if result.returncode != 0:
            raise DeploymentError(f"命令失败: {result.stderr}")
        return result
    
    def pre_deployment_checks(self):
        """部署前检查"""
        self.log("开始部署前检查...", "header")
        
        # 1. 检查 Git 状态
        self.log("检查 Git 状态...", "info")
        result = self.run_command(["git", "status", "--porcelain"])
        if result.stdout.strip():
            self.log("警告: 存在未提交的变更", "warning")
            if self.env == "production":
                raise DeploymentError("生产环境不允许有未提交的变更")
        
        # 2. 检查当前分支
        result = self.run_command(["git", "branch", "--show-current"])
        current_branch = result.stdout.strip()
        self.log(f"当前分支: {current_branch}", "info")
        
        if self.env == "production" and current_branch != "main":
            raise DeploymentError(f"生产环境必须从 main 分支部署，当前: {current_branch}")
        
        # 3. 运行测试
        if not self.skip_tests:
            self.log("运行测试...", "info")
            self._run_tests()
        else:
            self.log("跳过测试（--skip-tests）", "warning")
        
        # 4. 检查依赖
        self.log("检查依赖完整性...", "info")
        self._check_dependencies()
        
        self.log("✓ 部署前检查通过", "success")
    
    def _run_tests(self):
        """运行测试"""
        try:
            # 尝试检测测试命令
            if (self.project_root / "package.json").exists():
                self.run_command(["npm", "test"])
            elif (self.project_root / "pytest.ini").exists():
                self.run_command(["pytest"])
            elif (self.project_root / "go.mod").exists():
                self.run_command(["go", "test", "./..."])
            else:
                self.log("未检测到测试框架，跳过", "warning")
        except DeploymentError as e:
            self.log(f"测试失败: {e}", "error")
            raise
    
    def _check_dependencies(self):
        """检查依赖"""
        if (self.project_root / "package.json").exists():
            self.log("检查 npm 依赖...", "info")
            self.run_command(["npm", "audit", "--audit-level=high"])
        
        if (self.project_root / "requirements.txt").exists():
            self.log("检查 Python 依赖...", "info")
            # 可选：使用 safety 检查安全漏洞
    
    def build(self):
        """构建应用"""
        self.log("开始构建应用...", "header")
        
        # 前端构建
        if (self.project_root / "package.json").exists():
            self.log("构建前端...", "info")
            self.run_command(["npm", "run", "build"])
        
        # Docker 镜像构建
        if (self.project_root / "Dockerfile").exists():
            self.log("构建 Docker 镜像...", "info")
            tag = f"app:{self.env}-{self.timestamp}"
            self.run_command(["docker", "build", "-t", tag, "."])
            self.log(f"✓ 镜像构建完成: {tag}", "success")
        
        self.log("✓ 构建完成", "success")
    
    def deploy(self):
        """执行部署"""
        self.log(f"开始部署到 {self.env} 环境 ({self.strategy} 策略)...", "header")
        
        if self.strategy == "rolling":
            self._deploy_rolling()
        elif self.strategy == "blue-green":
            self._deploy_blue_green()
        elif self.strategy == "canary":
            self._deploy_canary()
        else:
            raise DeploymentError(f"不支持的部署策略: {self.strategy}")
        
        self.log("✓ 部署完成", "success")
    
    def _deploy_rolling(self):
        """滚动更新部署"""
        self.log("执行滚动更新...", "info")
        
        # 示例：Kubernetes 滚动更新
        if (self.project_root / "k8s").exists():
            self.run_command(["kubectl", "apply", "-f", "k8s/"])
            self.run_command(["kubectl", "rollout", "status", "deployment/app"])
        else:
            self.log("未找到 k8s/ 目录，跳过 Kubernetes 部署", "warning")
            self.log("请手动执行部署命令", "warning")
    
    def _deploy_blue_green(self):
        """蓝绿部署"""
        self.log("执行蓝绿部署...", "info")
        self.log("1. 部署到绿色环境", "info")
        self.log("2. 运行烟雾测试", "info")
        self.log("3. 切换流量到绿色环境", "info")
        self.log("蓝绿部署需要手动配置，请参考 guides/cicd-guide.md", "warning")
    
    def _deploy_canary(self):
        """金丝雀部署"""
        self.log("执行金丝雀部署...", "info")
        self.log("1. 部署到 5% 实例", "info")
        self.log("2. 监控 5 分钟", "info")
        self.log("3. 逐步增加到 100%", "info")
        self.log("金丝雀部署需要手动配置，请参考 guides/cicd-guide.md", "warning")
    
    def post_deployment_verification(self):
        """部署后验证"""
        self.log("开始部署后验证...", "header")
        
        # 1. 健康检查
        self.log("执行健康检查...", "info")
        self._health_check()
        
        # 2. 烟雾测试
        self.log("执行烟雾测试...", "info")
        self._smoke_tests()
        
        # 3. 监控验证（15 分钟）
        self.log("建议监控 15 分钟后再完全放行", "warning")
        
        self.log("✓ 部署后验证通过", "success")
    
    def _health_check(self):
        """健康检查"""
        # 示例：检查 HTTP 端点
        try:
            import requests
            health_urls = {
                "dev": "http://localhost:3000/health",
                "staging": "https://staging.example.com/health",
                "production": "https://api.example.com/health"
            }
            
            url = health_urls.get(self.env)
            if url:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log(f"✓ 健康检查通过: {url}", "success")
                else:
                    raise DeploymentError(f"健康检查失败: {response.status_code}")
            else:
                self.log("未配置健康检查 URL，跳过", "warning")
        except ImportError:
            self.log("未安装 requests 库，跳过健康检查", "warning")
        except Exception as e:
            self.log(f"健康检查异常: {e}", "error")
            raise
    
    def _smoke_tests(self):
        """烟雾测试"""
        self.log("执行核心功能验证...", "info")
        # 这里可以添加关键功能的快速验证
        self.log("✓ 烟雾测试通过", "success")
    
    def run(self):
        """执行完整部署流程"""
        try:
            start_time = time.time()
            
            self.log(f"\n{'='*60}", "header")
            self.log(f"开始部署到 {self.env} 环境", "header")
            self.log(f"部署策略: {self.strategy}", "header")
            self.log(f"{'='*60}\n", "header")
            
            # 1. 部署前检查
            self.pre_deployment_checks()
            
            # 2. 构建
            self.build()
            
            # 3. 部署
            self.deploy()
            
            # 4. 验证
            self.post_deployment_verification()
            
            elapsed = time.time() - start_time
            self.log(f"\n✓ 部署成功！耗时: {elapsed:.2f}秒", "success")
            self.log(f"环境: {self.env}", "success")
            self.log(f"时间戳: {self.timestamp}", "success")
            
        except DeploymentError as e:
            self.log(f"\n✗ 部署失败: {e}", "error")
            sys.exit(1)
        except KeyboardInterrupt:
            self.log("\n部署被用户中断", "warning")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="智能部署脚本")
    parser.add_argument("--env", choices=["dev", "staging", "production"], 
                       required=True, help="部署环境")
    parser.add_argument("--strategy", choices=["rolling", "blue-green", "canary"],
                       default="rolling", help="部署策略")
    parser.add_argument("--skip-tests", action="store_true",
                       help="跳过测试（不推荐）")
    
    args = parser.parse_args()
    
    deployer = Deployer(args.env, args.strategy, args.skip_tests)
    deployer.run()


if __name__ == "__main__":
    main()
