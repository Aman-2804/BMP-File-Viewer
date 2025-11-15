# CMPT 365 Programming Assignment 2

## Overview
This assignment extends the BMP viewer from PA1 with lossless image compression capabilities using Huffman Coding. The program can compress BMP images into a custom `.cmpt365` format and decompress them back to display the original image.

## Features
- **BMP Image Viewer**: View BMP images with brightness, scale, and RGB channel controls (from PA1)
- **Huffman Coding Compression**: Lossless compression algorithm implemented from scratch
- **Custom .cmpt365 Format**: Compressed image format with metadata and code tables
- **Compression Statistics**: Display original size, compressed size, compression ratio, and compression time
- **Decompression**: Open and display .cmpt365 files

## Files
- `bmp.py`: Main GUI application with BMP viewer and compression/decompression features
- `huffman.py`: Huffman Coding implementation (tree building, encoding, decoding)
- `compression.py`: CMPT365 file format handling (compression/decompression)
- `generate_csv.py`: Script to batch process sample images and generate CSV results
- `csv_template.csv`: Results template filled with compression statistics

## Usage

### Running the Application
```bash
python3 bmp.py
```

### Compressing an Image
1. Click "Open BMP" to load a BMP image
2. Click "Compress & Save" to compress and save as .cmpt365 file
3. Compression statistics will be displayed

### Decompressing an Image
1. Click "Open .cmpt365" to load a compressed file
2. The image will be decompressed and displayed automatically

### Generating CSV Results
```bash
python3 generate_csv.py
```
This will process all images in `PA2_sample_input/` and update `csv_template.csv` with compression statistics.

## Compression Algorithm
The implementation uses **Huffman Coding**, a lossless compression algorithm that:
- Builds a frequency table of byte values in the image
- Constructs a Huffman tree based on frequencies
- Generates variable-length codes (more frequent bytes get shorter codes)
- Encodes the image data using these codes

## .cmpt365 File Format
The custom format structure:
- Magic number: "CMPT365" (7 bytes)
- Version: 1 (1 byte)
- Metadata: Original size, width, height, BPP (14 bytes)
- Code table: Serialized Huffman code table
- Padding: Number of padding bits (1 byte)
- Compressed data: Huffman-encoded image bytes

## Requirements
- Python 3.x
- numpy
- PIL/Pillow
- tkinter (usually included with Python)

## Notes
- Small images may have compression ratios < 1.0 due to code table overhead
- The algorithm works best on images with repeated patterns
- All BMP formats supported by PA1 are supported (1, 4, 8, 24-bit)

