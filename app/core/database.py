import sqlite3


class DatabaseManager:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def create_table(self):
        """Create a table."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS songs (
                video_id TEXT PRIMARY KEY,
                artist TEXT NOT NULL,
                song_title TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def insert_songs(self, liked_videos: list):
        """Insert videos all at once (may be updated to batch)."""
        try:
            self.create_table()
            self.cursor.execute("BEGIN TRANSACTION")
            data = [
                (video["video_id"], video["artist"], video["song_title"])
                for video in liked_videos
            ]

            self.cursor.executemany(
                "INSERT OR IGNORE INTO songs (video_id, artist, song_title) VALUES (?, ?, ?)",
                data,
            )
            self.connection.commit()

        except sqlite3.IntegrityError as e:
            self.connection.rollback()

        except Exception as e:
            print("Error:", e)  # Handle other exceptions
            self.connection.rollback()

    def insert_song(self, v):
        try:
            data = (v["video_id"], v["artist"], v["song_title"])
            self.cursor.execute(
                "INSERT OR IGNORE INTO songs (video_id, artist, song_title) VALUES (?, ?, ?)",
                data,
            )
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            self.connection.rollback()
        except Exception as e:
            print("Error:", e)  # Handle other exceptions
            self.connection.rollback()

    def fetch_songs(self) -> list:
        """Fetch all users."""
        self.cursor.execute("SELECT * FROM songs")
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def exists(self, key: str) -> bool:
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM songs WHERE video_id= ?)", (key,)
        )
        exists = self.cursor.fetchone()[0]
        return bool(exists)

    def close(self):
        """Close the database connection."""
        self.connection.close()


# "Append a newly liked video to a table"
# Fetch all liked videos
