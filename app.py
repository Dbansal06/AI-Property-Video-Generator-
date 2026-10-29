import os
import sys
import json
import argparse
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import numpy as np

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    concatenate_videoclips
)

# ---------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# ---------------------------------------------------------------------------
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
DEFAULT_FPS = 24
SLIDE_DURATION = 5.0  # seconds per scene
TRANSITION_DURATION = 1.0  # crossfade duration

PRIMARY_COLOR = (24, 43, 73)      # Deep Navy
ACCENT_COLOR = (212, 160, 23)     # Gold
TEXT_COLOR = (255, 255, 255)      # White
BG_CARD_COLOR = (15, 23, 42, 210)  # Semi-transparent dark navy


# ---------------------------------------------------------------------------
# 1. SCRIPT & CAPTION GENERATION (REASONING & SYNTHESIS LOGIC)
# ---------------------------------------------------------------------------
def generate_property_narrative(data: Dict[str, Any]) -> Tuple[str, List[Dict[str, str]]]:
    """
    Generates structured script and slide caption overlays based strictly on input facts.
    Prevents hallucination by relying only on supplied details.
    """
    name = data.get("property_name", "Featured Property")
    location = data.get("location", "Prime Location")
    price = data.get("price", "Contact for Price")
    prop_type = data.get("property_type", "Residential")
    features = data.get("key_features", [])
    contact = data.get("contact_cta", "Contact us today for more details.")

    # Generate full voiceover narrative text
    features_text = ", ".join(features[:-1]) + f", and {features[-1]}" if len(features) > 1 else (features[0] if features else "modern amenities")
    
    full_script = (
        f"Welcome to {name}, located in {location}. "
        f"This stunning {prop_type} is offered at {price}. "
        f"Key highlights include {features_text}. "
        f"{contact}"
    )

    # Break details into scene-specific overlays
    scene_overlays = [
        {"title": name, "subtitle": f"{prop_type} | {location}"},
        {"title": "Pricing & Value", "subtitle": f"Offered at {price}"},
    ]

    # Map features across available middle slides
    if features:
        feat_str = " • ".join(features)
        scene_overlays.append({"title": "Key Features", "subtitle": feat_str})

    scene_overlays.append({"title": "Take The Next Step", "subtitle": contact})

    return full_script, scene_overlays


# ---------------------------------------------------------------------------
# 2. IMAGE PREPROCESSING & OVERLAY GRAPHICS
# ---------------------------------------------------------------------------
def process_and_resize_image(img_path: str, target_w: int = VIDEO_WIDTH, target_h: int = VIDEO_HEIGHT) -> Image.Image:
    """
    Resizes and crops image to fit target resolution (16:9 1080p) without stretching.
    """
    img = Image.open(img_path).convert("RGB")
    img_w, img_h = img.size
    
    # Calculate aspect ratios
    target_ratio = target_w / target_h
    img_ratio = img_w / img_h

    if img_ratio > target_ratio:
        # Image is wider: crop sides
        new_w = int(target_ratio * img_h)
        offset = (img_w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, img_h))
    else:
        # Image is taller: crop top/bottom
        new_h = int(img_w / target_ratio)
        offset = (img_h - new_h) // 2
        img = img.crop((0, offset, img_w, offset + new_h))

    return img.resize((target_w, target_h), Image.Resampling.LANCZOS)


def draw_text_overlay(base_img: Image.Image, title: str, subtitle: str) -> Image.Image:
    """
    Draws modern text overlay banners onto the image frame using PIL.
    """
    img_overlay = base_img.copy()
    draw = ImageDraw.Draw(img_overlay, "RGBA")
    
    # Simple fallback font selection
    try:
        font_title = ImageFont.truetype("arial.ttf", 52)
        font_sub = ImageFont.truetype("arial.ttf", 32)
    except IOError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Calculate banner card dimensions
    card_margin = 80
    card_padding = 30
    card_bottom = VIDEO_HEIGHT - card_margin
    card_height = 160
    card_top = card_bottom - card_height
    card_left = card_margin
    card_right = VIDEO_WIDTH - card_margin

    # Draw dark overlay container
    draw.rectangle(
        [card_left, card_top, card_right, card_bottom],
        fill=BG_CARD_COLOR,
        outline=ACCENT_COLOR,
        width=3
    )

    # Draw title text
    draw.text(
        (card_left + card_padding, card_top + 20),
        title,
        fill=ACCENT_COLOR,
        font=font_title
    )

    # Draw subtitle text
    draw.text(
        (card_left + card_padding, card_top + 90),
        subtitle,
        fill=TEXT_COLOR,
        font=font_sub
    )

    return img_overlay


# ---------------------------------------------------------------------------
# 3. VIDEO ASSEMBLY ENGINE
# ---------------------------------------------------------------------------
def build_video(
    data: Dict[str, Any],
    images: List[str],
    output_filepath: str,
    temp_dir: str = "temp"
) -> None:
    os.makedirs(temp_dir, exist_ok=True)
    
    print("[1/4] Generating voice-over narration and script overlays...")
    script_text, scene_overlays = generate_property_narrative(data)

    # Generate Audio via gTTS
    audio_path = os.path.join(temp_dir, "narration.mp3")
    tts = gTTS(text=script_text, lang='en', slow=False)
    tts.save(audio_path)
    
    narration_clip = AudioFileClip(audio_path)
    total_audio_duration = narration_clip.duration + 1.0  # padding

    # Adjust slide timing based on audio duration
    num_scenes = max(len(images), len(scene_overlays))
    calculated_duration = max(SLIDE_DURATION, total_audio_duration / num_scenes)

    print(f"[2/4] Processing {len(images)} images and creating dynamic overlays...")
    processed_clips = []
    
    for idx in range(num_scenes):
        # Match image and overlay dynamically
        img_file = images[idx % len(images)]
        overlay_info = scene_overlays[idx % len(scene_overlays)]

        # Process image graphics
        resized_base = process_and_resize_image(img_file)
        final_frame = draw_text_overlay(
            resized_base,
            title=overlay_info["title"],
            subtitle=overlay_info["subtitle"]
        )

        # Convert PIL Image to NumPy array for MoviePy
        frame_np = np.array(final_frame)
        
        # Build ImageClip
        img_clip = ImageClip(frame_np).set_duration(calculated_duration)
        processed_clips.append(img_clip)

    print("[3/4] Compositing video timeline with transitions...")
    # Apply crossfade transitions between scenes
    final_video = concatenate_videoclips(
        processed_clips,
        method="compose",
        padding=-TRANSITION_DURATION
    )

    # Attach Narration Audio
    final_video = final_video.set_audio(narration_clip)

    print(f"[4/4] Rendering video file to {output_filepath}...")
    final_video.write_videofile(
        output_filepath,
        fps=DEFAULT_FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium"
    )

    # Cleanup temporary narration file
    narration_clip.close()
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    print("\n✅ Promo video generated successfully!")


# ---------------------------------------------------------------------------
# 4. INPUT VALIDATION & CLI PARSER
# ---------------------------------------------------------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Property Video Generator")
    parser.add_argument(
        "--json",
        type=str,
        default="sample_data/property.json",
        help="Path to property details JSON file"
    )
    parser.add_argument(
        "--images",
        nargs="+",
        help="List of image paths (space separated). Overrides JSON image list if provided."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/property_promo.mp4",
        help="Destination path for rendered MP4 video"
    )
    return parser.parse_args()


def validate_and_load_input(json_path: str, custom_images: List[str]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Validates input data integrity and missing files gracefully without crashing.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Error: Property JSON file not found at '{json_path}'.")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Determine image list
    image_paths = custom_images if custom_images else data.get("images", [])

    if not image_paths:
        raise ValueError("Error: No images supplied in JSON or command-line arguments.")

    valid_images = []
    for img_p in image_paths:
        if os.path.exists(img_p):
            valid_images.append(img_p)
        else:
            print(f"⚠️ Warning: Image file '{img_p}' not found. Skipping...")

    if not valid_images:
        raise FileNotFoundError("Error: None of the supplied image paths exist on disk.")

    return data, valid_images


if __name__ == "__main__":
    args = parse_arguments()

    try:
        # Ensure output directory exists
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        prop_data, image_files = validate_and_load_input(args.json, args.images)
        build_video(prop_data, image_files, args.output)

    except Exception as e:
        print(f"\n❌ Execution Failed: {str(e)}", file=sys.stderr)
        sys.exit(1)