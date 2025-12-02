#!/usr/bin/env python3
"""
测试模板生成器 - 快速生成测试代码

使用方式：
    python test-template.py src/api/user.py        # 为 Python 文件生成测试
    python test-template.py src/components/Button.tsx  # 为 React 组件生成测试
"""

import argparse
import ast
from pathlib import Path


def generate_python_test(src_file: Path) -> str:
    """生成 Python 测试模板"""
    # 解析源文件，提取函数/类
    with open(src_file, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    
    module_name = src_file.stem
    test_code = f'''"""
测试 {module_name} 模块
"""

import pytest
from {module_name} import {', '.join(classes + functions[:3])}


'''
    
    # 为函数生成测试
    for func in functions[:5]:
        test_code += f'''def test_{func}():
    """测试 {func} 函数"""
    # TODO: 实现测试逻辑
    assert True


'''
    
    # 为类生成测试
    for cls in classes[:3]:
        test_code += f'''class Test{cls}:
    """测试 {cls} 类"""
    
    def test_init(self):
        """测试初始化"""
        # TODO: 实现测试逻辑
        assert True


'''
    
    return test_code


def generate_jest_test(src_file: Path) -> str:
    """生成 Jest 测试模板"""
    module_name = src_file.stem
    
    test_code = f'''/**
 * 测试 {module_name}
 */

import {{ describe, it, expect }} from '@jest/globals';
import {{ {module_name} }} from './{module_name}';

describe('{module_name}', () => {{
  it('should work correctly', () => {{
    // TODO: 实现测试逻辑
    expect(true).toBe(true);
  }});
}});
'''
    return test_code


def main():
    parser = argparse.ArgumentParser(description="测试模板生成器")
    parser.add_argument("file", type=str, help="源文件路径")
    args = parser.parse_args()
    
    src_file = Path(args.file)
    if not src_file.exists():
        print(f"错误: 文件不存在 {src_file}")
        return
    
    # 根据文件类型生成测试
    if src_file.suffix == '.py':
        test_code = generate_python_test(src_file)
        test_file = src_file.parent / f"test_{src_file.name}"
    else:
        test_code = generate_jest_test(src_file)
        test_file = src_file.parent / f"{src_file.stem}.test{src_file.suffix}"
    
    # 写入测试文件
    test_file.write_text(test_code, encoding='utf-8')
    print(f"✓ 测试文件已生成: {test_file}")


if __name__ == "__main__":
    main()
