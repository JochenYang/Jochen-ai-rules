import sys
import unittest
from pathlib import Path

# 设置正确的导入路径
SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'scripts'
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from context_engine.semantic_chunker import SemanticChunker

class TestSemanticChunker(unittest.TestCase):
    def test_chunk_small_file_unchanged(self):
        """小于60行的文件应保持原样"""
        content = """def foo():
    return 42

def bar():
    return 24
        """
        chunker = SemanticChunker()
        chunks = chunker.chunk_file(content, "test.py", "python")

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["kind"], "section")

    def test_chunk_function_boundary(self):
        """基于函数边界分块"""
        # 超过60行的内容以触发AST分块
        content = """
def authenticate(user):
    '''用户认证函数

    处理用户登录验证，返回认证结果。
    支持多种认证方式：
    - 用户名密码
    - OAuth2
    - API Key
    - SAML
    '''
    # 验证用户输入
    if not user:
        raise ValueError("User is required")
    # 验证用户凭证
    if not self._validate_credentials(user):
        raise ValueError("Invalid credentials")
    # 查找用户信息
    user_info = self._find_user(user)
    if not user_info:
        raise ValueError("User not found")
    # 生成认证token
    token = self._generate_token(user_info)
    # 记录登录日志
    self._log_login(user_info)
    # 返回认证结果
    return {"success": True, "token": token, "user": user_info}

def validate_token(token):
    '''验证Token有效性

    检查token是否过期或被撤销。
    支持多种token类型：
    - JWT
    - Bearer
    - Session
    - API Key
    '''
    # 解析token
    if not token:
        raise ValueError("Token is required")
    # 检查token格式
    parsed = self._parse_token(token)
    if not parsed:
        return {"valid": False, "reason": "Invalid format"}
    # 检查过期时间
    if self._is_token_expired(parsed):
        return {"valid": False, "reason": "Token expired"}
    # 验证签名
    if not self._verify_signature(parsed):
        return {"valid": False, "reason": "Invalid signature"}
    # 检查是否被撤销
    if self._is_token_revoked(parsed):
        return {"valid": False, "reason": "Token revoked"}
    return {"valid": True}

def process_request(request_data):
    '''处理请求数据

    统一的请求处理入口。
    进行参数验证、权限检查、
    业务逻辑处理和响应构建。
    '''
    # 验证请求格式
    if not self._validate_request_format(request_data):
        raise ValueError("Invalid request format")
    # 检查用户权限
    if not self._check_permissions(request_data):
        raise PermissionError("Insufficient permissions")
    # 执行业务逻辑
    result = self._execute_business_logic(request_data)
    # 记录操作日志
    self._log_operation(request_data, result)
    # 返回处理结果
    return result
"""
        chunker = SemanticChunker()
        chunks = chunker.chunk_file(content, "test.py", "python")

        # 应该分成三个 chunk
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0]["kind"], "function")
        self.assertEqual(chunks[0]["name"], "authenticate")
        self.assertEqual(chunks[1]["kind"], "function")
        self.assertEqual(chunks[1]["name"], "validate_token")
        self.assertEqual(chunks[2]["kind"], "function")
        self.assertEqual(chunks[2]["name"], "process_request")

    def test_extract_signals(self):
        """提取语义信号"""
        content = """def process_payment(amount, currency):
    '''Process payment with Stripe.'''
    pass
"""
        chunker = SemanticChunker()
        chunks = chunker.chunk_file(content, "test.py", "python")

        self.assertEqual(len(chunks), 1)
        signals = chunks[0]["signals"]
        self.assertIn("payment", signals)
        self.assertIn("stripe", signals)

    def test_class_chunking(self):
        """类级别的智能分块"""
        # 超过60行的内容以触发AST分块
        content = """
class PaymentService:
    '''支付服务类

    提供完整的支付处理功能，包括：
    - 支付处理
    - 退款处理
    - 订单管理
    - 交易查询
    - 账单生成

    支持多种支付渠道：
    - Stripe
    - PayPal
    - 支付宝
    - 微信支付
    '''
    def __init__(self):
        '''初始化支付服务'''
        self.merchant_id = None
        self.api_key = None
        self.environment = 'sandbox'
        self.retry_count = 3
        self.timeout = 30

    def process(self, amount):
        '''处理支付请求

        主要流程：
        1. 验证支付参数
        2. 构建支付请求
        3. 调用支付网关
        4. 处理支付结果
        5. 记录交易日志
        '''
        # 验证金额
        if amount <= 0:
            raise ValueError("Amount must be positive")
        # 构建请求
        request = self._build_payment_request(amount)
        # 调用网关
        result = self._call_payment_gateway(request)
        # 处理结果
        return self._handle_payment_result(result)

    def refund(self, transaction_id):
        '''处理退款请求

        退款流程：
        1. 验证交易ID
        2. 查询原交易
        3. 验证退款条件
        4. 发起退款
        5. 返回退款结果
        '''
        # 验证交易ID
        if not transaction_id:
            raise ValueError("Transaction ID is required")
        # 查询原交易
        original = self._get_original_transaction(transaction_id)
        # 验证退款条件
        if not self._can_refund(original):
            raise ValueError("Transaction cannot be refunded")
        # 发起退款
        refund_result = self._execute_refund(original)
        # 返回结果
        return self._handle_refund_result(refund_result)
"""
        chunker = SemanticChunker()
        chunks = chunker.chunk_file(content, "test.py", "python")

        # 整个类应作为一个 chunk
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["kind"], "class")
        self.assertEqual(chunks[0]["name"], "PaymentService")


if __name__ == "__main__":
    unittest.main()
