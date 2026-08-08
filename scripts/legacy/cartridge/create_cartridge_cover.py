#!/usr/bin/env python3
import os
import math
from PIL import Image, ImageDraw, ImageFont

def create_gameboy_sticker(
    input_artwork_path="assets/copertina.png",
    output_path="assets/cartridge_cover.png",
    width=1008,
    height=888
):
    # 1. Canvas creation (RGBA)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    # 2. Metallic silver background with gradient
    bg = Image.new("RGBA", (width, height), (225, 227, 230, 255))
    draw_bg = ImageDraw.Draw(bg)
    
    # Vertical gradient + metallic shine
    for y in range(height):
        shade = int(218 + 22 * math.sin(y / height * math.pi * 1.4))
        if 35 <= y <= 165:
            shade = min(255, shade + int(18 * math.sin((y - 35) / 130 * math.pi)))
        draw_bg.line([(0, y), (width, y)], fill=(shade, shade, shade + 4, 255))
    
    # 3. Outer DMG sticker mask (rounded corners + top-left notch cutout)
    mask = Image.new("L", (width, height), 0)
    draw_mask = ImageDraw.Draw(mask)
    
    corner_radius = 28
    notch_w = 115
    notch_h = 105
    
    # Draw main rounded rectangle
    draw_mask.rounded_rectangle([(0, 0), (width - 1, height - 1)], radius=corner_radius, fill=255)
    
    # Notch out top-left corner
    draw_mask.rectangle([(0, 0), (notch_w, notch_h)], fill=0)
    notch_radius = 16
    draw_mask.rounded_rectangle([(notch_w, 0), (width - 1, height - 1)], radius=corner_radius, fill=255)
    draw_mask.rounded_rectangle([(0, notch_h), (width - 1, height - 1)], radius=corner_radius, fill=255)
    draw_mask.rounded_rectangle([(notch_w - notch_radius*2, notch_h), (notch_w, notch_h + notch_radius*2)], radius=notch_radius, fill=255)
    
    # 4. Header Bar: Nintendo GAME BOY branding
    header = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_header = ImageDraw.Draw(header)
    
    # Dark separator bar under header at y = 168..175
    draw_header.rectangle([(0, 168), (width, 172)], fill=(25, 28, 35, 255))
    draw_header.rectangle([(0, 172), (width, 175)], fill=(170, 175, 182, 255))
    
    # Fonts
    font_large_path = "/usr/share/fonts/open-sans/OpenSans-BoldItalic.ttf"
    font_bold_path = "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Bold.ttf"
    font_mono_path = "/usr/share/fonts/liberation-mono-fonts/LiberationMono-Bold.ttf"
    
    font_gb = ImageFont.truetype(font_large_path, 54)
    font_nintendo = ImageFont.truetype(font_bold_path, 34)
    font_serial = ImageFont.truetype(font_mono_path, 22)
    font_bottom = ImageFont.truetype(font_bold_path, 22)
    font_tiny = ImageFont.truetype(font_bold_path, 16)

    # Nintendo logo & GAME BOY header placement
    nintendo_x = notch_w + 35
    nintendo_y = 58
    
    draw_header.text((nintendo_x, nintendo_y), "Nintendo", fill=(20, 50, 150, 255), font=font_nintendo)
    
    gb_x = nintendo_x + 165
    gb_y = 44
    draw_header.text((gb_x, gb_y), "GAME BOY", fill=(18, 45, 145, 255), font=font_gb)
    draw_header.text((gb_x + 315, gb_y + 12), "TM", fill=(18, 45, 145, 255), font=font_tiny)
    
    # 5. Main Artwork Frame & Scaling
    if os.path.exists(input_artwork_path):
        art_src = Image.open(input_artwork_path).convert("RGBA")
    else:
        art_src = Image.new("RGBA", (800, 800), (20, 20, 25, 255))

    frame_x1, frame_y1 = 65, 185
    frame_x2, frame_y2 = width - 65, height - 68
    frame_w = frame_x2 - frame_x1
    frame_h = frame_y2 - frame_y1
    
    # Outer dark bezel frame around artwork
    draw_bg.rounded_rectangle([(frame_x1 - 6, frame_y1 - 6), (frame_x2 + 6, frame_y2 + 6)], radius=18, fill=(15, 15, 20, 255))
    draw_bg.rounded_rectangle([(frame_x1 - 2, frame_y1 - 2), (frame_x2 + 2, frame_y2 + 2)], radius=14, fill=(45, 48, 55, 255))
    
    # Fit artwork entirely into frame without clipping top text (contain scaling)
    art_w, art_h = art_src.size
    scale = min(frame_w / art_w, frame_h / art_h)
    new_w = int(art_w * scale)
    new_h = int(art_h * scale)
    
    art_resized = art_src.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Create black canvas inside frame to pad background if needed
    art_frame_bg = Image.new("RGBA", (frame_w, frame_h), (10, 10, 12, 255))
    paste_x = (frame_w - new_w) // 2
    paste_y = (frame_h - new_h) // 2
    art_frame_bg.paste(art_resized, (paste_x, paste_y), art_resized)
    
    # Create rounded mask for artwork inner frame
    art_mask = Image.new("L", (frame_w, frame_h), 0)
    ImageDraw.Draw(art_mask).rounded_rectangle([(0, 0), (frame_w, frame_h)], radius=12, fill=255)
    
    # Paste artwork frame onto background
    bg.paste(art_frame_bg, (frame_x1, frame_y1), art_mask)
    
    # 6. Overlay Details & Badges
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # Left vertical text: DMG-ASFD-EUR
    serial_txt = "DMG-ASFD-EUR"
    bbox_s = font_serial.getbbox(serial_txt)
    sw = bbox_s[2] - bbox_s[0]
    sh = bbox_s[3] - bbox_s[1]
    
    serial_img = Image.new("RGBA", (sw + 10, sh + 10), (0, 0, 0, 0))
    ImageDraw.Draw(serial_img).text((5, 2), serial_txt, fill=(45, 48, 55, 255), font=font_serial)
    serial_rot = serial_img.rotate(90, expand=True)
    overlay.paste(serial_rot, (20, frame_y1 + 50), serial_rot)
    
    # Official Nintendo Seal of Quality Badge on bottom-right of artwork
    seal_cx, seal_cy = frame_x2 - 75, frame_y2 - 70
    seal_r = 50
    
    # Gold starburst seal circle
    draw_overlay.ellipse([(seal_cx - seal_r, seal_cy - seal_r), (seal_cx + seal_r, seal_cy + seal_r)], fill=(238, 204, 90, 255), outline=(200, 160, 40, 255), width=3)
    draw_overlay.ellipse([(seal_cx - seal_r + 5, seal_cy - seal_r + 5), (seal_cx + seal_r - 5, seal_cy + seal_r - 5)], fill=(255, 255, 255, 255), outline=(220, 180, 50, 255), width=2)
    
    # Seal text
    draw_overlay.text((seal_cx - 26, seal_cy - 22), "Official", fill=(130, 95, 15, 255), font=font_tiny)
    draw_overlay.text((seal_cx - 33, seal_cy - 5), "Nintendo", fill=(18, 45, 145, 255), font=font_tiny)
    draw_overlay.text((seal_cx - 42, seal_cy + 10), "Seal of Quality", fill=(130, 95, 15, 255), font=ImageFont.truetype(font_bold_path, 11))

    # Bottom margin text: ▲ THIS SIDE OUT ▲
    bottom_txt = "▲  THIS SIDE OUT  ▲"
    bbox_b = font_bottom.getbbox(bottom_txt)
    txt_w = bbox_b[2] - bbox_b[0]
    draw_overlay.text(((width - txt_w) // 2, height - 46), bottom_txt, fill=(65, 70, 78, 255), font=font_bottom)
    
    # 7. Combine layers and apply outer DMG mask
    final_img = Image.alpha_composite(bg, header)
    final_img = Image.alpha_composite(final_img, overlay)
    
    # Apply outer cutout mask
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    result.paste(final_img, (0, 0), mask)
    
    # Save output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.save(output_path, "PNG")
    print(f"[SUCCESS] Created Game Boy cartridge sticker: {output_path} ({width}x{height} px)")

if __name__ == "__main__":
    create_gameboy_sticker()
