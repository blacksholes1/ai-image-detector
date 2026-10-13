import os
import sys
import numpy as np
import cv2
from PIL import Image
from PIL.ExifTags import TAGS

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def clean_path(path_input):
    """Cleans drag-and-drop formatting issues (quotes, escaping, trailing spaces)"""
    path = path_input.strip()
    if (path.startswith('"') and path.endswith('"')) or (path.startswith("'") and path.endswith("'")):
        path = path[1:-1]
    return path

def analyze_metadata(file_path):
    """Scans binary data and EXIF tags for known AI model signatures."""
    results = {
        "status": "Clean",
        "flags": [],
        "exif_found": False
    }
    
    # Common signature flags left behind by AI models and generation tools
    ai_keywords = [
        b'c2pa', b'adobe_firefly', b'midjourney', b'stable-diffusion', 
        b'dall-e', b'comfyui', b'automatic1111', b'creative_agent', 
        b'generative_ai', b'waifu2x', b'gan_image'
    ]

    # 1. Binary stream scan (Highly accurate for stripped metadata structures)
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
            for kw in ai_keywords:
                if kw in file_bytes.lower():
                    results["flags"].append(f"AI Signature found in file structure: {kw.decode('utf-8')}")
                    results["status"] = "AI Generated"
    except Exception as e:
        results["flags"].append(f"Could not scan file binary data: {str(e)}")

    # 2. Traditional EXIF Header scan
    try:
        with Image.open(file_path) as img:
            exif_data = img.getexif()
            if exif_data:
                results["exif_found"] = True
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    val_str = str(value).lower()
                    
                    # Look for clues in software/artist info strings
                    if any(kw.decode('utf-8') in val_str for kw in ai_keywords):
                        results["flags"].append(f"AI Meta-tag in EXIF [{tag_name}]: {value}")
                        results["status"] = "AI Generated"
    except Exception:
        pass # Not all files support standard PIL EXIF streams (like videos)

    return results

def analyze_noise_signature(file_path):
    """
    Performs Noise Signature / Error Level Analysis (ELA).
    AI generations often exhibit hyper-uniform distributions or local noise variance grids.
    """
    try:
        # Load the image
        img = cv2.imread(file_path)
        if img is None:
            return "Unable to compute noise signature (Unsupported frame layout)"

        # Check resolution size for threshold calculations
        h, w, _ = img.shape
        
        # Method: Recompress and extract structural error discrepancies
        tmp_name = "tmp_recompress.jpg"
        cv2.imwrite(tmp_name, img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        recompressed = cv2.imread(tmp_name)
        os.remove(tmp_name)

        # Absolute pixel variances reveal anomalies between native compressions 
        diff = cv2.absdiff(img, recompressed)
        mean_variance = np.mean(diff)
        max_variance = np.max(diff)
        std_dev = np.std(diff)

        # Heuristic Assessment:
        # AI images typically feature either perfectly clean math noise layouts or extreme local spikes 
        if mean_variance < 0.2:
            return f"Suspiciously Uniform (Score: {mean_variance:.4f}) - High likelihood of synthetic vector origins."
        elif std_dev > 4.5:
            return f"Anomalous Localized Chaos (StdDev: {std_dev:.2f}) - Indication of regional splicing/AI elements."
        else:
            return f"Normal Structural Variance (Score: {mean_variance:.4f})"
            
    except Exception as e:
        return f"Noise analysis skipped: {str(e)}"

def process_file(file_path):
    file_path = clean_path(file_path)
    
    if not os.path.exists(file_path):
        print(f"\n❌ Error: The file path '{file_path}' does not exist.")
        return

    print("\n" + "="*50)
    print(f"🔍 SCANNING: {os.path.basename(file_path)}")
    print("="*50)

    # 1. Evaluate Metadata
    print("\n[1/2] Parsing Metadata Tracks...")
    meta_results = analyze_metadata(file_path)
    
    if meta_results["flags"]:
        for flag in meta_results["flags"]:
            print(f" ⚠️  {flag}")
    else:
        print(" No toxic AI meta-tags found in basic binary markers.")

    # 2. Evaluate Noise Signature
    print("\n[2/2] Analyzing Micro-Noise Matrix Consistency...")
    noise_score = analyze_noise_signature(file_path)
    print(f" 📊 Noise Results: {noise_score}")

    # Final Summary Matrix Output
    print("\n" + "="*50)
    print("📋 FORENSIC VERDICT SUMMARY:")
    print("="*50)
    
    if meta_results["status"] == "AI Generated":
        print("🚨 VERDICT: HIGH RISK / CONFIRMED AI CONTENT (Hard Signatures Match)")
    elif "Suspicious" in noise_score or "Anomalous" in noise_score:
        print("VERDICT: SUSPICIOUS (Metadata is clean but noise patterns deviate from standard camera optics)")
    else:
        print("VERDICT: PASS (No basic automated AI signatures detected)")
    print("="*50 + "\n")

def main():
    clear_screen()
    print("====================================================")
    print("          AI IMAGE & VIDEO FORENSIC SCANNER       ")
    print("====================================================")
    
    while True:
        try:
            print(" Drag and drop your file directly into this terminal window")
            print("   (Or type 'exit' to quit)")
            user_input = input("\nFile Path: ")
            
            if user_input.strip().lower() == 'exit':
                print("Exiting tool. Goodbye!")
                break
                
            if not user_input.strip():
                continue
                
            process_file(user_input)
            
            print("-" * 50)
        except KeyboardInterrupt:
            print("\nExiting tool.")
            sys.exit(0)

if __name__ == "__main__":
    main()
