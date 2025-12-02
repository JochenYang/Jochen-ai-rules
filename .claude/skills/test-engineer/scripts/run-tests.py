#!/usr/bin/env python3
"""
智能测试运行脚本 - 只运行受影响的测试

功能：
- 检测代码变更
- 分析依赖关系
- 只运行受影响的测试（节省时间）
- 生成测试报告

使用方式：
    python run-tests.py                    # 运行所有测试
    python run-tests.py --changed-only     # 只运行受影响的测试
    python run-tests.py --pattern "test_api*"  # 运行匹配的测试
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from typing import List, Set


class TestRunner:
    """智能测试运行器"""
    
    def __init__(self, changed_only: bool = False, pattern: str = None):
        self.changed_only = changed_only
        self.pattern = pattern
        self.project_root = Path.cwd()
        
    def log(self, message: str):
        print(f"[INFO] {message}")
    
    def run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        return result
    
    def get_changed_files(self) -> Set[str]:
        """获取变更的文件"""
        self.log("检测代码变更...")
        
        # Git diff（相对于 main 分支）
        result = self.run_command(["git", "diff", "--name-only", "main...HEAD"])
        if result.returncode != 0:
            # 如果没有 main 分支，检查工作区变更
            result = self.run_command(["git", "diff", "--name-only"])
        
        changed_files = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
        self.log(f"变更文件数: {len(changed_files)}")
        return changed_files
    
    def find_affected_tests(self, changed_files: Set[str]) -> List[str]:
        """分析受影响的测试"""
        self.log("分析受影响的测试...")
        
        affected_tests = []
        
        for file in changed_files:
            file_path = Path(file)
            
            # 直接变更的测试文件
            if self._is_test_file(file):
                affected_tests.append(file)
                continue
            
            # 查找对应的测试文件
            test_file = self._find_test_file(file_path)
            if test_file and test_file.exists():
                affected_tests.append(str(test_file))
        
        self.log(f"受影响的测试: {len(affected_tests)}")
        return list(set(affected_tests))  # 去重
    
    def _is_test_file(self, file: str) -> bool:
        """判断是否为测试文件"""
        file_lower = file.lower()
        return (
            'test' in file_lower or
            file.endswith('_test.py') or
            file.endswith('_test.js') or
            file.endswith('.test.ts') or
            file.endswith('.spec.ts')
        )
    
    def _find_test_file(self, src_file: Path) -> Path:
        """查找对应的测试文件"""
        # Python 测试约定
        if src_file.suffix == '.py':
            # 1. 同目录下的 test_*.py
            test_file = src_file.parent / f"test_{src_file.stem}.py"
            if test_file.exists():
                return test_file
            
            # 2. tests/ 目录
            test_file = self.project_root / "tests" / f"test_{src_file.stem}.py"
            if test_file.exists():
                return test_file
        
        # JavaScript/TypeScript 测试约定
        elif src_file.suffix in ['.js', '.ts', '.jsx', '.tsx']:
            # 1. 同目录下的 *.test.ts
            test_file = src_file.parent / f"{src_file.stem}.test{src_file.suffix}"
            if test_file.exists():
                return test_file
            
            # 2. __tests__/ 目录
            test_file = src_file.parent / "__tests__" / f"{src_file.stem}.test{src_file.suffix}"
            if test_file.exists():
                return test_file
        
        return None
    
    def run_tests(self):
        """运行测试"""
        test_files = []
        
        if self.changed_only:
            changed_files = self.get_changed_files()
            if not changed_files:
                self.log("没有代码变更，跳过测试")
                return
            
            test_files = self.find_affected_tests(changed_files)
            if not test_files:
                self.log("没有受影响的测试")
                return
        
        # 检测测试框架并运行
        if self._has_pytest():
            self._run_pytest(test_files)
        elif self._has_jest():
            self._run_jest(test_files)
        elif self._has_go_test():
            self._run_go_test()
        else:
            self.log("未检测到测试框架", "warning")
    
    def _has_pytest(self) -> bool:
        return (self.project_root / "pytest.ini").exists() or \
               (self.project_root / "pyproject.toml").exists()
    
    def _has_jest(self) -> bool:
        package_json = self.project_root / "package.json"
        if package_json.exists():
            data = json.loads(package_json.read_text())
            return "jest" in data.get("devDependencies", {}) or \
                   "jest" in data.get("dependencies", {})
        return False
    
    def _has_go_test(self) -> bool:
        return (self.project_root / "go.mod").exists()
    
    def _run_pytest(self, test_files: List[str] = None):
        """运行 pytest"""
        self.log("运行 Python 测试 (pytest)...")
        
        cmd = ["pytest", "-v", "--tb=short"]
        
        # 覆盖率
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
        
        # 指定测试文件
        if test_files:
            cmd.extend(test_files)
        elif self.pattern:
            cmd.extend(["-k", self.pattern])
        
        result = self.run_command(cmd)
        print(result.stdout)
        
        if result.returncode != 0:
            print(result.stderr)
            sys.exit(1)
        
        self.log("✓ 测试通过")
        self.log("覆盖率报告: htmlcov/index.html")
    
    def _run_jest(self, test_files: List[str] = None):
        """运行 Jest"""
        self.log("运行 JavaScript/TypeScript 测试 (Jest)...")
        
        cmd = ["npm", "test", "--", "--verbose"]
        
        # 覆盖率
        cmd.append("--coverage")
        
        # 指定测试文件
        if test_files:
            cmd.extend(test_files)
        elif self.pattern:
            cmd.extend(["--testNamePattern", self.pattern])
        
        result = self.run_command(cmd)
        print(result.stdout)
        
        if result.returncode != 0:
            print(result.stderr)
            sys.exit(1)
        
        self.log("✓ 测试通过")
        self.log("覆盖率报告: coverage/lcov-report/index.html")
    
    def _run_go_test(self):
        """运行 Go 测试"""
        self.log("运行 Go 测试...")
        
        cmd = ["go", "test", "-v", "-race", "-coverprofile=coverage.out", "./..."]
        
        if self.pattern:
            cmd.extend(["-run", self.pattern])
        
        result = self.run_command(cmd)
        print(result.stdout)
        
        if result.returncode != 0:
            print(result.stderr)
            sys.exit(1)
        
        # 生成覆盖率 HTML
        self.run_command(["go", "tool", "cover", "-html=coverage.out", "-o", "coverage.html"])
        
        self.log("✓ 测试通过")
        self.log("覆盖率报告: coverage.html")


def main():
    parser = argparse.ArgumentParser(description="智能测试运行脚本")
    parser.add_argument("--changed-only", action="store_true",
                       help="只运行受影响的测试")
    parser.add_argument("--pattern", type=str,
                       help="测试名称匹配模式")
    
    args = parser.parse_args()
    
    runner = TestRunner(args.changed_only, args.pattern)
    runner.run_tests()


if __name__ == "__main__":
    main()
