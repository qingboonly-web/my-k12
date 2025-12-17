import sys
import logging
import argparse
from sheerid_verifier import SheerIDVerifier

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="K12 SheerID 本地验证工具")
    parser.add_argument("url_or_id", help="SheerID 验证 URL 或 Verification ID")
    args = parser.parse_args()

    input_val = args.url_or_id
    
    # 尝试解析 ID
    if "verificationId" in input_val or "http" in input_val:
        verification_id = SheerIDVerifier.parse_verification_id(input_val)
        if not verification_id:
            logger.error("无法从 URL 中解析 Verification ID")
            sys.exit(1)
    else:
        # 假设输入的就是 ID
        verification_id = input_val

    logger.info(f"开始验证，ID: {verification_id}")
    
    verifier = SheerIDVerifier(verification_id)
    result = verifier.verify()
    
    if result['success']:
        logger.info("验证提交成功！")
        logger.info(f"结果: {result}")
    else:
        logger.error("验证提交失败！")
        logger.error(f"错误信息: {result.get('message')}")

if __name__ == "__main__":
    main()
