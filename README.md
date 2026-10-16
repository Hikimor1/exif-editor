# EXIF Editor

Desktop GUI application for viewing and editing EXIF metadata in JPEG/HEIC images. Built with Python + Tkinter.

## Features

- 📷 **Edit EXIF fields**: camera make/model, lens, focal length, aperture, ISO, shutter speed, white balance, flash, etc.
- 🗺️ **GPS coordinates**: latitude, longitude, altitude, timestamp — edit manually or apply in batch
- 📅 **Date/time control**: set `DateTimeOriginal` and `DateTimeDigitized` precisely
- 📁 **Batch processing**: load multiple files, apply the same metadata to all with auto-incremented timestamps (+10 sec per file) and slightly randomized GPS coordinates
- 💾 **Output formats**: JPEG or HEIC (requires `pillow-heif`)
- 🔄 **Overwrite mode**: edit in place or save to a separate output directory
- 🖥️ **Dark-themed Tkinter UI** with a live log panel

## Installation

```bash
pip install -r requirements.txt

# Optional: HEIC support
pip install pillow-heif
```

> Requires Python 3.9+

## Usage

```bash
python exif_editor.py
```

Or build a standalone executable with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "EXIF Editor" exif_editor.py
```

## Dependencies

| Package | Purpose |
|---|---|
| `Pillow` | Image loading and saving |
| `piexif` | Reading and writing EXIF data |
| `pillow-heif` | HEIC/HEIF format support (optional) |
| `tkinter` | GUI (included with Python) |

## Notes

- When batch-processing, each file gets a timestamp offset of +10 seconds from the base time and a small random GPS jitter (~100–500 m) to produce unique but realistic metadata
- HEIC output requires `pillow-heif` to be installed; falls back to JPEG automatically if not found
- The app sets DPI awareness on Windows for a crisp UI on high-resolution displays
