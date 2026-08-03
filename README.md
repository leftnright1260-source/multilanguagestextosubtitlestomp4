🎬 Text-to-Subtitles MP4 Generator
The idea is to create a green-screen MP4 from a text file in 60+ languages converted into subtitles, with a fixed reading pace adjustable by ±50%. Includes live preview and direct MP4 export—perfect for making subtitles for Shorts and videos!

📋 Overview
Text-to-Subtitles MP4 Generator is a Python desktop application with a simple user interface designed to automate subtitle video creation. Unlike traditional tools that require pre-recorded audio to sync text, this program automatically calculates the timeline and reading pace directly from a plain text file (.txt).

It exports a high-quality 30 FPS MP4 video with a green chroma-key background (#126e47), ready to drop into Premiere Pro, CapCut, or DaVinci Resolve to key out the background in seconds.

✨ Key Features
Smart Multilingual Support (60+ Languages): Automatically handles Latin, Cyrillic, CJK, RTL/Arabic, Indic, and Amharic scripts with proper fonts and character limits.

Dynamic Time-Stretching (±50% Range): Features a speed slider to speed up or slow down the overall reading pace by up to 50% in real time to match voiceovers.

Live Preview & Controls: Play, pause, reset, or scrub through subtitle blocks before exporting.

Automatic Grammar-Based Pacing: Calculates natural reading pauses based on periods, commas, question marks, and line breaks.

Direct Local MP4 Rendering: Generates HD videos locally using OpenCV and Pillow with high-contrast text shadows, without cloud fees or watermarks.

🛠️ How It Works
Select Language: Choose your target language to apply the correct typography rules.

Load Text File: Import your .txt file; the app automatically formats and splits text into clean two-line subtitle blocks.

Adjust Pace (Optional): Use the ±50% slider to calibrate the final duration.

Preview or Export: Test the live preview, then click export to render your .mp4 video.

🚀 How to Run
Make sure you have Python installed.

Install the required libraries:
pip install opencv-python numpy Pillow

Run the main script:
python main.py
📄 Copyright & Credits
© 2026 José Galindo. All rights reserved.

Developed as a professional tool for subtitle automation and multi-language content creation.

Developer: José Galindo

Website: https://gabriels.work
