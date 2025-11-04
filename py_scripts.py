import requests
from PIL import Image
from io import BytesIO
from cairosvg import svg2png
import os

def convert_svg_to_jpeg_and_optimize(svg_url, output_path, max_file_size_mb=2, target_width=None, target_height=None, quality=85):
    """
    根据 SVG URL 将其转换为 JPEG 格式，并控制文件大小在指定 MB 范围内。

    Args:
        svg_url (str): SVG 文件的 URL。
        output_path (str): 输出 JPEG 文件的完整路径。
        max_file_size_mb (int): JPEG 文件的最大允许大小（MB）。
        target_width (int, optional): 如果指定，输出图片将被缩放到此宽度。保持宽高比。
        target_height (int, optional): 如果指定，输出图片将被缩放到此高度。保持宽高比。
        quality (int): JPEG 压缩质量（0-100）。数字越大质量越高，文件越大。
    
    Returns:
        str: 成功转换后的 JPEG 文件路径，或 None (如果失败)。
    """
    max_file_size_bytes = max_file_size_mb * 1024 * 1024

    print(f"正在从 URL 下载 SVG: {svg_url}")
    try:
        response = requests.get(svg_url, timeout=10)
        response.raise_for_status() # 检查 HTTP 错误
        svg_data = response.content
    except requests.exceptions.RequestException as e:
        print(f"下载 SVG 失败: {e}")
        return None

    # 1. 使用 CairoSVG 将 SVG 渲染为 PNG
    # 这一步将矢量图转换为位图，可以指定输出的宽度/高度
    try:
        # 如果没有指定目标尺寸，CairoSVG 会尝试根据SVG内部的viewBox或width/height来渲染
        # 如果SVG本身没有明确尺寸，默认可能很小，所以通常建议指定target_width/height
        # 或者在第一次渲染时先获取一个较大的中间PNG，再用Pillow缩放
        if target_width or target_height:
            # CairoSVG渲染时，优先使用width/height参数，它会保持比例
            png_bytes = svg2png(bytestring=svg_data, write_to=None, 
                                parent_width=target_width, parent_height=target_height)
        else:
            # 默认渲染到一个合理的大小，例如 512x512
            png_bytes = svg2png(bytestring=svg_data, write_to=None, parent_width=512, parent_height=512)

        print("SVG 渲染为 PNG 成功。")
    except Exception as e:
        print(f"SVG 渲染为 PNG 失败: {e}")
        return None

    # 2. 使用 Pillow 将 PNG 转换为 JPEG 并进行优化
    try:
        img = Image.open(BytesIO(png_bytes)).convert("RGB") # 转换为 RGB 模式以便保存为 JPEG

        # 如果之前没有指定 target_width/height，并且生成的PNG尺寸不理想，可以在这里再次调整
        if not (target_width or target_height): # 假设我们希望最终JPEG有一个推荐的尺寸
            if img.width > 800 or img.height > 800: # 如果PNG太大
                img.thumbnail((800, 800), Image.Resampling.LANCZOS) # 缩放至最大800x800

        # 初始化优化参数
        current_quality = quality
        file_buffer = BytesIO()

        # 尝试不同质量等级，直到文件大小满足要求
        while True:
            file_buffer.seek(0)
            file_buffer.truncate(0) # 清空缓冲区
            
            img.save(file_buffer, "jpeg", quality=current_quality, optimize=True)
            current_size = file_buffer.tell()

            print(f"尝试质量 {current_quality}, 文件大小: {current_size / (1024 * 1024):.2f} MB")

            if current_size <= max_file_size_bytes or current_quality <= 10:
                # 文件大小已满足要求 或 质量已降到最低
                if current_quality <= 10 and current_size > max_file_size_bytes:
                    print("警告: 即使质量降到最低，文件大小仍超过限制。")
                break
            
            # 如果文件太大，降低质量
            current_quality -= 5 # 每次降低5点质量
            if current_quality < 10: # 质量不能低于10
                current_quality = 10
        
        # 将最终优化后的图片保存到文件
        with open(output_path, 'wb') as f:
            f.write(file_buffer.getvalue())
        
        final_size = os.path.getsize(output_path)
        print(f"成功转换并保存 JPEG 到: {output_path}, 最终大小: {final_size / (1024 * 1024):.2f} MB")
        return output_path

    except Exception as e:
        print(f"处理或保存 JPEG 失败: {e}")
        return None

# --- 使用示例 ---
if __name__ == "__main__":
    # 示例 SVG URL (这里用一个简单的在线SVG作为例子)
    # 你可以替换成你自己的SVG URL
    # 这个SVG是一个蓝色圆圈
    example_svg_url = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_checker.png" # 这是一个PNG，但我们可以用它模拟图片下载
    # 找一个真实的SVG例子:
    example_svg_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Circle_of_red_colour.svg/512px-Circle_of_red_colour.svg.png" # 这是一个PNG

    # 替换成实际的 SVG URL
    # 你可以尝试一个简单的SVG，例如 GitHub 的 Octocat SVG
    # 注意：这个URL是GitHub用来展示SVG的PNG版本，并非原始SVG文件
    # example_svg_url = "https://raw.githubusercontent.com/primer/octicons/main/icons/mark-github-16.svg" # 这是一个SVG
    # example_svg_url = "https://upload.wikimedia.org/wikipedia/commons/0/02/SVG_logo.svg" # SVG Logo

    output_filename = "output_avatar.jpeg"
    
    # 尝试转换并优化
    converted_file = convert_svg_to_jpeg_and_optimize(
        svg_url=example_svg_url,
        output_path=output_filename,
        max_file_size_mb=0.5, # 将最大文件大小设置为 0.5 MB
        target_width=500,    # 指定输出宽度为 500 像素
        # target_height=500, # 也可以指定高度，或者两者都指定，CairoSVG会保持比例
        quality=90           # 初始JPEG质量
    )

    if converted_file:
        print(f"JPEG 转换完成，文件位于: {converted_file}")
    else:
        print("JPEG 转换失败。")

    # 另一个例子，不指定尺寸
    output_filename_no_size = "output_avatar_default_size.jpeg"
    converted_file_no_size = convert_svg_to_jpeg_and_optimize(
        svg_url=example_svg_url,
        output_path=output_filename_no_size,
        max_file_size_mb=0.5,
        quality=90
    )
    if converted_file_no_size:
        print(f"JPEG (默认尺寸) 转换完成，文件位于: {converted_file_no_size}")
    else:
        print("JPEG (默认尺寸) 转换失败。")