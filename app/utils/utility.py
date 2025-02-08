import re


def regex_cleaners(video_title: str) -> str:
    # Remove parenthesis substr ie (Official music vid)
    if "(" in video_title and ")" in video_title:
        video_title = re.sub(r"\s?\(.*?\)", "", video_title)

    # Remove brackets
    if "[" in video_title and "]" in video_title:
        video_title = re.sub(r"\s?\[.*?\]", "", video_title)

    # Remove numbered songs
    if video_title[0].isdigit() and "." in video_title:
        video_title = re.sub(r"^\d+\.\s?", "", video_title)

    return video_title


def sanitize_start(value: str) -> str:
    """
    Santize song title and artist name, so that they don't start with invalid characters.
    For creating files later without error.
    """
    INVALID_CHARS = set('<>:"/\\|?*.')
    while value and value[0] in INVALID_CHARS:
        value = value[1:]
    return value
