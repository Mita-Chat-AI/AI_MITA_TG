import io
import requests

from pydub import AudioSegment

from ...config_reader import config

class ASR:
    def __init__(self, audio_bytes):
        self.audio_bytes = audio_bytes
    
    async def recognition(self) -> dict:
        audio = AudioSegment.from_file(self.audio_bytes, format="ogg")
        wav_bytes = io.BytesIO()
        audio.export(wav_bytes, format="wav")
        wav_bytes.seek(0)

        files = {'audio_file': wav_bytes.getvalue()}
        response = requests.post(
            url=config.asr_api.get_secret_value(),
            files=files,
            proxies={'http': config.socks_proxy.get_secret_value()}
        )
        response.raise_for_status()

        result = response.json()

        print(f'result: {result} {response}')
        return result