"""
Vision to Speech - Simple API for converting images to speech
Refactored from EXE.ipynb for easy reuse by backend developers
"""
import os
import time
import requests
from typing import Optional, Dict, Any
from google import genai
from google.genai import types


class VTS:
    """
    Vision to Speech - Convert images to audio files
    Simple API that takes image path and outputs WAV file
    """
    
    def __init__(self, gemini_api_key: str, fpt_api_key: str, voice: str = "banmai"):
        """
        Initialize VTS with API keys
        
        Args:
            gemini_api_key (str): Google Gemini API key
            fpt_api_key (str): FPT.AI TTS API key  
            voice (str): Voice for TTS (banmai, lannhi, myan, giahuy, minhquang, etc.)
        """
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.fpt_api_key = fpt_api_key
        self.voice = voice
        self.model = "gemini-2.5-flash"
        
        # Default prompt giống như trong EXE.ipynb
        self.prompt = """
Bạn là trợ lý hỗ trợ người khiếm thị.
Hãy phân loại ảnh thành một trong hai loại:
- [Tài liệu]: Nếu bức ảnh là tài liệu/trang giấy → OCR toàn bộ nội dung và format lại nội dung đó cho hoàn chỉnh, chỉnh chu và ngăn nắp, không tóm tắt.
- [Ngữ cảnh]: Nếu bức ảnh là cảnh vật/bối cảnh → chỉ cần miêu tả tóm tắt tổng thể.
Trả kết quả theo format:
Thể loại: [Tài liệu hoặc Ngữ cảnh]
Nội dung: <nội dung tương ứng>
"""
    
    def convert(self, image_path: str, output_wav_path: str, wait_time: int = 10) -> Dict[str, Any]:
        """
        Convert image to speech WAV file
        
        Args:
            image_path (str): Path to input image file
            output_wav_path (str): Path for output WAV file
            wait_time (int): Wait time for TTS generation (default: 10 seconds)
            
        Returns:
            Dict with success status and details
        """
        try:
            # Step 1: Analyze image with Gemini
            print("🔍 Analyzing image...")
            
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}",
                    "text_result": None,
                    "audio_path": None
                }
            
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            
            response = self.gemini_client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    self.prompt
                ]
            )
            
            text_result = response.text.strip()
            print(f"📄 Analysis result: {text_result[:100]}...")
            
            # Step 2: Convert text to speech with FPT.AI
            print("🔊 Converting to speech...")
            
            url = "https://api.fpt.ai/hmi/tts/v5"
            headers = {
                "api-key": self.fpt_api_key,
                "speed": "",
                "voice": self.voice
            }
            
            # Send TTS request
            tts_response = requests.post(url, data=text_result.encode("utf-8"), headers=headers)
            
            if tts_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"TTS API request failed: {tts_response.status_code}",
                    "text_result": text_result,
                    "audio_path": None
                }
            
            res_json = tts_response.json()
            
            if "async" not in res_json:
                return {
                    "success": False,
                    "error": "No audio URL in TTS response",
                    "text_result": text_result,
                    "audio_path": None,
                    "api_response": res_json
                }
            
            audio_url = res_json["async"]
            print(f"🔗 Audio URL: {audio_url}")
            
            # Wait for audio generation
            print(f"⏳ Waiting {wait_time} seconds for audio generation...")
            time.sleep(wait_time)
            
            # Download audio file
            audio_response = requests.get(audio_url)
            
            if audio_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to download audio: {audio_response.status_code}",
                    "text_result": text_result,
                    "audio_path": None
                }
            
            # Create output directory if needed
            output_dir = os.path.dirname(output_wav_path)
            if output_dir:  # Only create directory if output_dir is not empty
                os.makedirs(output_dir, exist_ok=True)
            
            # Save WAV file
            with open(output_wav_path, "wb") as f:
                f.write(audio_response.content)
            
            print(f"✅ Successfully saved audio to: {output_wav_path}")
            
            return {
                "success": True,
                "error": None,
                "text_result": text_result,
                "audio_path": output_wav_path,
                "audio_url": audio_url,
                "voice_used": self.voice
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "text_result": None,
                "audio_path": None
            }
    
    def set_voice(self, voice: str):
        """Change TTS voice"""
        self.voice = voice
    
    def set_prompt(self, prompt: str):
        """Change analysis prompt"""
        self.prompt = prompt


# Example usage:
if __name__ == "__main__":
    # Initialize with your API keys
    vts = VTS(
        gemini_api_key="YOUR_GEMINI_API_KEY", 
        fpt_api_key="YOUR_FPT_API_KEY",
        voice="banmai"
    )
    
    # Convert image to speech
    result = vts.convert(
        image_path="path/to/your/image.jpg",
        output_wav_path="output.wav"
    )
    
    if result["success"]:
        print("✅ Conversion completed!")
        print(f"📄 Text: {result['text_result']}")
        print(f"🔊 Audio: {result['audio_path']}")
    else:
        print(f"❌ Conversion failed: {result['error']}")