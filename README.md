## 🎥 Turn Wide Images into Vertical Showcase Videos for Instagram Reels, TikTok, and YouTube Shorts

> **A simple Python script that transforms wide images into engaging 1080×1920 videos for Instagram Reels, TikTok, and YouTube Shorts — with smooth pan + fade effects.**


## ✨ Features
- **Automatic batch processing** — drop multiple images, get multiple videos
- **Cinematic animation**:  
  1️⃣ Starts zoomed in on the **left**  
  2️⃣ Smoothly **pans right**  
  3️⃣ **Fades** to the full image (no distortion!)
- **Perfect 9:16 aspect ratio** (1080×1920) — ready for Reels & Shorts
- **Smart letterboxing** — preserves original proportions with black bars if needed
- **Zero dependencies** beyond OpenCV & NumPy

---

## 🚀 Quick Start

### 1. Clone or download this repository
```bash
git clone https://github.com/your-username/stillmotion.git
cd stillmotion
```

### 2. Install dependencies
```bash
pip install opencv-python numpy
```

### 3. Add your images
Place your JPG or PNG files in the input/ folder:
```bash
stillmotion/
├── input/
│   ├── beach.jpg
│   └── mountains.png
└── ...
```

### 4. Run the script
```bash
python wideSlider.py
```

### 5. Get your videos!
Your ready-to-post videos will appear in the output/ folder:
```bash
output/
├── beach.mp4
└── mountains.mp4
```

## 📝 Requirements 
- Python 3.6+
- opencv-python (for video/image processing)
- numpy (for array operations)


## 📄 License 
MIT License — feel free to use, modify, and share! 
