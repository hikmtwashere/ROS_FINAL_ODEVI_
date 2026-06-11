#!/usr/bin/env python3

import os

pkg_dir = "/home/hikmetunverdi/rbtg_ws/src/bookstore_service_robot"
models_dir = os.path.join(pkg_dir, "models")

qr_items = {
    "qr_information_desk": {
        "texture": "information_desk.png",
        "material": "QRInformationDesk",
    },
    "qr_science_section": {
        "texture": "science_section.png",
        "material": "QRScienceSection",
    },
    "qr_novel_section": {
        "texture": "novel_section.png",
        "material": "QRNovelSection",
    },
    "qr_checkout_area": {
        "texture": "checkout_area.png",
        "material": "QRCheckoutArea",
    },
}

for model_name, data in qr_items.items():
    model_dir = os.path.join(models_dir, model_name)
    scripts_dir = os.path.join(model_dir, "materials", "scripts")
    textures_dir = os.path.join(model_dir, "materials", "textures")

    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(textures_dir, exist_ok=True)

    src_texture = os.path.join(models_dir, "qr_markers", "materials", "textures", data["texture"])
    dst_texture = os.path.join(textures_dir, data["texture"])

    with open(src_texture, "rb") as src:
        with open(dst_texture, "wb") as dst:
            dst.write(src.read())

    model_config = f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author>
    <name>Hikmet</name>
  </author>
  <description>QR marker model for bookstore service robot mission</description>
</model>
"""

    material_script = f"""material {data["material"]}
{{
  technique
  {{
    pass
    {{
      texture_unit
      {{
        texture {data["texture"]}
      }}
    }}
  }}
}}
"""

    model_sdf = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{model_name}">
    <static>true</static>
    <link name="qr_link">
      <visual name="qr_visual">
        <pose>0 0 0 0 0 0</pose>
        <geometry>
          <box>
            <size>0.60 0.02 0.60</size>
          </box>
        </geometry>
        <material>
          <script>
            <uri>model://{model_name}/materials/scripts</uri>
            <uri>model://{model_name}/materials/textures</uri>
            <name>{data["material"]}</name>
          </script>
        </material>
      </visual>
    </link>
  </model>
</sdf>
"""

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(model_config)

    with open(os.path.join(scripts_dir, "qr.material"), "w") as f:
        f.write(material_script)

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write(model_sdf)

    print(f"Model oluşturuldu: {model_dir}")
