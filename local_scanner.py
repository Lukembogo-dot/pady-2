import os


class LocalScanner:
    PHOTO_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.heic', '.webp', '.bmp', '.gif', '.tiff'
    }
    VIDEO_EXTENSIONS = {
        '.mp4', '.mov', '.avi', '.mkv', '.webm', '.3gp', '.wmv'
    }
    DOCUMENT_EXTENSIONS = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.ppt', '.pptx', '.txt', '.csv', '.odt'
    }

    # Folders we never want to walk into, even if they live
    # inside one of the scan roots (junk, caches, version control, etc.)
    IGNORE_DIR_NAMES = {
        '.git', '__pycache__', 'node_modules',
        '$RECYCLE.BIN', 'System Volume Information',
        '.backup_temp'
    }

    def __init__(self, scan_roots):
        """
        scan_roots: list of absolute folder paths to scan,
        e.g. [Documents, Pictures, Desktop, Downloads]
        Non-existent paths are skipped silently (e.g. user has no Desktop folder).
        """
        self.scan_roots = [
            path for path in scan_roots if os.path.isdir(path)
        ]

    @staticmethod
    def default_profile_folders():
        """
        Returns the standard 'essential' folders for the current
        Windows user: Documents, Pictures, Desktop, Downloads.
        """
        home = os.path.expanduser("~")
        candidates = ["Documents", "Pictures", "Desktop", "Downloads"]
        return [os.path.join(home, name) for name in candidates]

    def get_all_files(self):
        print("\nScanning local folders...\n")
        files = []
        for root_folder in self.scan_roots:
            print(f"Scanning {root_folder} ...")
            for current_dir, dirs, filenames in os.walk(root_folder):
                # prune ignored directories in-place so os.walk skips them
                dirs[:] = [
                    d for d in dirs if d not in self.IGNORE_DIR_NAMES
                ]
                for filename in filenames:
                    full_path = os.path.join(current_dir, filename)
                    try:
                        size = os.path.getsize(full_path)
                    except OSError:
                        # file disappeared, permission denied, broken
                        # symlink, etc. - skip and keep going
                        continue
                    files.append({
                        "path": full_path,
                        "size": size
                    })
        return files

    def categorize_files(self, files):
        categorized = {
            "photos": [],
            "videos": [],
            "documents": [],
            "other": []
        }
        for file in files:
            extension = os.path.splitext(file["path"])[1].lower()
            if extension in self.PHOTO_EXTENSIONS:
                categorized["photos"].append(file)
            elif extension in self.VIDEO_EXTENSIONS:
                categorized["videos"].append(file)
            elif extension in self.DOCUMENT_EXTENSIONS:
                categorized["documents"].append(file)
            else:
                categorized["other"].append(file)
        return categorized

    def build_statistics(self, categories):
        stats = {}
        for category, files in categories.items():
            total_size = sum(file["size"] for file in files)
            stats[category] = {
                "count": len(files),
                "size": total_size
            }
        return stats

    @staticmethod
    def format_size(size):
        units = ["B", "KB", "MB", "GB", "TB"]
        for unit in units:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"