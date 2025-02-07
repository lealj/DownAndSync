import datetime
from PyQt6.QtGui import QTextCursor


class OutputStream:
    """
    Custom stream to redirect stdout to a QTextEdit widget.
    """

    def __init__(self, text_edit, original_stream):
        self.text_edit = text_edit
        self.original_stream = original_stream

    def write(self, message: str):
        if message.strip():
            # Write to the QTextEdit 'terminal' widget
            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            self.text_edit.append(f"{timestamp} {message.strip()}")
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

            # Also write to the original stream (terminal)
            if not message.endswith("\n"):
                message += "\n"
            self.original_stream.write(message)

    def flush(self):
        self.original_stream.flush()
