"""PDF generator for MP Suvidha: Madhya Pradesh Digital Services Portal.
Supports real Unicode Devanagari (Hindi) and English typography, genuine QR code generation,
and professional executive layout using Pillow and qrcode.
"""
import io
import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import qrcode

ROOT_DIR = Path(__file__).resolve().parent.parent

def get_unicode_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Attempts to load a Devanagari-compatible Unicode TrueType font, with graceful cross-platform fallbacks."""
    candidate_paths = [
        r"C:\Windows\Fonts\Nirmala.ttc",
        r"C:\Windows\Fonts\nirmala.ttf",
        r"C:\Windows\Fonts\mangal.ttf",
        r"C:\Windows\Fonts\aparaj.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            try:
                # If TrueType collection (.ttc), index 0 is regular, 1 is bold
                index = 1 if (bold and path.lower().endswith(".ttc")) else 0
                return ImageFont.truetype(path, size=size, index=index)
            except Exception:
                try:
                    return ImageFont.truetype(path, size=size)
                except Exception:
                    pass
    return ImageFont.load_default()


def build_certificate_pdf(cert: dict) -> bytes:
    """Generates an executive, print-ready A4 demonstration certificate PDF

    with full Devanagari Hindi text rendering, official seal, borders, and a genuine scannable QR code.
    """
    # A4 Dimensions at 150 DPI
    width, height = 1240, 1754
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Load Fonts
    font_brand = get_unicode_font(34, bold=True)
    font_subbrand = get_unicode_font(20, bold=False)
    font_cert_title = get_unicode_font(28, bold=True)
    font_label = get_unicode_font(20, bold=True)
    font_val = get_unicode_font(20, bold=False)
    font_val_bold = get_unicode_font(22, bold=True)
    font_badge = get_unicode_font(16, bold=True)
    font_disclaimer = get_unicode_font(13, bold=False)
    font_disclaimer_bold = get_unicode_font(14, bold=True)

    # Color Palette
    navy = (18, 59, 99)
    royal = (23, 105, 170)
    saffron = (244, 163, 64)
    teal = (22, 140, 131)
    text_dark = (31, 41, 55)
    text_muted = (100, 116, 139)
    box_bg = (245, 248, 252)
    border_color = (226, 232, 240)

    # 1. Official Double Borders
    draw.rectangle([(24, 24), (width - 24, height - 24)], outline=navy, width=5)
    draw.rectangle([(34, 34), (width - 34, height - 34)], outline=saffron, width=2)
    draw.rectangle([(42, 42), (width - 42, height - 42)], outline=(235, 240, 248), width=1)

    # Corner Accents
    for cx, cy in [(42, 42), (width - 42, 42), (42, height - 42), (width - 42, height - 42)]:
        draw.rectangle([(cx - 8, cy - 8), (cx + 8, cy + 8)], fill=saffron)

    # 2. Portal Header
    logo_path = ROOT_DIR / "static" / "images" / "mp-suvidha-logo.png"
    y_top = 70
    if logo_path.is_file():
        try:
            logo_img = Image.open(logo_path).convert("RGBA")
            # Resize proportionally to height 70
            aspect = logo_img.width / logo_img.height
            new_w = int(70 * aspect)
            logo_resized = logo_img.resize((new_w, 70), Image.Resampling.LANCZOS)
            # Create white background for pasting
            temp_bg = Image.new("RGB", (new_w, 70), (255, 255, 255))
            temp_bg.paste(logo_resized, (0, 0), logo_resized)
            img.paste(temp_bg, ((width - new_w) // 2, y_top))
            y_top += 85
        except Exception:
            pass

    # Header Text
    draw.text((width // 2, y_top), "मध्य प्रदेश डिजिटल सेवाएँ · MP SUVIDHA", font=font_brand, fill=navy, anchor="mm")
    y_top += 38
    draw.text((width // 2, y_top), "Citizen Services Demonstration & Delivery Portal", font=font_subbrand, fill=text_muted, anchor="mm")
    y_top += 45

    # Decorative Badge Strip
    badge_text = "★ DEMONSTRATION RECORD · ई-सेवा सत्यापन प्रमाण पत्र ★"
    draw.rectangle([(width // 2 - 320, y_top - 16), (width // 2 + 320, y_top + 16)], fill=(238, 244, 255), outline=royal, width=1)
    draw.text((width // 2, y_top), badge_text, font=font_badge, fill=royal, anchor="mm")
    y_top += 55

    # Certificate Title
    draw.text((width // 2, y_top), "डिजिटल सेवा प्रमाण पत्र / E-CERTIFICATE", font=font_cert_title, fill=navy, anchor="mm")
    y_top += 30
    draw.line([(width // 2 - 200, y_top), (width // 2 + 200, y_top)], fill=saffron, width=3)
    y_top += 35

    # Extract Certificate Metadata
    applicant_name = cert.get("applicant_name") or "Aarav Sharma"
    service_name = cert.get("service_name") or "Public Service"
    department = cert.get("department") or "Public Administration"
    cert_number = cert.get("number") or "MPS-CERT-2026-00000"
    app_id = cert.get("application_id") or "MPS-2026-00000"
    issue_date = cert.get("issue_date") or "2026-11-12"
    status = cert.get("status") or "Valid"

    # 3. Main Data Card Box
    box_x0, box_y0 = 80, y_top
    box_x1, box_y1 = width - 80, y_top + 540
    draw.rectangle([(box_x0, box_y0), (box_x1, box_y1)], fill=box_bg, outline=border_color, width=2)
    # Accent top border
    draw.line([(box_x0, box_y0), (box_x1, box_y0)], fill=royal, width=4)

    fields = [
        ("Certificate Number (प्रमाण पत्र क्रमांक):", cert_number, True, navy),
        ("Application ID (आवेदन संदर्भ संख्या):", app_id, False, text_dark),
        ("Issued To (आवेदक का नाम):", applicant_name, True, navy),
        ("Service Name (सेवा का नाम):", service_name, True, royal),
        ("Department (संबद्ध विभाग):", department, False, text_dark),
        ("Date of Issue (जारी दिनांक):", issue_date, False, text_dark),
        ("Verification Status (सत्यापन स्थिति):", f"{status} (Demo Registered / सत्यापित)", True, teal),
    ]

    cur_y = box_y0 + 35
    for label, val, is_bold, color in fields:
        draw.text((box_x0 + 40, cur_y), label, font=font_label, fill=text_muted)
        val_font = font_val_bold if is_bold else font_val
        draw.text((box_x0 + 430, cur_y), val, font=val_font, fill=color)
        cur_y += 62
        draw.line([(box_x0 + 30, cur_y - 12), (box_x1 - 30, cur_y - 12)], fill=(230, 235, 245), width=1)

    y_bottom_section = box_y1 + 50

    # 4. QR Code Generation (Genuine Verification Engine)
    verify_url = f"http://127.0.0.1:5000/#verify?cert={cert_number}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=5,
        border=2,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=navy, back_color="white").convert("RGB")

    # Place QR Code on the Right
    qr_x = width - 80 - qr_img.width
    qr_y = y_bottom_section
    img.paste(qr_img, (qr_x, qr_y))
    draw.text((qr_x + qr_img.width // 2, qr_y + qr_img.height + 15), "Scan to Verify Online", font=font_badge, fill=navy, anchor="mm")
    draw.text((qr_x + qr_img.width // 2, qr_y + qr_img.height + 35), "सत्यापन हेतु स्कैन करें", font=font_disclaimer, fill=text_muted, anchor="mm")

    # 5. Security Watermark / Seal on the Left
    seal_x = 80
    seal_y = y_bottom_section + 10
    draw.ellipse([(seal_x, seal_y), (seal_x + 160, seal_y + 160)], outline=navy, width=3)
    draw.ellipse([(seal_x + 8, seal_y + 8), (seal_x + 152, seal_y + 152)], outline=saffron, width=2)
    draw.text((seal_x + 80, seal_y + 55), "MP SUVIDHA", font=font_label, fill=navy, anchor="mm")
    draw.text((seal_x + 80, seal_y + 85), "VERIFIED", font=font_label, fill=teal, anchor="mm")
    draw.text((seal_x + 80, seal_y + 115), "DEMO SEAL", font=font_badge, fill=text_muted, anchor="mm")

    # Signature / Authorized Text in Middle
    mid_x = 280
    draw.text((mid_x, y_bottom_section + 40), "Digitally Generated Demonstration Record", font=font_val_bold, fill=navy)
    draw.text((mid_x, y_bottom_section + 70), "Government Process Simulation Framework", font=font_subbrand, fill=royal)
    draw.text((mid_x, y_bottom_section + 100), f"Verification Reference: {cert_number}", font=font_badge, fill=text_muted)
    draw.text((mid_x, y_bottom_section + 125), "Issuance Node: Bhopal Central Data Gateway", font=font_badge, fill=text_muted)

    # 6. Official Demonstration Disclaimer (Both Languages)
    disc_box_y0 = height - 240
    disc_box_y1 = height - 55
    draw.rectangle([(80, disc_box_y0), (width - 80, disc_box_y1)], fill=(255, 251, 235), outline=(254, 215, 170), width=1)
    draw.line([(80, disc_box_y0), (width - 80, disc_box_y0)], fill=saffron, width=3)

    draw.text((105, disc_box_y0 + 20), "LEGAL DISCLAIMER & NOTIFICATION / वैधानिक अस्वीकरण:", font=font_disclaimer_bold, fill=(180, 83, 9))
    disc_en = (
        "1. This certificate is an informational digital demonstration generated on the MP Suvidha portal to illustrate citizen service delivery. "
        "It holds no statutory, legal, or administrative validity with the Government of Madhya Pradesh or any official department."
    )
    disc_hi = (
        "२. यह प्रमाण पत्र नागरिक सेवा वितरण प्रणाली के तकनीकी प्रदर्शन हेतु एमपी सुविधा पोर्टल द्वारा जनरेट किया गया है। "
        "यह मध्य प्रदेश शासन अथवा किसी सरकारी विभाग का आधिकारिक प्रमाण पत्र नहीं है और विधिक प्रयोजनों हेतु मान्य नहीं है।"
    )
    y_d = disc_box_y0 + 48
    for line in textwrap.wrap(disc_en, width=105):
        draw.text((105, y_d), line, font=font_disclaimer, fill=(120, 53, 15))
        y_d += 20
    y_d += 6
    for line in textwrap.wrap(disc_hi, width=105):
        draw.text((105, y_d), line, font=font_disclaimer, fill=(120, 53, 15))
        y_d += 20

    # Save to PDF buffer
    buf = io.BytesIO()
    img.save(buf, format="PDF", resolution=150.0)
    return buf.getvalue()


def build_evaluation_report_pdf(item: dict) -> bytes:
    """Generates an internal technical evaluation audit report PDF."""
    width, height = 1240, 1754
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_title = get_unicode_font(26, bold=True)
    font_head = get_unicode_font(18, bold=True)
    font_body = get_unicode_font(15, bold=False)
    font_mono = get_unicode_font(14, bold=True)

    navy = (18, 59, 99)
    royal = (23, 105, 170)
    text_dark = (31, 41, 55)

    # Simple Header
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=navy, width=3)
    draw.text((width // 2, 60), "E-GOVERNANCE PORTAL AUDIT & TECHNICAL ASSESSMENT", font=font_title, fill=navy, anchor="mm")
    draw.text((width // 2, 95), "MP Suvidha Internal System Evaluation Report", font=font_head, fill=royal, anchor="mm")
    draw.line([(60, 120), (width - 60, 120)], fill=(200, 210, 225), width=2)

    cur_y = 150
    draw.text((60, cur_y), f"Portal Name: {item.get('portal_name', 'N/A')}", font=font_head, fill=text_dark)
    cur_y += 30
    draw.text((60, cur_y), f"Evaluation Date: {item.get('evaluation_date', 'N/A')}", font=font_body, fill=text_dark)
    cur_y += 30
    draw.text((60, cur_y), f"Evaluator: {item.get('evaluator', 'System Auditor')}", font=font_body, fill=text_dark)
    cur_y += 40

    draw.text((60, cur_y), "Evaluation Parameter Scores (Scale 1 to 5):", font=font_head, fill=navy)
    cur_y += 30

    scores = item.get("scores") or {}
    for param, score in list(scores.items())[:10]:
        val = int(score) if str(score).isdigit() else 0
        stars = "★ " * val + "☆ " * (5 - val)
        draw.text((80, cur_y), f"- {param.ljust(30)} : {val}/5   {stars}", font=font_mono, fill=text_dark)
        cur_y += 26

    cur_y += 25
    sections = [
        ("Strengths:", item.get("strengths") or "High accessibility and fast service response."),
        ("Limitations:", item.get("limitations") or "Multi-step navigation barriers in rural regions."),
        ("Technical Recommendations:", item.get("recommendations") or "Expand mobile-first microservices and bilingual caching."),
    ]
    for h_txt, b_txt in sections:
        draw.text((60, cur_y), h_txt, font=font_head, fill=navy)
        cur_y += 28
        for line in textwrap.wrap(b_txt, width=95):
            draw.text((80, cur_y), line, font=font_body, fill=text_dark)
            cur_y += 24
        cur_y += 15

    buf = io.BytesIO()
    img.save(buf, format="PDF", resolution=150.0)
    return buf.getvalue()
