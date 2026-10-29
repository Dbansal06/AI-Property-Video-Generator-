# AI Property Video Generator

A lightweight Python application that transforms static property photos and structured listing metadata into professional, promo-ready HD MP4 real estate videos complete with custom overlays, scene transitions, and AI voice-over narration.

Designed as an automated content creation utility for real estate sales and marketing teams.

---

## 🛠️ Key Features

- **Fact-Grounded Script Generation**: Synthesizes structured voice-over scripts using supplied listing details without hallucinating facts.
- **Dynamic Graphical Overlays**: Automatically centers, crops (16:9 1080p), and draws high-contrast dark card text overlays for each scene using Pillow.
- **Voice-over Narration**: Automatically renders speech audio from property facts using `gTTS`.
- **Professional Crossfade Transitions**: Smooth blend transitions generated dynamically between image slides using `MoviePy`.
- **Resilient Input Handling**: Gracefully handles missing image paths or incomplete properties with warnings instead of throwing uncaught exceptions.

---

## 📋 Prerequisites & Installation

### 1. Requirements
- **Python**: 3.9, 3.10, or 3.11 recommended.
- **FFmpeg**: Required by `MoviePy` for video rendering.
  - *Ubuntu/Debian*: `sudo apt-get install ffmpeg`
  - *macOS*: `brew install ffmpeg`
  - *Windows*: Download binaries or install via `winget install FFmpeg`

### 2. Setup Virtual Environment

```bash
# Clone or navigate to the project directory
cd property_video_generator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Quickstart Guide

### Step 1: Generate Sample Data & Assets
Run the synthetic asset generator script to populate mock test photos and JSON metadata:

```bash
python generate_sample_assets.py
```

### Step 2: Run the Video Generator
Execute the main application via CLI:

```bash
python app.py --json sample_data/property.json --output output/luxury_apartment_promo.mp4
```

---

## 💻 CLI Usage Options

```bash
python app.py [-h] [--json JSON] [--images IMAGES [IMAGES ...]] [--output OUTPUT]
```

### Arguments:
- `--json`: Path to property JSON metadata file (Default: `sample_data/property.json`)
- `--images`: Optional custom list of image files to override images specified inside JSON.
- `--output`: Output file destination for the rendered MP4 (Default: `output/property_promo.mp4`)

**Example using custom command-line image overrides:**
```bash
python app.py --json sample_data/property.json --images custom1.jpg custom2.jpg --output output/custom_video.mp4
```

---

## 📝 Input JSON Data Format

```json
{
    "property_name": "The Grand Horizon Residence",
    "location": "Bandra West, Mumbai",
    "price": "₹4.5 Cr",
    "property_type": "3 BHK Premium Apartment",
    "key_features": [
        "Sea-facing balcony",
        "Smart home automation",
        "Italian marble flooring"
    ],
    "contact_cta": "Call Realty Assistant at +91-9876543210",
    "images": [
        "sample_data/img1.jpg",
        "sample_data/img2.jpg",
        "sample_data/img3.jpg"
    ]
}
```

---

## ⚙️ Architecture & Technical Approach

1. **Information Extraction**: The system reads raw JSON listings and structures key facts into clear visual slide overlays (Title slide, Value proposition, Key features highlight, and Final CTA slide).
2. **Narration Synthesis**: Converts structured script text into standard clear audio using Google Text-to-Speech (`gTTS`).
3. **Graphics Engine**: Standardizes images using PIL Lanczos downsampling/cropping to 1920x1080 resolution, appending semi-transparent vector cards with distinct title typography.
4. **Timeline Compositing**: Sets relative scene timing according to narration length and applies smooth crossfade video transitions before encoding with standard H.264 video codec and AAC audio codec.

---

## ⚠️ Known Limitations & Future Improvements

- **Background Music**: Current setup utilizes narration audio. Background music track layering can be easily added as an secondary audio composite track.
- **Fonts**: Uses standard system fonts (`arial.ttf` / default font). Custom brand typography files can be specified in `draw_text_overlay()`.
