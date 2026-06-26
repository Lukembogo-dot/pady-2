import os
import zipfile


class ZipEngine:

    @staticmethod
    def create_zip(source_dir, archive_path):
        with zipfile.ZipFile(
            archive_path,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, source_dir)
                    try:
                        zipf.write(full_path, arcname)
                    except Exception as e:
                        print(f"\nFailed:\n{full_path}")
                        print(e)
