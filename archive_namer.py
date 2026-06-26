from datetime import datetime
import os


class ArchiveNamer:
    @staticmethod
    def generate(label, destination):
        safe_label = (
            label.replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )
        date_part = datetime.now().strftime("%Y-%m-%d")
        counter = 1
        while True:
            filename = (
                f"{safe_label}_"
                f"{date_part}_"
                f"{counter:03d}.zip"
            )
            full_path = os.path.join(destination, filename)
            if not os.path.exists(full_path):
                return full_path
            counter += 1