#!/usr/bin/env python3
"""
性能分析脚本 - 自动识别性能瓶颈

功能：
- Python profiling（cProfile）
- Node.js profiling（--prof）
- 数据库慢查询分析
- API 响应时间分析

使用方式：
    python profile.py --python app.py         # Python 性能分析
    python profile.py --node server.js        # Node.js 性能分析
    python profile.py --db postgres           # 数据库慢查询
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List


class Profiler:
    """性能分析器"""
    
    def __init__(self, target_type: str, target_file: str = None):
        self.target_type = target_type
        self.target_file = target_file
        self.project_root = Path.cwd()
    
    def log(self, message: str):
        print(f"[INFO] {message}")
    
    def run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        return result
    
    def profile(self):
        """执行性能分析"""
        if self.target_type == "python":
            self._profile_python()
        elif self.target_type == "node":
            self._profile_node()
        elif self.target_type == "db":
            self._profile_database()
        else:
            self.log(f"不支持的类型: {self.target_type}")
    
    def _profile_python(self):
        """Python 性能分析"""
        if not self.target_file:
            self.log("错误: 请指定 Python 文件")
            return
        
        self.log(f"分析 Python 应用: {self.target_file}")
        
        # 使用 cProfile
        self.log("使用 cProfile 进行性能分析...")
        cmd = ["python", "-m", "cProfile", "-o", "profile.stats", self.target_file]
        
        self.log(f"执行: {' '.join(cmd)}")
        result = self.run_command(cmd)
        
        if result.returncode != 0:
            self.log(f"错误: {result.stderr}")
            return
        
        # 生成可读报告
        self.log("生成性能报告...")
        self._generate_python_report()
    
    def _generate_python_report(self):
        """生成 Python 性能报告"""
        import pstats
        from pstats import SortKey
        
        stats = pstats.Stats('profile.stats')
        
        # 按累计时间排序
        print("\n=== 按累计时间排序（Top 20） ===")
        stats.sort_stats(SortKey.CUMULATIVE).print_stats(20)
        
        # 按调用次数排序
        print("\n=== 按调用次数排序（Top 20） ===")
        stats.sort_stats(SortKey.CALLS).print_stats(20)
        
        self.log("✓ 性能分析完成")
        self.log("详细数据: profile.stats")
    
    def _profile_node(self):
        """Node.js 性能分析"""
        if not self.target_file:
            self.log("错误: 请指定 Node.js 文件")
            return
        
        self.log(f"分析 Node.js 应用: {self.target_file}")
        
        # 使用 --prof
        self.log("使用 --prof 进行性能分析...")
        cmd = ["node", "--prof", self.target_file]
        
        self.log(f"执行: {' '.join(cmd)}")
        self.log("应用将运行 30 秒...")
        
        proc = subprocess.Popen(cmd, cwd=self.project_root)
        time.sleep(30)  # 运行 30 秒
        proc.terminate()
        
        # 处理 profiling 数据
        self.log("处理 profiling 数据...")
        isolate_files = list(self.project_root.glob("isolate-*.log"))
        
        if isolate_files:
            isolate_file = isolate_files[0]
            cmd = ["node", "--prof-process", str(isolate_file)]
            result = self.run_command(cmd)
            
            # 保存报告
            report_file = self.project_root / "profile-report.txt"
            report_file.write_text(result.stdout)
            
            self.log("✓ 性能分析完成")
            self.log(f"报告: {report_file}")
        else:
            self.log("错误: 未找到 profiling 数据文件")
    
    def _profile_database(self):
        """数据库慢查询分析"""
        self.log("分析数据库慢查询...")
        
        if self.target_file == "postgres":
            self._profile_postgres()
        elif self.target_file == "mysql":
            self._profile_mysql()
        else:
            self.log("请指定数据库类型: postgres 或 mysql")
    
    def _profile_postgres(self):
        """PostgreSQL 慢查询"""
        self.log("查询 PostgreSQL 慢查询...")
        
        sql = """
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            max_time
        FROM pg_stat_statements
        ORDER BY total_time DESC
        LIMIT 20;
        """
        
        cmd = ["psql", "-c", sql]
        result = self.run_command(cmd)
        
        if result.returncode == 0:
            print("\n=== PostgreSQL 慢查询 Top 20 ===")
            print(result.stdout)
            self.log("✓ 查询完成")
        else:
            self.log(f"错误: {result.stderr}")
            self.log("提示: 确保已启用 pg_stat_statements 扩展")
    
    def _profile_mysql(self):
        """MySQL 慢查询"""
        self.log("查询 MySQL 慢查询...")
        
        sql = """
        SELECT 
            sql_text,
            count_star AS exec_count,
            avg_timer_wait / 1000000000000 AS avg_time_sec,
            max_timer_wait / 1000000000000 AS max_time_sec
        FROM performance_schema.events_statements_summary_by_digest
        ORDER BY avg_timer_wait DESC
        LIMIT 20;
        """
        
        cmd = ["mysql", "-e", sql]
        result = self.run_command(cmd)
        
        if result.returncode == 0:
            print("\n=== MySQL 慢查询 Top 20 ===")
            print(result.stdout)
            self.log("✓ 查询完成")
        else:
            self.log(f"错误: {result.stderr}")


def main():
    parser = argparse.ArgumentParser(description="性能分析脚本")
    parser.add_argument("--python", type=str, help="Python 文件")
    parser.add_argument("--node", type=str, help="Node.js 文件")
    parser.add_argument("--db", type=str, choices=["postgres", "mysql"], help="数据库类型")
    
    args = parser.parse_args()
    
    if args.python:
        profiler = Profiler("python", args.python)
    elif args.node:
        profiler = Profiler("node", args.node)
    elif args.db:
        profiler = Profiler("db", args.db)
    else:
        parser.print_help()
        return
    
    profiler.profile()


if __name__ == "__main__":
    main()
