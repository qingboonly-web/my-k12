import os
from img_generator import generate_teacher_pdf, generate_teacher_png

def test_generation():
    print("生成 PDF...")
    pdf_data = generate_teacher_pdf("John", "Doe")
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_data)
    print(f"PDF 已保存到 test_output.pdf, 大小: {len(pdf_data)} bytes")

    print("生成 PNG...")
    png_data = generate_teacher_png("John", "Doe")
    with open("test_output.png", "wb") as f:
        f.write(png_data)
    print(f"PNG 已保存到 test_output.png, 大小: {len(png_data)} bytes")

if __name__ == "__main__":
    test_generation()
