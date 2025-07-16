from io import BytesIO

import soundfile as sf
from pedalboard import Pedalboard, Convolution, Reverb


async def apply_effects(audio_bytes: bytes) -> bytes:
    audio, sr = sf.read(BytesIO(audio_bytes))

    board = Pedalboard(
        [
            Reverb(
                room_size=0.001,
                damping=0.8,
                wet_level=0.1
                )
        ]
    )

    effect = board(audio, sample_rate=sr)
    
    buffer = BytesIO()
    sf.write(buffer, effect, sr, format='MP3')
    return buffer.getvalue()