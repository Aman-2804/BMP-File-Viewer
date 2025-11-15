# BMP File Viewer

A Python application for viewing and compressing BMP images with a graphical user interface. The viewer supports multiple BMP formats and includes lossless compression using Huffman coding algorithm.

## Features

### Image Viewing
- **Multi-format BMP Support**: View BMP images with 1-bit, 4-bit, 8-bit, and 24-bit color depths
- **Interactive Display**: Canvas-based image viewer with automatic centering
- **Brightness Control**: Adjustable brightness slider (0-100%)
- **Image Scaling**: Zoom in/out with scale slider (10-100%)
- **RGB Channel Toggle**: Enable/disable individual Red, Green, and Blue color channels
- **Metadata Display**: Shows file size, dimensions, and bits per pixel (BPP)

### Compression & Decompression
- **Huffman Coding**: Lossless compression algorithm implemented from scratch
- **Custom .cmpt365 Format**: Compressed image format with embedded metadata
- **Compression Statistics**: Real-time display of original size, compressed size, compression ratio, and processing time
- **Seamless Decompression**: Open and view compressed .cmpt365 files directly

## How It Works

The application parses BMP file headers and pixel data, displaying images using PIL/Pillow. For compression, it implements Huffman coding:
1. Analyzes byte frequencies in the image pixel data
2. Builds a Huffman tree based on frequency distribution
3. Generates variable-length codes (shorter codes for more frequent bytes)
4. Encodes the image data and stores it in a custom .cmpt365 format

The .cmpt365 format preserves all original image metadata (width, height, BPP) along with the Huffman code table and compressed pixel data.

## Installation

### Prerequisites
- Python 3.x
- Required packages:
  ```bash
  pip install numpy pillow
  ```

Note: `tkinter` is typically included with Python installations.

## Usage

### Running the Application
```bash
python bmp.py
```

### Viewing BMP Images
1. Click **"Open BMP / .cmpt365"** button
2. Select a BMP file from the file dialog
3. The image will be displayed with metadata shown at the top
4. Use the sliders and channel buttons to adjust the image

### Compressing Images
1. Open a BMP image using the "Open BMP / .cmpt365" button
2. Click **"Compress & Save"** button
3. Choose a location and filename for the .cmpt365 file
4. Compression statistics will be displayed automatically

### Decompressing Images
1. Click **"Open & Decompress .cmpt365"** button (or use "Open BMP / .cmpt365")
2. Select a .cmpt365 file
3. The image will be decompressed and displayed immediately
4. Compression statistics from the original compression are shown

## Controls

- **Brightness Slider**: Adjusts image brightness from 0% (black) to 100% (original)
- **Scale Slider**: Resizes the image from 10% to 100% of original size
- **Toggle R/G/B Buttons**: Enable or disable individual color channels
- **Open BMP / .cmpt365**: Loads BMP or compressed .cmpt365 files
- **Compress & Save**: Compresses the currently loaded BMP and saves as .cmpt365
- **Open & Decompress .cmpt365**: Loads and decompresses .cmpt365 files

## Sample Images

The project includes sample BMP images in various formats:
- `BIOS.bmp`, `earth.bmp`, `Fall.bmp`: 24-bit color images
- `nature.bmp`, `nature_2.bmp`: Various color depths
- `pal1.bmp`, `pal1bg.bmp`, `pal4.bmp`, `pal8gs.bmp`: Palette-based images

## Technical Details

### Supported BMP Formats
- **1-bit**: Monochrome images with 2 colors
- **4-bit**: 16-color palette images
- **8-bit**: 256-color palette images
- **24-bit**: True color RGB images

### Compression Performance
- Compression ratio depends on image content and patterns
- Images with repeated patterns achieve better compression
- Small images may have ratios < 1.0 due to code table overhead
- Compression is fully lossless - original image data is perfectly restored

## Project Structure

```
bmp viewer/
├── bmp.py              # Main application (GUI and compression/decompression)
├── README.md           # This file
└── sample inputs/      # Sample BMP images for testing
    ├── BIOS.bmp
    ├── earth.bmp
    ├── Fall.bmp
    └── ... (other sample images)
```

## Implementation Highlights

- **Huffman Coding**: Custom implementation of Huffman tree construction and encoding/decoding
- **File Format Parsing**: Manual parsing of BMP headers and pixel data
- **GUI Framework**: Built with Tkinter for cross-platform compatibility
- **NumPy Integration**: Efficient pixel data manipulation and processing
- **Custom Compression Format**: Binary file format with structured header and data sections

## License

This project is open source and available for educational purposes.
