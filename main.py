import os
import re
import shutil
from datetime import datetime

import yaml
from colorama import Fore, Style, init
from PIL import Image

# 初始化colorama
init()

VERSION = "0.1-Beta"
AUTHOR = "安和（AHCorn）"
PROJECT_URL = "https://github.com/AHCorn/Blog-Webp-Assistant"
# 球球先手动备份，弄坏了不要骂我


def create_backup(folder_path):
    """创建备份
    Args:
        folder_path: 要备份的文件夹路径
    Returns:
        backup_path: 备份文件夹路径
    """
    try:
        # 创建backup文件夹
        script_dir = os.path.dirname(os.path.abspath(__file__))
        backup_dir = os.path.join(script_dir, "backup")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # 使用时间戳创建唯一的备份文件夹
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")

        # 复制文件夹内容
        shutil.copytree(folder_path, backup_path)
        print(f"\n{Fore.GREEN}备份已创建: {backup_path}{Style.RESET_ALL}")
        return backup_path
    except Exception as e:
        print(f"\n{Fore.RED}创建备份时出错: {str(e)}{Style.RESET_ALL}")
        return None


def delete_original_images(folder_path):
    """删除已转换为webp的原始图片
    Args:
        folder_path: 文件夹路径
    Returns:
        deleted_count: 删除的文件数量
    """
    # 首先收集要删除的文件
    files_to_delete = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
                file_path = os.path.join(root, file)
                webp_path = os.path.splitext(file_path)[0] + ".webp"

                if os.path.exists(webp_path):
                    files_to_delete.append(file_path)

    if not files_to_delete:
        print("\n没有找到可删除的文件。")
        return 0

    print(f"\n找到 {len(files_to_delete)} 个可删除的文件：")
    for file in files_to_delete:
        print(file)

    # 询问是否要备份要删除的文件
    if (
        input(
            f"\n{Fore.YELLOW}是否要备份这些即将删除的文件？(y/n，默认y): {Style.RESET_ALL}"
        )
        .strip()
        .lower()
        != "n"
    ):
        if not backup_files_to_delete(folder_path, files_to_delete):
            if (
                input(
                    f"\n{Fore.RED}备份失败，是否继续删除操作？(y/n，默认n): {Style.RESET_ALL}"
                )
                .strip()
                .lower()
                != "y"
            ):
                return 0

    # 执行删除操作
    deleted_count = 0
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            deleted_count += 1
            print(f"已删除: {file_path}")
        except Exception as e:
            print(f"{Fore.RED}删除文件 {file_path} 时出错: {str(e)}{Style.RESET_ALL}")

    return deleted_count


def find_image_files(folder_path):
    """递归查找所有图片文件"""
    image_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
    image_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(root, file))

    return image_files


def find_markdown_files(folder_path):
    """递归查找所有Markdown文件"""
    markdown_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".md", ".markdown")):
                markdown_files.append(os.path.join(root, file))

    return markdown_files


def show_introduction():
    """脚本介绍"""
    print(f"\n{Fore.CYAN}=== Blog-Webp-Assistant v{VERSION} ==={Style.RESET_ALL}")
    print(f"作者：{AUTHOR}")
    print(f"项目地址：{PROJECT_URL}\n")

    print(f"\n{Fore.YELLOW}转换实现：{Style.RESET_ALL}")
    print("使用 Pillow 库进行图片转换")
    print("支持有损和无损转换")
    print("支持自定义压缩质量")

    print(f"\n{Fore.YELLOW}功能说明：{Style.RESET_ALL}")
    print("1. 将图片批量转换为 webp 格式")
    print("2. 自动处理 Markdown 文件中的图片引用")
    print("3. 支持多种图片引用格式：")
    print("   - Markdown 标准格式 ![alt](image.jpg)")
    print("   - HTML 格式 <img src='image.jpg'>")
    print('   - 简和主题的 Hugo Shortcode {{< imgrow "image.jpg" >}}')
    print("   - 直接引用（文件名形式的图片引用，这个需要格外注意）")

    print(f"\n{Fore.YELLOW}直接引用检测说明：{Style.RESET_ALL}")
    print("脚本会检测文本中的图片文件名")
    print("不过仅在对应的 webp 文件存在时才会替换")
    print('如：文中的 "555.jpg" 只有在同目录下存在 "555.webp" 时才会被替换')

    print(f"\n{Fore.YELLOW}可能存在的风险：{Style.RESET_ALL}")
    print("1. 图片质量：")
    print("   - 有损压缩导致图片质量下降")
    print("   - 特殊图片建议使用无损压缩")
    print("2. 文件替换：")
    print("   - 转换过程会生成新文件")
    print("   - 对原始文件的操作不可逆")
    print("3. Markdown 修改：")
    print("   - 会修改 Markdown 文件内容")
    print("   - 虽然极力避免，但仍可能会错误识别到文本中的图片文件名")

    print(f"\n{Fore.YELLOW}所以请：{Style.RESET_ALL}")
    print("1. 开始使用前先手动备份一份，不要过度依赖脚本的自动备份")
    print("2. 重要图片建议使用无损压缩，或者不要转换，可通过挨个确认模式避免")
    print("3. 删除原始文件前确保 webp 文件可正常使用，原始文件也建议备份保留")

    input(
        f"\n{Fore.GREEN}确认理解风险并已完成手动备份，按回车键继续...{Style.RESET_ALL}"
    )


def show_menu():
    """显示主菜单"""
    print(f"\n{Fore.CYAN}=== Blog-Webp-Assistant v{VERSION} ==={Style.RESET_ALL}")
    print(f"作者：{AUTHOR}")
    print(f"项目地址：{PROJECT_URL}\n")
    print("1. 转换图片为 Webp 格式")
    print("2. 更新 Markdown 中的图片引用")
    print("3. 执行完整流程（转换 + 更新引用）")
    print("4. 删除已转换图片的原始文件")
    print("0. 退出")
    choice = input("\n请选择操作 (0-4): ").strip()
    return choice


def show_warning():
    """显示警告信息"""
    print(f"\n{Fore.RED}警告！{Style.RESET_ALL}")
    print(
        f"{Fore.RED}1. 此脚本的操作会修改、替换、删除您的文件，请确保数据已备份{Style.RESET_ALL}"
    )
    print(f"{Fore.RED}2. 脚本处于调试阶段，缺乏测试，请勿过度依赖{Style.RESET_ALL}")
    print(f"{Fore.RED}3. 数据无价，请谨慎操作，一定要备份！！！{Style.RESET_ALL}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(script_dir, "backup")
    print(f"\n{Fore.YELLOW}备份将保存在: {backup_dir}{Style.RESET_ALL}")

    backup_response = (
        input(f"\n{Fore.YELLOW}是否需要创建备份？(y/n，默认y): {Style.RESET_ALL}")
        .strip()
        .lower()
    )
    return backup_response != "n"


def backup_files_to_delete(folder_path, files_to_delete):
    """备份即将删除的文件
    Args:
        folder_path: 原始文件夹路径
        files_to_delete: 要删除的文件列表
    Returns:
        backup_path: 备份文件夹路径
    """
    try:
        # 创建backup文件夹
        script_dir = os.path.dirname(os.path.abspath(__file__))
        backup_dir = os.path.join(script_dir, "backup")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # 使用时间戳创建唯一的备份文件夹
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"deleted_files_backup_{timestamp}")

        # 创建备份目录结构
        for file_path in files_to_delete:
            # 获取相对路径
            rel_path = os.path.relpath(file_path, folder_path)
            # 构建备份路径
            backup_file_path = os.path.join(backup_path, rel_path)
            # 创建目录结构
            os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
            # 复制文件
            shutil.copy2(file_path, backup_file_path)

        print(f"\n{Fore.GREEN}已备份要删除的文件到: {backup_path}{Style.RESET_ALL}")
        return backup_path
    except Exception as e:
        print(f"\n{Fore.RED}备份要删除的文件时出错: {str(e)}{Style.RESET_ALL}")
        return None


def replace_image_references(markdown_path, need_confirm=True):
    """替换Markdown文件中的图片引用为webp格式
    Args:
        markdown_path: Markdown文件路径
        need_confirm: 是否需要逐个确认替换
    """
    try:
        with open(markdown_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 分离YAML前置元数据和正文内容
        yaml_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            main_content = content[yaml_match.end() :]

            # 处理YAML中的图片引用
            yaml_changed = False
            try:
                yaml_data = yaml.safe_load(yaml_content)
                if yaml_data and isinstance(yaml_data, dict):
                    # 检查并更新image字段
                    if "image" in yaml_data:
                        img_path = yaml_data["image"]
                        if isinstance(img_path, str):
                            base_name = os.path.splitext(img_path)[0]
                            ext = os.path.splitext(img_path)[1].lower()
                            if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
                                webp_path = base_name + ".webp"
                                if os.path.exists(
                                    os.path.join(
                                        os.path.dirname(markdown_path), webp_path
                                    )
                                ):
                                    print(f"\n处理文件: {markdown_path}")
                                    print(f"在YAML中发现图片引用: {img_path}")
                                    print(f"可替换为: {webp_path}")
                                    if need_confirm:
                                        response = (
                                            input("是否替换？(y/n/gg，默认n): ")
                                            .strip()
                                            .lower()
                                        )
                                        if response == "gg":
                                            need_confirm = False
                                            content = content.replace(
                                                img_path, webp_path
                                            )
                                            yaml_changed = True
                                            print(
                                                f"{Fore.YELLOW}切换到自动替换模式{Style.RESET_ALL}"
                                            )
                                        elif response == "y":
                                            content = content.replace(
                                                img_path, webp_path
                                            )
                                            yaml_changed = True
                                    else:
                                        # 自动批处理模式，直接替换
                                        content = content.replace(img_path, webp_path)
                                        yaml_changed = True
                                        print(
                                            f"{Fore.GREEN}已自动替换{Style.RESET_ALL}"
                                        )
            except yaml.YAMLError:
                print(f"处理 {markdown_path} 的YAML数据时出错")
        else:
            yaml_content = ""
            main_content = content
            yaml_changed = False

        # 处理正文中的图片引用
        # 匹配各种图片引用格式
        img_patterns = [
            (
                r"!\[([^\]]*?)\]\(([^)]+?)\)",
                "Markdown格式",
            ),  # Markdown 标准格式 ![alt](path)
            (r"<img.*?src=[\'\"](.*?)[\'\"]", "HTML格式"),  # HTML 格式 <img src="path">
            (
                r'(?:\"|\s)([^"\s]+\.(?:jpg|jpeg|png|bmp|tiff))(?:\"|\s|$)',
                "直接引用",
            ),  # 裸露的图片路径，包括引号包围的情况
            (
                r'{{<\s*(?:imgrow|music)\s+(?:[^>}]*?\s+)?(?:img=)?\"([^"]+\.(?:jpg|jpeg|png|bmp|tiff))\"',
                "Hugo Shortcode",
            ),  # Hugo shortcode中的img属性
            (r"{{<\s*imgrow\s+([^>}]*?)>}}", "Hugo Imgrow"),  # Hugo imgrow shortcode
        ]

        def process_image_path(img_path, md_dir):
            """处理图片路径，检查是否存在对应的webp文件"""
            if not img_path:
                return None

            # 移除URL参数
            # img_path = img_path.split('?')[0]

            # 检查文件扩展名
            ext = os.path.splitext(img_path)[1].lower()
            if ext not in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
                return None

            # 构建webp路径
            base_path = os.path.splitext(img_path)[0]
            webp_path = base_path + ".webp"

            # 检查webp文件是否存在
            full_webp_path = (
                os.path.join(md_dir, webp_path)
                if not os.path.isabs(webp_path)
                else webp_path
            )
            if os.path.exists(full_webp_path):
                return webp_path
            return None

        def process_imgrow_shortcode(content):
            """处理 Hugo imgrow shortcode 中的所有图片引用"""
            pattern = r'\"([^"]+\.(?:jpg|jpeg|png|bmp|tiff))\"'
            matches = []

            def collect_matches(match):
                img_path = match.group(1)
                matches.append((img_path, match.start(1), match.end(1)))
                return match.group(0)

            re.sub(pattern, collect_matches, content)
            return matches

        def replace_match(pattern_info, content, md_dir):
            pattern, pattern_type = pattern_info
            replacements = []
            nonlocal need_confirm

            def get_context(content, start_pos, end_pos):
                """获取替换位置的上下文"""
                context_start = max(0, start_pos - 5)
                context_end = min(len(content), end_pos + 5)
                before = content[context_start:start_pos]
                after = content[end_pos:context_end]
                return before, after

            def collect_replacement(match):
                if pattern_type == "Hugo Imgrow":
                    # 处理整个 imgrow shortcode
                    shortcode_content = match.group(1)
                    img_matches = process_imgrow_shortcode(shortcode_content)

                    for img_path, start, end in img_matches:
                        webp_path = process_image_path(img_path, md_dir)
                        if webp_path:
                            # 计算在原始内容中的位置
                            abs_start = match.start(1) + start
                            abs_end = match.start(1) + end
                            before, after = get_context(content, abs_start, abs_end)
                            replacements.append(
                                (
                                    img_path,
                                    webp_path,
                                    img_path,
                                    webp_path,
                                    (before, after),
                                    "Hugo Imgrow内图片",
                                )
                            )
                    return match.group(0)
                elif pattern_type in ["Markdown格式", "HTML格式", "Hugo Shortcode"]:
                    img_path = (
                        match.group(2)
                        if pattern_type == "Markdown格式"
                        else match.group(1)
                    )
                    webp_path = process_image_path(img_path, md_dir)
                    if webp_path:
                        if pattern_type == "Markdown格式":
                            new_text = f"![{match.group(1)}]({webp_path})"
                        elif pattern_type == "HTML格式":
                            new_text = match.group(0).replace(img_path, webp_path)
                        else:  # Hugo Shortcode
                            new_text = match.group(0).replace(img_path, webp_path)
                        replacements.append(
                            (
                                match.group(0),
                                new_text,
                                img_path,
                                webp_path,
                                None,
                                pattern_type,
                            )
                        )
                else:  # 直接引用
                    img_path = match.group(1)
                    webp_path = process_image_path(img_path, md_dir)
                    if webp_path:
                        before, after = get_context(
                            content, match.start(1), match.end(1)
                        )
                        replacements.append(
                            (
                                img_path,
                                webp_path,
                                img_path,
                                webp_path,
                                (before, after),
                                "直接引用",
                            )
                        )
                return match.group(0)

            # 先收集所有可能的替换
            re.sub(pattern, collect_replacement, content)

            # 如果有可替换项
            if replacements:
                # 检查是否有直接引用的情况
                has_direct_refs = any(
                    r[5] in ["直接引用", "Hugo Imgrow内图片"] for r in replacements
                )  # Imgrow 是我主题的shortcode 用来展示图片的

                # 如果不需要逐个确认且有直接引用，先显示示例
                if not need_confirm and has_direct_refs:
                    print(
                        f"\n{Fore.YELLOW}发现直接引用或Hugo Shortcode中的图片路径，这种情况需要特别注意！{Style.RESET_ALL}"
                    )
                    print(
                        f"\n{Fore.YELLOW}注意：只有当文件夹中存在对应的webp文件时，才会进行替换。{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.YELLOW}例如：如果文中有 555.jpg 这样的假装有表情包的表达，但文件夹中没有 555.webp ，则不会被替换。{Style.RESET_ALL}"
                    )
                    print("\n这些引用可能出现在文本中或Hugo Shortcode中，例如：")

                    # 示例
                    example_shown = False
                    for old, new, old_path, new_path, context, ref_type in replacements:
                        if ref_type in ["直接引用", "Hugo Imgrow内图片"]:
                            before, after = context
                            print(f"\n类型：{ref_type}")
                            print(
                                f"上下文示例：...{before}{Fore.RED}{old_path}{Style.RESET_ALL}{after}..."
                            )
                            print(
                                f"将替换为：...{before}{Fore.GREEN}{new_path}{Style.RESET_ALL}{after}..."
                            )
                            print(
                                f"{Fore.GREEN}（已确认存在对应的webp文件）{Style.RESET_ALL}"
                            )
                            example_shown = True
                            break

                    if example_shown:
                        response = (
                            input("\n是否要替换这些图片路径？(y/n): ").strip().lower()
                        )
                        if response != "y":
                            # 移除所有直接引用的替换
                            replacements = [
                                r
                                for r in replacements
                                if r[5] not in ["直接引用", "Hugo Imgrow内图片"]
                            ]
                        else:
                            # 保险
                            confirm_response = (
                                input("是否要逐个确认这些替换？(y/n): ").strip().lower()
                            )
                            if confirm_response == "y":
                                need_confirm = True

                # 处理所有替换
                if replacements:
                    print(f"\n在{pattern_type}中发现以下可替换项：")
                    for old, new, old_path, new_path, context, ref_type in replacements:
                        print(f"\n[{ref_type}] 发现图片引用:")
                        if ref_type in ["直接引用", "Hugo Imgrow内图片"]:
                            before, after = context
                            print(
                                f"上下文：...{before}{Fore.RED}{old_path}{Style.RESET_ALL}{after}..."
                            )
                            print(
                                f"替换为：...{before}{Fore.GREEN}{new_path}{Style.RESET_ALL}{after}..."
                            )
                            print(
                                f"{Fore.GREEN}（已确认存在对应的webp文件）{Style.RESET_ALL}"
                            )
                        else:
                            print(f"原始引用: {old_path}")
                            print(f"替换为: {new_path}")

                        if need_confirm:
                            response = (
                                input("是否替换？(y/n/gg，默认n): ").strip().lower()
                            )
                            if response == "gg":
                                need_confirm = False
                                content = content.replace(old, new)
                                print(
                                    f"{Fore.YELLOW}切换到自动替换模式{Style.RESET_ALL}"
                                )
                            elif response == "y":
                                content = content.replace(old, new)
                        else:
                            # 自动批处理模式，直接替换
                            content = content.replace(old, new)
                            print(f"{Fore.GREEN}已自动替换{Style.RESET_ALL}")

            return content, bool(replacements)

        # 获取markdown文件所在目录
        md_dir = os.path.dirname(markdown_path)

        # 处理所有图片引用模式
        main_content = content[yaml_match.end() :] if yaml_match else content
        content_changed = False

        for pattern_info in img_patterns:
            new_main_content, changed = replace_match(
                pattern_info, main_content, md_dir
            )
            if changed:
                main_content = new_main_content
                content_changed = True

        # 如果有任何修改，保存文件
        if content_changed or yaml_changed:
            if yaml_match:
                final_content = content[: yaml_match.end()] + main_content
            else:
                final_content = main_content

            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(final_content)
            return True
        return False
    except Exception as e:
        print(f"处理Markdown文件 {markdown_path} 时出错: {str(e)}")
        return False


def convert_to_webp(image_path, lossless=False, need_confirm=True, quality=80):
    """将图片转换为webp格式
    Args:
        image_path: 图片路径
        lossless: 是否使用无损压缩
        need_confirm: 是否需要确认覆盖
        quality: 压缩质量(1-100)
    """
    try:
        # 构建输出文件路径
        output_path = os.path.splitext(image_path)[0] + ".webp"

        # 检查是否已存在同名webp文件
        if os.path.exists(output_path):
            if need_confirm:
                response = (
                    input(f"\n文件 {output_path} 已存在，是否覆盖？(y/n/gg，默认n): ")
                    .strip()
                    .lower()
                )
                if response == "gg":
                    return "gg"
                if response != "y":
                    print("跳过该文件")
                    return False

        # 转换图片
        image = Image.open(image_path)
        if lossless:
            image.save(output_path, "webp", lossless=True)
        else:
            image.save(output_path, "webp", quality=quality)
        return True
    except Exception as e:
        print(f"{Fore.RED}转换 {image_path} 时出错: {str(e)}{Style.RESET_ALL}")
        return False


def process_images(folder_path):
    """处理图片转换"""
    image_files = find_image_files(folder_path)
    if not image_files:
        print(f"{Fore.YELLOW}未找到任何图片文件！{Style.RESET_ALL}")
        return False

    print(f"\n找到 {len(image_files)} 个图片文件。")
    print("\n文件列表:")
    for file in image_files:
        print(file)

    response = input("\n是否将这些图片转换为webp格式？(y/n): ").strip().lower()
    if response != "y":
        print("操作已取消。")
        return False

    lossless_response = input("\n是否使用无损压缩？(y/n): ").strip().lower()
    use_lossless = lossless_response == "y"

    quality = 80  # 默认质量
    if not use_lossless:
        print("\n将使用有损压缩模式")
        quality_input = input(
            f"请输入压缩质量(1-100，默认{quality}，直接回车使用默认值): "
        ).strip()
        if quality_input:
            try:
                quality = int(quality_input)
                if quality < 1 or quality > 100:
                    print(
                        f"{Fore.YELLOW}输入的质量值无效，将使用默认值 80{Style.RESET_ALL}"
                    )
                    quality = 80
            except ValueError:
                print(
                    f"{Fore.YELLOW}输入的质量值无效，将使用默认值 80{Style.RESET_ALL}"
                )
        print(f"将使用压缩质量: {quality}（文件体积较小但质量可能损失）")
    else:
        print("\n将使用无损压缩模式（文件体积较大但质量无损）")

    # 保险
    need_confirm = (
        input(
            f"\n{Fore.YELLOW}是否需要逐个确认覆盖已存在的文件？(y/n): {Style.RESET_ALL}"
        )
        .strip()
        .lower()
        == "y"
    )
    if not need_confirm:
        print("\n将自动覆盖所有已存在的文件")
    else:
        print("\n处理过程中可以输入 'gg' 来切换到自动覆盖模式")

    converted_count = 0
    existing_count = 0

    print("\n开始转换...")
    for image_path in image_files:
        result = convert_to_webp(
            image_path,
            lossless=use_lossless,
            need_confirm=need_confirm,
            quality=quality,
        )
        if result == "gg":
            print(f"\n{Fore.YELLOW}切换到自动覆盖模式{Style.RESET_ALL}")
            need_confirm = False
            # 使用自动模式
            if convert_to_webp(
                image_path, lossless=use_lossless, need_confirm=False, quality=quality
            ):
                converted_count += 1
                print(f"已转换: {image_path}")
            else:
                existing_count += 1
        elif result:
            converted_count += 1
            print(f"已转换: {image_path}")
        else:
            existing_count += 1

    print(f"\n{Fore.GREEN}转换完成！{Style.RESET_ALL}")
    print(f"成功转换: {converted_count} 个文件")
    if existing_count > 0:
        print(f"跳过 {existing_count} 个文件")
    return True


def process_markdown(folder_path):
    """处理Markdown文件"""
    markdown_files = find_markdown_files(folder_path)
    if not markdown_files:
        print("未找到任何Markdown文件！")
        return False

    print(f"\n找到 {len(markdown_files)} 个Markdown文件")

    # 询问是否需要逐个确认替换
    need_confirm = input("\n是否需要逐个确认替换？(y/n): ").strip().lower() == "y"
    if need_confirm:
        print("\n将逐个确认替换")
    else:
        print("\n将自动替换所有可替换的图片引用")

    updated_count = 0

    print("\n开始更新Markdown文件...")
    for md_file in markdown_files:
        if replace_image_references(md_file, need_confirm):
            updated_count += 1
            print(f"已更新: {md_file}")

    print("\nMarkdown处理完成！")
    print(f"已更新 {updated_count} 个文件中的图片引用")
    return True


def main():
    show_introduction()

    while True:
        choice = show_menu()
        if choice == "0":
            print("\n感谢使用！")
            print(
                f"\n{Fore.CYAN}如果有幸帮助到您，也欢迎您到 {Style.BRIGHT}{PROJECT_URL}{Style.RESET_ALL} 点个Star ⭐ v ⭐，感谢"
            )
            break

        if choice not in ["1", "2", "3", "4"]:
            print(f"{Fore.RED}无效的选择，请重试！{Style.RESET_ALL}")
            continue

        folder_path = input("\n请输入要处理的文件夹路径: ").strip()
        if not os.path.exists(folder_path):
            print(f"{Fore.RED}输入的文件夹路径不存在！{Style.RESET_ALL}")
            continue

        # 一定要备份啊 T-T
        if show_warning():
            backup_path = create_backup(folder_path)
            if not backup_path:
                continue
        else:
            print(
                f"\n{Fore.YELLOW}您选择了不创建备份，请自行承担数据丢失风险！！{Style.RESET_ALL}"
            )
            if input("确定要继续吗？(y/n): ").strip().lower() != "y":
                continue

        if choice in ["1", "3"]:
            process_images(folder_path)

        if choice in ["2", "3"]:
            process_markdown(folder_path)

        if choice == "4":
            print(f"\n{Fore.YELLOW}删除说明：{Style.RESET_ALL}")
            print(
                "1. 脚本会在指定文件夹中搜索所有图片文件（jpg、png、jpeg、bmp、tiff）"
            )
            print("2. 检查每个图片是否存在同名的 webp 文件")
            print("   例如：对于 image.jpg，检查是否存在 image.webp")
            print(
                "3. 如果找到同名的 webp 文件，则将原始图片（如 image.jpg）加入删除列表"
            )
            print("4. 删除操作不可逆，建议先进行备份")

            if (
                input(f"\n{Fore.RED}您确定要继续删除操作吗？(y/n): {Style.RESET_ALL}")
                .strip()
                .lower()
                == "y"
            ):
                deleted_count = delete_original_images(folder_path)
                print(f"\n删除完成！共删除 {deleted_count} 个原始图片文件")
            else:
                print("操作已取消")


if __name__ == "__main__":
    main()
