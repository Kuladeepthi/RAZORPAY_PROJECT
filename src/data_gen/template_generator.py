"""
SentinelEvidence — Base Document Template Generator (6 Distinct Templates)

Generates 6 realistic, high-resolution payment dispute evidence documents
representative of Indian e-commerce / payments ecosystem:
1. upi_gpay_01: Google Pay UPI Confirmation
2. upi_phonepe_02: PhonePe UPI Transaction Slip
3. gst_invoice_apex_01: Apex Retail Solutions Tax Invoice
4. gst_invoice_techmart_02: TechMart Electronics B2B Invoice
5. courier_bluedart_01: BlueDart Express Proof-of-Delivery
6. courier_delhivery_02: Delhivery Logistics Handover Receipt
"""

from pathlib import Path
from typing import Dict
from PIL import Image, ImageDraw, ImageFont


def _get_font(size: int = 16, bold: bool = False):
    try:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()


def create_gpay_upi_template() -> Image.Image:
    w, h = 600, 900
    img = Image.new("RGB", (w, h), (245, 247, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (w, 140)], fill=(26, 115, 232))
    draw.text((w // 2 - 110, 50), "Payment Successful", fill=(255, 255, 255), font=_get_font(24, True))
    draw.text((w // 2 - 80, 90), "Transaction Complete", fill=(220, 240, 255), font=_get_font(16))

    draw.rectangle([(40, 160), (w - 40, 480)], fill=(255, 255, 255), outline=(220, 225, 230), width=2)
    draw.text((60, 190), "Paid to", fill=(100, 110, 120), font=_get_font(16))
    draw.text((60, 215), "TechMart India Pvt Ltd", fill=(20, 30, 40), font=_get_font(22, True))
    draw.text((60, 255), "VPA: techmart@razorpay", fill=(120, 130, 140), font=_get_font(14))
    draw.line([(60, 290), (w - 60, 290)], fill=(235, 240, 245), width=2)
    draw.text((60, 320), "Amount Debited", fill=(100, 110, 120), font=_get_font(16))
    draw.text((60, 350), "₹ 4,850.00", fill=(10, 120, 40), font=_get_font(36, True))

    draw.rectangle([(40, 500), (w - 40, 820)], fill=(255, 255, 255), outline=(220, 225, 230), width=2)
    fields = [
        ("Transaction ID", "pay_N9vKl4M29Lp1"),
        ("UPI Reference No", "423984719283"),
        ("Date & Time", "22 Aug 2026, 02:45 PM"),
        ("Sender VPA", "buyer@okaxis"),
        ("Payment Mode", "UPI - Instant Settlement"),
        ("Gateway Status", "CAPTURED (RZP_SETTLED)"),
    ]
    y_pos = 530
    for label, val in fields:
        draw.text((60, y_pos), label, fill=(110, 120, 130), font=_get_font(14))
        draw.text((w - 60 - (len(val) * 9), y_pos), val, fill=(30, 40, 50), font=_get_font(14, True))
        y_pos += 45
    draw.text((w // 2 - 90, 850), "Secured by Razorpay Gateway", fill=(160, 170, 180), font=_get_font(13))
    return img


def create_phonepe_upi_template() -> Image.Image:
    w, h = 600, 900
    img = Image.new("RGB", (w, h), (248, 246, 252))
    draw = ImageDraw.Draw(img)
    # PhonePe Purple theme
    draw.rectangle([(0, 0), (w, 130)], fill=(95, 37, 159))
    draw.text((w // 2 - 100, 45), "Transaction Successful", fill=(255, 255, 255), font=_get_font(22, True))
    draw.text((w // 2 - 70, 85), "PhonePe Payment", fill=(230, 210, 255), font=_get_font(15))

    draw.rectangle([(30, 150), (w - 30, 440)], fill=(255, 255, 255), outline=(210, 200, 225), width=1)
    draw.text((50, 175), "Paid To Merchant", fill=(110, 100, 120), font=_get_font(14))
    draw.text((50, 200), "Flipkart Internet Pvt Ltd", fill=(30, 20, 40), font=_get_font(20, True))
    draw.text((50, 235), "UPI ID: flipkart.pay@ybl", fill=(130, 120, 140), font=_get_font(13))
    draw.line([(50, 270), (w - 50, 270)], fill=(240, 235, 245), width=1)
    draw.text((50, 295), "Total Amount", fill=(110, 100, 120), font=_get_font(15))
    draw.text((50, 325), "₹ 2,999.00", fill=(95, 37, 159), font=_get_font(34, True))

    draw.rectangle([(30, 460), (w - 30, 780)], fill=(255, 255, 255), outline=(210, 200, 225), width=1)
    details = [
        ("Txn Reference ID", "pay_PHNP8923401"),
        ("Bank UTR", "982347109283"),
        ("Payment Date", "21-Aug-2026 18:22 IST"),
        ("Debited From", "HDFC Bank XX4092"),
        ("Service Type", "E-Commerce Checkout"),
    ]
    y = 485
    for label, val in details:
        draw.text((50, y), label, fill=(100, 100, 110), font=_get_font(13))
        draw.text((w - 50 - (len(val) * 9), y), val, fill=(20, 20, 30), font=_get_font(13, True))
        y += 50
    return img


def create_apex_invoice_template() -> Image.Image:
    w, h = 800, 1050
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(20, 20), (w - 20, h - 20)], outline=(50, 50, 50), width=2)
    draw.text((40, 40), "TAX INVOICE", fill=(10, 30, 80), font=_get_font(28, True))
    draw.text((40, 80), "Apex Retail Solutions Private Limited", fill=(40, 40, 40), font=_get_font(16, True))
    draw.text((40, 105), "GSTIN: 29AAAAA0000A1Z5 | PAN: AAAAA0000A", fill=(80, 80, 80), font=_get_font(13))
    draw.line([(40, 140), (w - 40, 140)], fill=(150, 150, 150), width=1)

    draw.text((40, 155), "Invoice Number: INV-2026-8942", fill=(20, 20, 20), font=_get_font(15, True))
    draw.text((40, 180), "Invoice Date: 18-Aug-2026", fill=(40, 40, 40), font=_get_font(14))
    draw.text((40, 205), "Order ID: order_N8xKm92Lp01", fill=(40, 40, 40), font=_get_font(14))
    draw.text((450, 155), "Billed To: Aarav Sharma", fill=(20, 20, 20), font=_get_font(15, True))
    draw.text((450, 180), "Bellandur, Bangalore 560103", fill=(60, 60, 60), font=_get_font(13))

    draw.rectangle([(40, 250), (w - 40, 285)], fill=(230, 235, 245))
    draw.text((50, 260), "Item Description", fill=(20, 30, 50), font=_get_font(14, True))
    draw.text((700, 260), "Total", fill=(20, 30, 50), font=_get_font(14, True))
    draw.text((50, 310), "Smart Noise-Cancelling Headphones Pro", fill=(30, 30, 30), font=_get_font(14))
    draw.text((680, 310), "₹ 12,499.00", fill=(30, 30, 30), font=_get_font(14, True))
    draw.line([(40, 360), (w - 40, 360)], fill=(200, 200, 200), width=1)
    draw.rectangle([(480, 400), (w - 40, 445)], fill=(240, 248, 255), outline=(180, 210, 240))
    draw.text((500, 412), "Grand Total: ₹ 12,499.00", fill=(10, 30, 80), font=_get_font(18, True))
    return img


def create_techmart_invoice_template() -> Image.Image:
    w, h = 800, 1050
    img = Image.new("RGB", (w, h), (252, 252, 254))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(15, 15), (w - 15, h - 15)], outline=(80, 100, 120), width=2)
    draw.rectangle([(15, 15), (w - 15, 90)], fill=(30, 50, 70))
    draw.text((35, 35), "COMMERCIAL B2B INVOICE", fill=(255, 255, 255), font=_get_font(24, True))

    draw.text((35, 110), "TechMart Enterprise Supplies Ltd", fill=(20, 20, 20), font=_get_font(16, True))
    draw.text((35, 135), "GSTIN: 36AABCT1234F1Z8 | Hyderabad Hub", fill=(80, 80, 80), font=_get_font(13))
    draw.text((35, 170), "Invoice Ref: TM-INV-55102", fill=(40, 40, 40), font=_get_font(14, True))
    draw.text((35, 195), "Date: 15-Aug-2026", fill=(60, 60, 60), font=_get_font(13))
    draw.text((450, 170), "Client: CloudNine Studios", fill=(40, 40, 40), font=_get_font(14, True))

    draw.rectangle([(35, 240), (w - 35, 275)], fill=(220, 230, 240))
    draw.text((45, 250), "Description", fill=(30, 40, 50), font=_get_font(14, True))
    draw.text((680, 250), "Amount", fill=(30, 40, 50), font=_get_font(14, True))
    draw.text((45, 300), "Server Hardware Rack Mount Module 4U", fill=(30, 30, 30), font=_get_font(14))
    draw.text((670, 300), "₹ 48,500.00", fill=(30, 30, 30), font=_get_font(14, True))
    draw.rectangle([(450, 380), (w - 35, 425)], fill=(235, 245, 235), outline=(150, 200, 150))
    draw.text((470, 392), "Net Payable: ₹ 48,500.00", fill=(20, 100, 40), font=_get_font(16, True))
    return img


def create_bluedart_pod_template() -> Image.Image:
    w, h = 750, 600
    img = Image.new("RGB", (w, h), (250, 250, 252))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (w, 90)], fill=(20, 40, 90))
    draw.text((30, 25), "BlueDart Express — Proof of Delivery (POD)", fill=(255, 255, 255), font=_get_font(22, True))
    draw.rectangle([(w - 180, 25), (w - 30, 65)], fill=(40, 167, 69))
    draw.text((w - 155, 35), "DELIVERED", fill=(255, 255, 255), font=_get_font(16, True))

    draw.rectangle([(30, 110), (w - 30, 340)], fill=(255, 255, 255), outline=(210, 215, 225), width=1)
    fields = [
        ("Tracking / AWB No:", "BD-849302198"),
        ("Merchant Order ID:", "order_N8xKm92Lp01"),
        ("Recipient Name:", "Aarav Sharma"),
        ("Delivery Timestamp:", "20-Aug-2026 14:12 IST"),
        ("Receiver OTP Status:", "OTP VERIFIED (8392)"),
    ]
    y = 130
    for label, val in fields:
        draw.text((50, y), label, fill=(100, 110, 120), font=_get_font(13))
        draw.text((250, y), val, fill=(30, 30, 40), font=_get_font(13, True))
        y += 35
    draw.rectangle([(50, 370), (320, 520)], fill=(255, 255, 255), outline=(180, 180, 180))
    draw.text((60, 380), "Recipient Signature:", fill=(100, 100, 100), font=_get_font(12))
    draw.line([(80, 450), (140, 430), (180, 460), (220, 420), (280, 440)], fill=(20, 40, 120), width=3)
    return img


def create_delhivery_pod_template() -> Image.Image:
    w, h = 750, 600
    img = Image.new("RGB", (w, h), (247, 248, 250))
    draw = ImageDraw.Draw(img)
    # Delhivery Red / Black header
    draw.rectangle([(0, 0), (w, 85)], fill=(180, 20, 30))
    draw.text((30, 25), "Delhivery — Consignment Handover Slip", fill=(255, 255, 255), font=_get_font(20, True))
    draw.rectangle([(w - 170, 22), (w - 25, 62)], fill=(30, 140, 50))
    draw.text((w - 150, 32), "SUCCESS", fill=(255, 255, 255), font=_get_font(15, True))

    draw.rectangle([(30, 105), (w - 30, 330)], fill=(255, 255, 255), outline=(200, 205, 215), width=1)
    fields = [
        ("Waybill Number:", "DEL-991204812"),
        ("Client ID:", "CL-AMAZON-IN"),
        ("Customer Name:", "Priya Patel"),
        ("Delivery Time:", "19-Aug-2026 11:45 IST"),
        ("Hub Handover:", "Mumbai West Delivery Center"),
    ]
    y = 120
    for label, val in fields:
        draw.text((50, y), label, fill=(90, 95, 105), font=_get_font(13))
        draw.text((240, y), val, fill=(20, 25, 35), font=_get_font(13, True))
        y += 35
    draw.rectangle([(50, 350), (320, 500)], fill=(255, 255, 255), outline=(170, 170, 170))
    draw.text((60, 360), "Recipient Sign Seal:", fill=(90, 90, 90), font=_get_font(12))
    draw.line([(90, 430), (130, 410), (170, 440), (210, 400), (270, 420)], fill=(10, 20, 80), width=2)
    return img


def generate_base_templates(output_dir: str = "data/templates") -> Dict[str, str]:
    """Renders 6 distinct base templates across 3 e-commerce payment categories."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    templates = {
        "upi_gpay_01.png": create_gpay_upi_template(),
        "upi_phonepe_02.png": create_phonepe_upi_template(),
        "gst_invoice_apex_01.png": create_apex_invoice_template(),
        "gst_invoice_techmart_02.png": create_techmart_invoice_template(),
        "courier_bluedart_01.png": create_bluedart_pod_template(),
        "courier_delhivery_02.png": create_delhivery_pod_template(),
    }

    saved_paths = {}
    for filename, img in templates.items():
        file_path = out_path / filename
        img.save(str(file_path), "PNG")
        saved_paths[filename] = str(file_path)

    return saved_paths


if __name__ == "__main__":
    paths = generate_base_templates()
    print(f"Generated {len(paths)} distinct base templates.")
