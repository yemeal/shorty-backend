import emoji
from typing import Annotated
from pydantic import AfterValidator

def validate_single_emoji(value: str) -> str:
    """Must be exactly one emoji (ZWJ sequences count as one). No extra text."""
    
    if emoji.emoji_count(value) != 1:
        raise ValueError("Field must contain exactly one emoji")
    
    
    if emoji.replace_emoji(value, replace="").strip() != "":
        raise ValueError("Field must contain only emoji, no text")
        
    return value

SingleEmoji = Annotated[str, AfterValidator(validate_single_emoji)]
