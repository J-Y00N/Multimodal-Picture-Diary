from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("assets/fonts/MaruBuri-Regular.ttf"),
        Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
        Path("/System/Library/Fonts/Supplemental/AppleGothic.ttf"),
        Path("/System/Library/Fonts/Supplemental/NotoSansCJK.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = list(text.replace("\r", ""))
    lines: list[str] = []
    current = ""
    for token in words:
        if token == "\n":
            if current:
                lines.append(current)
                current = ""
            lines.append("")
            continue
        candidate = current + token
        bbox = draw.textbbox((0, 0), candidate, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = token
    if current:
        lines.append(current)
    return lines


def _draw_wrapped_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    x: int,
    y: int,
    max_width: int,
    max_lines: int,
    line_height: int,
    fill,
) -> int:
    lines = _wrap_text(draw, text, font, max_width=max_width)
    for line in lines[:max_lines]:
        draw.text((x, y), line, fill=fill, font=font)
        y += line_height
    if len(lines) > max_lines:
        draw.text((x, y), "...", fill=fill, font=font)
        y += line_height
    return y


def _draw_label_chip(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    draw.rounded_rectangle(
        (x, y, x + width + 28, y + height + 16),
        radius=18,
        fill=(236, 228, 212),
        outline=(214, 205, 190),
    )
    draw.text((x + 14, y + 8), text, fill=(92, 82, 70), font=font)


def _paste_rounded_image(canvas: Image.Image, image: Image.Image, x: int, y: int, radius: int) -> None:
    rounded = image.convert("RGBA")
    mask = Image.new("L", rounded.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, rounded.width, rounded.height), radius=radius, fill=255)
    canvas.paste(rounded, (x, y), mask)


def compose_diary_page(
    diary_text: str,
    generated_image: Image.Image,
    prompt: str,
    *,
    show_prompt_notes: bool = False,
) -> Image.Image:
    canvas = Image.new("RGB", (1080, 1520), color=(248, 243, 232))
    draw = ImageDraw.Draw(canvas)

    title_font = _load_font(42)
    body_font = _load_font(28)
    meta_font = _load_font(20)
    section_font = _load_font(30)

    draw.rounded_rectangle((40, 40, 1040, 1480), radius=28, fill=(255, 252, 246), outline=(214, 205, 190), width=2)
    draw.rounded_rectangle((64, 58, 330, 142), radius=28, fill=(240, 231, 216))

    draw.text((88, 76), "Picture Diary", fill=(38, 36, 32), font=title_font)
    draw.text((88, 122), datetime.now().strftime("%Y-%m-%d"), fill=(104, 96, 86), font=meta_font)

    framed = generated_image.copy().convert("RGB")
    framed.thumbnail((920, 680))
    img_x = (1080 - framed.width) // 2
    image_y = 178
    draw.rounded_rectangle(
        (img_x - 12, image_y - 12, img_x + framed.width + 12, image_y + framed.height + 12),
        radius=30,
        fill=(239, 231, 216),
    )
    _paste_rounded_image(canvas, framed, img_x, image_y, radius=22)

    chip_y = image_y + framed.height + 18
    _draw_label_chip(draw, 72, chip_y, "Diary Memory", meta_font)
    _draw_label_chip(draw, 240, chip_y, "Generated Illustration", meta_font)

    text_y = image_y + framed.height + 56
    draw.line((72, text_y + 12, 1008, text_y + 12), fill=(222, 214, 200), width=2)
    draw.text((72, text_y + 26), "Diary", fill=(38, 36, 32), font=section_font)
    diary_block_top = text_y + 76
    diary_block_bottom = 1420 if not show_prompt_notes else 1210
    draw.rounded_rectangle(
        (60, diary_block_top - 12, 1020, diary_block_bottom),
        radius=24,
        fill=(251, 248, 242),
    )
    y = _draw_wrapped_block(
        draw,
        diary_text.strip(),
        body_font,
        x=84,
        y=diary_block_top + 12,
        max_width=912,
        max_lines=12 if not show_prompt_notes else 8,
        line_height=42,
        fill=(48, 44, 39),
    )

    if show_prompt_notes:
        prompt_block_y = max(y + 28, 1228)
        draw.rounded_rectangle(
            (60, prompt_block_y, 1020, min(prompt_block_y + 180, 1450)),
            radius=24,
            fill=(244, 238, 229),
        )
        draw.text((84, prompt_block_y + 20), "Prompt Notes", fill=(38, 36, 32), font=section_font)
        _draw_wrapped_block(
            draw,
            prompt.strip(),
            meta_font,
            x=84,
            y=prompt_block_y + 66,
            max_width=912,
            max_lines=3,
            line_height=28,
            fill=(104, 96, 86),
        )
    return canvas
