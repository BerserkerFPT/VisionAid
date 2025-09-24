"""
Demo sử dụng vision_to_speech.py
"""
from vision_to_speech import VTS

def main():
    # Khởi tạo với API keys (thay thế bằng API keys thực tế)
    vts = VTS(
        gemini_api_key="AIzaSyBrlp7XaKUwZTjGJovioB08Dw3KgnDdnKQ",  # API key từ EXE.ipynb
        fpt_api_key="OCAAgYnKtkjwxWYDgnvPwhQNyccmEkca",          # API key từ EXE.ipynb
        voice="banmai"
    )
    
    # Đường dẫn ảnh từ EXE.ipynb
    image_path = r"G:\My Drive\DSP391m\481191925_1249528846840541_6357321759927879116_n.jpg"
    output_path = "output.wav"
    
    print("🚀 Starting image to speech conversion...")
    
    # Chuyển đổi ảnh thành âm thanh
    result = vts.convert(
        image_path=image_path,
        output_wav_path=output_path,
        wait_time=10
    )
    
    # Hiển thị kết quả
    if result["success"]:
        print("\n" + "="*50)
        print("✅ CONVERSION COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"📄 Analysis Result:")
        print(result['text_result'])
        print(f"\n🔊 Audio saved to: {result['audio_path']}")
        print(f"🎵 Voice used: {result['voice_used']}")
        print(f"🔗 Audio URL: {result['audio_url']}")
    else:
        print("\n" + "="*50)
        print("❌ CONVERSION FAILED!")
        print("="*50)
        print(f"Error: {result['error']}")
    
    print("\n🎯 Demo completed!")

if __name__ == "__main__":
    main()