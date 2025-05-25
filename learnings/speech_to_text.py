
import io
import logging
import wave
import requests
from dotenv import load_dotenv
from livekit.agents import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    stt,
    utils,
)
from typing import Any

from livekit.agents.utils import AudioBuffer
from pydub import AudioSegment


load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")

class myClass(stt.STT):
    def __init__(
        self,
    ):
        super().__init__(
            capabilities=stt.STTCapabilities(streaming=False, interim_results=False)
        )

    async def _recognize_impl(
        self, buffer: AudioBuffer, *, language = None, conn_options = None
    ) -> stt.SpeechEvent:
        
        buffer = utils.merge_frames(buffer)
        io_buffer = io.BytesIO()
    
        with wave.open(io_buffer, "wb") as wav:
            wav.setnchannels(buffer.num_channels)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(buffer.sample_rate)
            wav.writeframes(buffer.data)

        # wav文件转为mp3格式
        mp3 = AudioSegment.from_wav(io_buffer)
        io_buffer = io.BytesIO()
        mp3.export(io_buffer, format="mp3")
        

        # 请求接口 对接funASR
        url = "http://test/asr"

        files = {'file': ('test.wav', io_buffer.getvalue(), 'audio/wav')}
        response = requests.post(url, files=files)
        resultText = response.json()["result"][0]["text"]

        logger.info(f"response: {resultText}")

        return stt.SpeechEvent(
            type=stt.SpeechEventType.FINAL_TRANSCRIPT,
            alternatives=[
                stt.SpeechData(text=resultText or "", language=language or "")
            ],
        )
   