🎬 Text-to-Subtitles MP4 Generator

Create green-screen subtitle videos from plain text in 67 languages.

Text-to-Subtitles MP4 Generator converts a .txt file into a 1920×1080 MP4 video with animated subtitle-style text on a green-screen background.

The reading pace is automatically calculated from the text and can be adjusted by ±50% to match your voiceover or narration.

Designed for YouTube Shorts, social media videos, video editing, and multilingual content creation.

📥 Download for Windows
⬇️ Download Subtitletomp4 v1.0.0 — Windows 64-bit

No Python installation required.

Download the ZIP, extract it, and run the Windows executable included in the package.

Tip: Do not download "Source code (zip)" if you simply want to use the application. Download the Windows executable ZIP above.

📋 Overview

Text-to-Subtitles MP4 Generator is a Python desktop application designed to automate the creation of subtitle-style MP4 videos from plain text files.

Instead of requiring pre-recorded audio to synchronize the text, the application calculates the subtitle timing directly from the text and its punctuation.

The exported video is:

1920 × 1080 Full HD
30 FPS
Green-screen background: #126e47
White text with a black shadow
MP4 format
Ready for chroma-key editing in video editors such as Premiere Pro, CapCut, or DaVinci Resolve.
✨ Key Features
🌍 Multilingual Support — 67 Languages

Supports a wide range of writing systems, including:

Latin
Cyrillic
Chinese
Japanese
Korean
Arabic
Persian
Urdu
Bengali
Hindi
Thai
Burmese
Amharic
Armenian
Mongolian
and more.

The application automatically selects typography settings according to the selected language.

⏱️ Adjustable Reading Pace — ±50%

Use the built-in slider to make the subtitle sequence faster or slower by up to 50%.

This makes it easier to synchronize the generated video with an existing voiceover.

👁️ Live Preview

Preview the subtitle animation before rendering the final video.

Controls include:

Play
Pause
Restart
Timeline navigation
Subtitle block navigation
📝 Automatic Text Formatting

The application:

Reads the .txt file.
Removes unnecessary blank lines.
Formats the text.
Wraps it into subtitle lines.
Groups the lines into subtitle blocks.
⏸️ Punctuation-Based Timing

Reading pauses are automatically calculated according to punctuation such as:

Periods
Commas
Question marks
Exclamation marks
Other supported punctuation
Line breaks
🎬 Local MP4 Rendering

The video is rendered locally on your computer using OpenCV and Pillow.

No cloud processing is required and no watermark is added by the application.

🛠️ How It Works
1. Select a language

Choose the language of your text from the language menu.

2. Load a TXT file

Select a plain-text .txt file containing your script.

3. Adjust the reading pace

Use the ±50% slider if you need to make the final video faster or slower.

4. Preview

Use the live preview to check the subtitle animation.

5. Export

Click:

🎬 EXPORT TO MP4

The application creates a Full HD MP4 ready for your video-editing workflow.

💻 Running from Source

If you want to run the Python source code instead of the Windows executable:

Requirements
Python 3
OpenCV
NumPy
Pillow

Install the required libraries:

pip install opencv-python numpy Pillow

Run:

python Subtitletomp4.py
📦 Windows Executable

The Windows version is distributed as a ZIP package containing the compiled executable.

Python is not required when using the compiled Windows version.

Download the latest version from the Releases section.

👨‍💻 Credits

Developed by José Galindo

GABRIELS.WORK

Website: https://gabriels.work

© 2026 José Galindo. All rights reserved.
