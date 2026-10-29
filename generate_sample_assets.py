import os
import json
from PIL import Image, ImageDraw, ImageFont

def create_sample_dataset():
    os.makedirs("sample_data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Create synthetic images representing property rooms
    slides = [
        ("Grand Exterior & Facade", (30, 58, 112)),
        ("Spacious Living Room", (44, 82, 130)),
        ("Modern Gourmet Kitchen", (56, 110, 140)),
        ("Master Bedroom Suite", (70, 130, 150))
    ]

    image_paths = []
    for idx, (label, color) in enumerate(slides, start=1):
        img = Image.new("RGB", (1920, 1080), color=color)
        draw = ImageDraw.Draw(img)
        
        # Add decorative geometric shapes to simulate modern architectural photo
        draw.rectangle([100, 100, 1820, 980], outline=(255, 255, 255), width=4)
        draw.line([100, 540, 1820, 540], fill=(255, 255, 255), width=2)
        
        try:
            font = ImageFont.truetype("arial.ttf", 64)
        except IOError:
            font = ImageFont.load_default()
            
        draw.text((200, 200), f"SAMPLE PHOTO {idx}: {label}", fill=(255, 255, 255), font=font)
        
        path = f"sample_data/img{idx}.jpg"
        img.save(path)
        image_paths.append(path)

    # Write property metadata JSON
    property_data = {
        "property_name": "The Grand Horizon Luxury Residence",
        "location": "Bandra West, Mumbai",
        "price": "₹4.5 Cr",
        "property_type": "3 BHK Premium Apartment",
        "key_features": [
            "Sea-facing balcony",
            "Fully automated smart home system",
            "Italian marble flooring",
            "2 Dedicated covered parking spaces"
        ],
        "contact_cta": "Call Realty Assistant at +91-9876543210 or visit www.realtyassistant.in",
        "images": image_paths
    }

    json_path = "sample_data/property.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(property_data, f, indent=4)

    print("✅ Sample synthetic property metadata and images created successfully in 'sample_data/'.")

if __name__ == "__main__":
    create_sample_dataset()
