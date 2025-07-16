import re

from ..mitacore.memory import Memory


async def memory_chars(memory: Memory) -> int:
    user_chars = 0
    mita_chars = 0
    for item in memory:
        if item['role'] == 'user':
            user_chars += len(item['content'])
        elif item['role'] ==  'assistant':
            mita_chars += len(item['content'])
    return user_chars, mita_chars


def remove_unwanted_chars(text) -> str:
    pattern = re.compile(
        r'[^\w\s.,!?\-]|'              # разрешаем точку, запятую, восклицательный знак, тире
        r'[\U0001F600-\U0001F64F]|'    # emoji
        r'[\U0001F300-\U0001F5FF]|'
        r'[\U0001F680-\U0001F6FF]|'
        r'[\U0001F700-\U0001F77F]|'
        r'[\U0001F780-\U0001F7FF]|'
        r'[\U0001F800-\U0001F8FF]|'
        r'[\U0001F900-\U0001F9FF]|'
        r'[~Σ]|'                       # символы ~ и Σ
        r'\breactions\b|'              # слово reactions
        r'\btext\b|' 
        r'\bhtml\b|'     
        r'\bto player\b|'             
        r'smilestrange>|'
        r'smile>|'
        r'discontent>',
        flags=re.IGNORECASE
    )
    return pattern.sub('', text)

