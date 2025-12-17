"""教师证明文档生成（PDF + PNG）"""
import random
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    raise RuntimeError(
        "需要安装 playwright，请执行 `pip install playwright` 然后 `playwright install chromium`"
    ) from exc


def _render_template(first_name: str, last_name: str) -> str:
    """读取模板，替换姓名/工号/日期。"""
    full_name = f"{first_name} {last_name}"
    employee_id = random.randint(1000000, 9999999)
    current_date = datetime.now().strftime("%m/%d/%Y %I:%M %p")

    template_path = Path(__file__).parent / "card2.html"
    html = template_path.read_text(encoding="utf-8")

    # 替换示例姓名 / 员工号 / 日期（模板里出现两处姓名 + span）
    html = html.replace("Michael A. Davis", full_name)
    html = html.replace("E-882910", f"E-{employee_id}")
   
    return html


def generate_teacher_pdf(first_name: str, last_name: str) -> bytes:
    """生成教师证明 PDF 文档字节。"""
    html = _render_template(first_name, last_name)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        # 稍微等待以确保渲染完成
        page.wait_for_timeout(500)
        
        # 打印 PDF
        # format="Letter" 比较适合美国常用的纸张大小
        pdf_data = page.pdf(format="Letter", print_background=True)
        
        browser.close()
        
    return pdf_data


def generate_teacher_png(first_name: str, last_name: str) -> bytes:
    """使用 Playwright 截图生成 PNG。"""
    html = _render_template(first_name, last_name)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 设置较大的视口以容纳完整内容
        page = browser.new_page(viewport={"width": 1200, "height": 1000})
        page.set_content(html, wait_until="load")
        page.wait_for_timeout(500)
        
        # 定位到 .page 元素截图，这样只有卡片部分
        card = page.locator(".page")
        png_bytes = card.screenshot(type="png")
        
        browser.close()

    return png_bytes


# 兼容旧调用：默认生成 PDF
def generate_teacher_image(first_name: str, last_name: str) -> bytes:
    return generate_teacher_pdf(first_name, last_name)
