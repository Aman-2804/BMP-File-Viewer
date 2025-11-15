import tkinter as tk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk
import numpy as np
import struct
import os
import heapq
from collections import Counter
import time

class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCoding:
    def __init__(self):
        self.codes = {}
        self.reverse_codes = {}
    
    def build_tree(self, data):
        """Build Huffman tree from frequency analysis"""
        frequency = Counter(data)
        
        if len(frequency) == 0:
            return None
        
        if len(frequency) == 1:
            char = list(frequency.keys())[0]
            node = HuffmanNode(char, frequency[char])
            return node
        
        heap = []
        for char, freq in frequency.items():
            heapq.heappush(heap, HuffmanNode(char, freq))
        
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, merged)
        
        return heap[0] if heap else None
    
    def generate_codes(self, root, code=""):
        """Generate Huffman codes from tree"""
        if root is None:
            return
        
        if root.char is not None:
            if code == "":
                code = "0"
            self.codes[root.char] = code
            self.reverse_codes[code] = root.char
            return
        
        self.generate_codes(root.left, code + "0")
        self.generate_codes(root.right, code + "1")
    
    def compress(self, data):
        """Compress data using Huffman coding"""
        if len(data) == 0:
            return b'', {}, 0
        
        root = self.build_tree(data)
        self.codes = {}
        self.reverse_codes = {}
        self.generate_codes(root)
        
        encoded_bits = ''.join([self.codes[byte] for byte in data])
        
        padding = 8 - (len(encoded_bits) % 8)
        if padding == 8:
            padding = 0
        encoded_bits += '0' * padding
        
        compressed_bytes = bytearray()
        for i in range(0, len(encoded_bits), 8):
            byte = int(encoded_bits[i:i+8], 2)
            compressed_bytes.append(byte)
        
        code_table = self.codes.copy()
        
        return bytes(compressed_bytes), code_table, padding
    
    def decompress(self, compressed_data, code_table, padding):
        """Decompress data using Huffman coding"""
        if len(compressed_data) == 0:
            return b''
        
        self.reverse_codes = {v: k for k, v in code_table.items()}
        
        bit_string = ''.join([format(byte, '08b') for byte in compressed_data])
        
        if padding > 0:
            bit_string = bit_string[:-padding]
        
        decoded = bytearray()
        current_code = ""
        
        for bit in bit_string:
            current_code += bit
            if current_code in self.reverse_codes:
                decoded.append(self.reverse_codes[current_code])
                current_code = ""
        
        return bytes(decoded)
    
    def serialize_code_table(self, code_table):
        """Serialize code table to bytes"""
        data = bytearray()
        data.extend(struct.pack('<I', len(code_table)))
        
        for byte_val, code in code_table.items():
            data.append(byte_val)
            code_bytes = int(code, 2).to_bytes((len(code) + 7) // 8, 'big')
            data.append(len(code_bytes))
            data.extend(code_bytes)
            data.append(len(code))
        
        return bytes(data)
    
    def deserialize_code_table(self, data):
        """Deserialize code table from bytes"""
        if len(data) < 4:
            return {}
        
        num_entries = struct.unpack('<I', data[:4])[0]
        code_table = {}
        offset = 4
        
        for _ in range(num_entries):
            if offset >= len(data):
                break
            byte_val = data[offset]
            offset += 1
            
            if offset >= len(data):
                break
            code_bytes_len = data[offset]
            offset += 1
            
            if offset + code_bytes_len > len(data):
                break
            code_bytes = data[offset:offset+code_bytes_len]
            offset += code_bytes_len
            
            if offset >= len(data):
                break
            bit_length = data[offset]
            offset += 1
            
            bit_string = bin(int.from_bytes(code_bytes, 'big'))[2:]
            bit_string = bit_string.zfill(bit_length)
            code_table[byte_val] = bit_string
        
        return code_table

class CMPT365Compressor:
    """Handles compression and decompression of BMP images to .cmpt365 format"""
    
    MAGIC_NUMBER = b'CMPT365'
    VERSION = 1
    
    def __init__(self):
        self.huffman = HuffmanCoding()
    
    def compress_bmp(self, bmp_bytes, image_data, metadata):
        """Compress BMP image data to .cmpt365 format"""
        pixel_bytes = image_data.tobytes()
        
        compressed_data, code_table, padding = self.huffman.compress(pixel_bytes)
        
        code_table_bytes = self.huffman.serialize_code_table(code_table)
        
        cmpt365_data = bytearray()
        cmpt365_data.extend(self.MAGIC_NUMBER)
        cmpt365_data.append(self.VERSION)
        cmpt365_data.extend(struct.pack('<I', metadata['size']))
        cmpt365_data.extend(struct.pack('<I', metadata['width']))
        cmpt365_data.extend(struct.pack('<I', metadata['height']))
        cmpt365_data.extend(struct.pack('<H', metadata['bpp']))
        cmpt365_data.extend(struct.pack('<I', len(code_table_bytes)))
        cmpt365_data.extend(code_table_bytes)
        cmpt365_data.append(padding)
        cmpt365_data.extend(struct.pack('<I', len(compressed_data)))
        cmpt365_data.extend(compressed_data)
        
        return bytes(cmpt365_data)
    
    def decompress_cmpt365(self, cmpt365_bytes):
        """Decompress .cmpt365 file to image data and metadata"""
        if len(cmpt365_bytes) < 7:
            raise ValueError("Invalid .cmpt365 file: too short")
        
        if cmpt365_bytes[:7] != self.MAGIC_NUMBER:
            raise ValueError("Invalid .cmpt365 file: wrong magic number")
        
        offset = 7
        
        version = cmpt365_bytes[offset]
        offset += 1
        
        if version != self.VERSION:
            raise ValueError(f"Unsupported .cmpt365 version: {version}")
        
        original_size = struct.unpack('<I', cmpt365_bytes[offset:offset+4])[0]
        offset += 4
        width = struct.unpack('<I', cmpt365_bytes[offset:offset+4])[0]
        offset += 4
        height = struct.unpack('<I', cmpt365_bytes[offset:offset+4])[0]
        offset += 4
        bpp = struct.unpack('<H', cmpt365_bytes[offset:offset+2])[0]
        offset += 2
        
        metadata = {
            'size': original_size,
            'width': width,
            'height': height,
            'bpp': bpp
        }
        
        code_table_size = struct.unpack('<I', cmpt365_bytes[offset:offset+4])[0]
        offset += 4
        code_table_bytes = cmpt365_bytes[offset:offset+code_table_size]
        offset += code_table_size
        
        code_table = self.huffman.deserialize_code_table(code_table_bytes)
        
        padding = cmpt365_bytes[offset]
        offset += 1
        
        compressed_size = struct.unpack('<I', cmpt365_bytes[offset:offset+4])[0]
        offset += 4
        compressed_data = cmpt365_bytes[offset:offset+compressed_size]
        
        pixel_bytes = self.huffman.decompress(compressed_data, code_table, padding)
        
        image_data = np.frombuffer(pixel_bytes, dtype=np.uint8)
        image_data = image_data.reshape((height, width, 3))
        
        return image_data, metadata

class BMPViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("BMP Viewer")

        self.metadata_label = tk.Label(root, text="Metadata: ", anchor="w", justify="left", font=("Arial", 10))
        self.metadata_label.pack(fill=tk.X, padx=5, pady=5)

        self.canvas = Canvas(root, width=500, height=500, bg='gray')
        self.canvas.pack(padx=5, pady=5)

        self.btn_open = tk.Button(root, text="Open BMP / .cmpt365", command=self.load_bmp)
        self.btn_open.pack(padx=5, pady=5)

        self.brightness_slider = tk.Scale(root, from_=0, to=100, orient="horizontal",
                                             label="Brightness", command=self.adjust_brightness)
        self.brightness_slider.set(100) 
        self.brightness_slider.pack(padx=5, pady=5)

        self.scale_slider = tk.Scale(root, from_=10, to=100, orient="horizontal",
                                     label="Scale (%)", command=self.scale_image)
        self.scale_slider.set(100)  
        self.scale_slider.pack(padx=5, pady=5)

        self.r_btn = tk.Button(root, text="Toggle R", command=lambda: self.toggle_channel(0))
        self.r_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.g_btn = tk.Button(root, text="Toggle G", command=lambda: self.toggle_channel(1))
        self.g_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.b_btn = tk.Button(root, text="Toggle B", command=lambda: self.toggle_channel(2))
        self.b_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.image_data = None  
        self.original_data = None  
        self.metadata = {}  
        self.active_channels = [True, True, True]
        self.bmp_bytes = None
        self.compressor = CMPT365Compressor()
        
        self.stats_label = tk.Label(root, text="Compression Stats: None", anchor="w", justify="left", font=("Arial", 9))
        self.stats_label.pack(fill=tk.X, padx=5, pady=2)
        
        self.btn_compress = tk.Button(root, text="Compress & Save", command=self.compress_and_save)
        self.btn_compress.pack(padx=5, pady=5)
        
        self.btn_open_compressed = tk.Button(root, text="Open & Decompress .cmpt365", command=self.load_compressed)
        self.btn_open_compressed.pack(padx=5, pady=5)  

    def load_bmp(self):
        file_path = filedialog.askopenfilename(filetypes=[("BMP Files", "*.bmp"), ("CMPT365 Files", "*.cmpt365"), ("All Files", "*.*")])
        if not file_path:
            return

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        try:
            if file_path.lower().endswith('.cmpt365') or file_bytes[:7] == b'CMPT365':
                self.load_compressed_file(file_path, file_bytes)
            else:
                self.bmp_bytes = file_bytes
                self.metadata = self.parse_metadata(file_bytes)
                metadata_text = (
                    f"File Size: {self.metadata['size']} bytes\n"
                    f"Width: {self.metadata['width']} px\n"
                    f"Height: {self.metadata['height']} px\n"
                    f"BPP: {self.metadata['bpp']}"
                )
                self.metadata_label.config(text=metadata_text)

                self.image_data = self.parse_bitmap(file_bytes)
                self.original_data = np.copy(self.image_data)
                self.display_image()
                self.stats_label.config(text="Compression Stats: None")
        except ValueError as e:
            messagebox.showerror("Unsupported Format", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def parse_metadata(self, bmp_bytes):
        file_size = int.from_bytes(bmp_bytes[2:6], 'little')
        width = int.from_bytes(bmp_bytes[18:22], 'little')
        height = int.from_bytes(bmp_bytes[22:26], 'little')
        bpp = int.from_bytes(bmp_bytes[28:30], 'little')
        return {"size": file_size, "width": width, "height": height, "bpp": bpp}

    def parse_bitmap(self, bmp_bytes):
        offset = int.from_bytes(bmp_bytes[10:14], 'little')
        width, height = self.metadata["width"], abs(self.metadata["height"])
        bpp = self.metadata["bpp"]

        if bpp == 24:
            return self.parse_24bit_bmp(bmp_bytes, offset, width, height)
        elif bpp == 8:
            return self.parse_8bit_bmp(bmp_bytes, offset, width, height)
        elif bpp == 4:
            return self.parse_4bit_bmp(bmp_bytes, offset, width, height)
        elif bpp == 1:
            return self.parse_1bit_bmp(bmp_bytes, offset, width, height)
        else:
            raise ValueError(f"Unsupported BMP format with {bpp}-bit depth")

    def parse_24bit_bmp(self, bmp_bytes, offset, width, height):
        row_size = ((24 * width + 31) // 32) * 4
        pixel_data = bmp_bytes[offset:]
        img = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            row_start = y * row_size
            for x in range(width):
                byte_index = row_start + x * 3
                b, g, r = pixel_data[byte_index:byte_index+3]
                img[height - 1 - y, x] = [r, g, b]
        return img

    def parse_8bit_bmp(self, bmp_bytes, offset, width, height):
        color_table_offset = 54
        color_table_size = 256 * 4
        color_table_bytes = bmp_bytes[color_table_offset:color_table_offset+color_table_size]
        colors = []
        for i in range(0, len(color_table_bytes), 4):
            b, g, r, _ = color_table_bytes[i:i+4]
            colors.append((r, g, b))
        row_size = ((8 * width + 31) // 32) * 4
        pixel_data = bmp_bytes[offset:]
        img = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            row_start = y * row_size
            for x in range(width):
                pixel_index = pixel_data[row_start + x]
                img[height - 1 - y, x] = colors[pixel_index]
        return img

    def parse_4bit_bmp(self, bmp_bytes, offset, width, height):
        color_table_offset = 54
        color_table_size = 16 * 4  
        color_table_bytes = bmp_bytes[color_table_offset:color_table_offset+color_table_size]
        colors = []
        for i in range(0, len(color_table_bytes), 4):
            b, g, r, _ = color_table_bytes[i:i+4]
            colors.append((r, g, b))
        row_size = ((4 * width + 31) // 32) * 4
        pixel_data = bmp_bytes[offset:]
        img = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            row_start = y * row_size
            for x in range(width):
                byte_index = row_start + (x // 2)
                if x % 2 == 0:
                    pixel_index = (pixel_data[byte_index] >> 4) & 0x0F
                else:
                    pixel_index = pixel_data[byte_index] & 0x0F
                img[height - 1 - y, x] = colors[pixel_index]
        return img

    def parse_1bit_bmp(self, bmp_bytes, offset, width, height):
        color_table = [(0, 0, 0), (255, 255, 255)]
        row_size = ((width + 31) // 32) * 4
        pixel_data = bmp_bytes[offset:]
        img = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            row_start = y * row_size
            for x in range(width):
                byte_index = row_start + (x // 8)
                bit_index = 7 - (x % 8)
                pixel_index = (pixel_data[byte_index] >> bit_index) & 1
                img[height - 1 - y, x] = color_table[pixel_index]
        return img

    def display_image(self):
        if self.image_data is None:
            return

        img = np.copy(self.image_data)
        for i in range(3):
            if not self.active_channels[i]:
                img[:, :, i] = 0

        pil_img = Image.fromarray(img)
        self.tk_img = ImageTk.PhotoImage(pil_img)

        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = (canvas_width - pil_img.width) // 2
        y = (canvas_height - pil_img.height) // 2
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.tk_img)

    def adjust_brightness(self, value):
        factor = int(value) / 100.0
        self.image_data = np.clip(self.original_data * factor, 0, 255).astype(np.uint8)
        self.display_image()

    def scale_image(self, value):
        scale = int(value) / 100.0
        height, width, _ = self.original_data.shape
        new_height, new_width = int(height * scale), int(width * scale)
        resized_img = np.zeros((new_height, new_width, 3), dtype=np.uint8)
        for y in range(new_height):
            for x in range(new_width):
                orig_x, orig_y = int(x / scale), int(y / scale)
                resized_img[y, x] = self.original_data[min(orig_y, height-1), min(orig_x, width-1)]
        self.image_data = resized_img
        self.display_image()

    def toggle_channel(self, channel):
        self.active_channels[channel] = not self.active_channels[channel]
        self.display_image()
    
    def compress_and_save(self):
        """Compress the current BMP image and save as .cmpt365 file"""
        if self.image_data is None or self.bmp_bytes is None:
            messagebox.showwarning("No Image", "Please open a BMP image first.")
            return
        
        start_time = time.time()
        
        try:
            compressed_data = self.compressor.compress_bmp(
                self.bmp_bytes, self.original_data, self.metadata
            )
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".cmpt365",
                filetypes=[("CMPT365 Files", "*.cmpt365"), ("All Files", "*.*")]
            )
            
            if not file_path:
                return
            
            with open(file_path, "wb") as f:
                f.write(compressed_data)
            
            compression_time = (time.time() - start_time) * 1000
            
            original_size = self.metadata['size']
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
            
            stats_text = (
                f"Original Size: {original_size:,} bytes | "
                f"Compressed Size: {compressed_size:,} bytes | "
                f"Ratio: {compression_ratio:.2f}:1 | "
                f"Time: {compression_time:.2f} ms"
            )
            self.stats_label.config(text=stats_text)
            
            messagebox.showinfo("Success", f"Image compressed and saved successfully!\n\n{stats_text}")
            
        except Exception as e:
            messagebox.showerror("Compression Error", f"An error occurred during compression:\n{str(e)}")
    
    def load_compressed_file(self, file_path, cmpt365_bytes):
        """Internal method to load and decompress a .cmpt365 file"""
        image_data, metadata = self.compressor.decompress_cmpt365(cmpt365_bytes)
        
        self.image_data = image_data
        self.original_data = np.copy(image_data)
        self.metadata = metadata
        self.bmp_bytes = None
        
        metadata_text = (
            f"File Size: {metadata['size']} bytes\n"
            f"Width: {metadata['width']} px\n"
            f"Height: {metadata['height']} px\n"
            f"BPP: {metadata['bpp']}"
        )
        self.metadata_label.config(text=metadata_text)
        
        self.brightness_slider.set(100)
        self.scale_slider.set(100)
        self.active_channels = [True, True, True]
        
        self.display_image()
        
        compressed_size = len(cmpt365_bytes)
        original_size = metadata['size']
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
        stats_text = (
            f"Original Size: {original_size:,} bytes | "
            f"Compressed Size: {compressed_size:,} bytes | "
            f"Ratio: {compression_ratio:.2f}:1"
        )
        self.stats_label.config(text=stats_text)
    
    def load_compressed(self):
        """Load and decompress a .cmpt365 file"""
        file_path = filedialog.askopenfilename(filetypes=[("CMPT365 Files", "*.cmpt365"), ("All Files", "*.*")])
        if not file_path:
            return
        
        try:
            with open(file_path, "rb") as f:
                cmpt365_bytes = f.read()
            
            self.load_compressed_file(file_path, cmpt365_bytes)
            
        except Exception as e:
            messagebox.showerror("Decompression Error", f"An error occurred during decompression:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BMPViewer(root)
    root.mainloop()
