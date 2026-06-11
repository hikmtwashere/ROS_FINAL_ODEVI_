#!/usr/bin/env python3

import os
import qrcode

base_dir = "/home/hikmetunverdi/rbtg_ws/src/bookstore_service_robot/models/qr_markers/materials/textures"
os.makedirs(base_dir, exist_ok=True)

qr_data = {
    "information_desk.png": "LOCATION=INFORMATION_DESK",
    "science_section.png": "LOCATION=SCIENCE_SECTION",
    "novel_section.png": "LOCATION=NOVEL_SECTION",
    "checkout_area.png": "LOCATION=CHECKOUT_AREA",
}

for filename, text in qr_data.items():
    img = qrcode.make(text)
    path = os.path.join(base_dir, filename)
    img.save(path)
    print(f"QR oluşturuldu: {path} -> {text}")
