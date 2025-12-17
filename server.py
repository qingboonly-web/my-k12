import logging
import os
import asyncio
from typing import List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sheerid_verifier import SheerIDVerifier

# --- 日志处理 ---
class WebSocketLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    def emit(self, record):
        log_entry = self.format(record)
        # 因为 emit 是同步的，我们需要在一个事件循环中发送消息
        # 这里简单的使用 fire-and-forget，或者放入一个队列
        # 为了简单起见，我们尝试获取当前的事件循环并创建一个任务
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(self.broadcast(log_entry), loop)
        except RuntimeError:
            # 如果没有运行的循环（不太可能，因为我们在 FastAPI 中），忽略
            pass

    async def broadcast(self, message: str):
        for connection in self.connections[:]:
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

# 创建全局的 handler
ws_log_handler = WebSocketLogHandler()
ws_log_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
# 获取 root logger 并添加我们的 handler
root_logger = logging.getLogger()
root_logger.addHandler(ws_log_handler)
# 确保 sheerid_verifier 的 logger 也能被捕获 (通常它会向上传播到 root)

logger = logging.getLogger(__name__)

app = FastAPI(title="K12 SheerID Verifier")

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await ws_log_handler.connect(websocket)
    try:
        while True:
            # 保持连接，接收消息（虽然我们可以只单向发送）
            # 这里的 await 是必须的，否则连接可能会关闭
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_log_handler.disconnect(websocket)
    except Exception:
        ws_log_handler.disconnect(websocket)

class VerifyRequest(BaseModel):
    url_or_id: str

@app.post("/api/verify")
def verify(request: VerifyRequest):
    input_val = request.url_or_id
    
    # 尝试解析 ID
    if "verificationId" in input_val or "http" in input_val:
        verification_id = SheerIDVerifier.parse_verification_id(input_val)
        if not verification_id:
            raise HTTPException(status_code=400, detail="无法从 URL 中解析 Verification ID")
    else:
        # 假设输入的就是 ID
        verification_id = input_val

    logger.info(f"开始验证，ID: {verification_id}")
    
    try:
        verifier = SheerIDVerifier(verification_id)
        result = verifier.verify()
        
        if result['success']:
            logger.info("验证提交成功！")
            return result
        else:
            logger.error("验证提交失败！")
            return result
            
    except Exception as e:
        logger.error(f"系统错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 提供静态文件服务
# 我们将 index.html 放在 static 目录下，或者直接根目录
# 这里简单起见，如果请求根路径，返回 index.html
@app.get("/")
async def read_index():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    # 监听所有IP，方便局域网访问（虽然这里是本地运行）
    uvicorn.run(app, host="0.0.0.0", port=8000)
