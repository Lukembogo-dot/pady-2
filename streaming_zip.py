import os
import zipfile


class StreamingZipEngine:
    """
    Replaces the copy-to-temp-folder-then-zip flow. Each source file
    is read once and written straight into the archive - there is no
    intermediate full copy on disk, so peak space needed is roughly
    1x the backup size instead of 2x.

    Folder structure inside the zip mirrors the original scan roots,
    same as the old CopyEngine/ZipEngine combination did, e.g.:
        Documents/Projects/code.txt
        Pictures/photo1.jpg
    """

    def __init__(self, scan_roots):
        self.scan_roots = scan_roots

    def _arcname_for(self, source_path):
        for root in self.scan_roots:
            norm_root = os.path.normpath(root)
            if os.path.commonpath([norm_root, source_path]) == norm_root:
                root_name = os.path.basename(norm_root)
                relative = os.path.relpath(source_path, norm_root)
                return os.path.join(root_name, relative)

        # Fallback for a file outside any known root - keep drive +
        # path so files of the same name from different drives don't
        # collide inside the archive.
        drive, tail = os.path.splitdrive(source_path)
        tail = tail.lstrip("\\/")
        return os.path.join(drive.replace(":", ""), tail)

    def create_zip(self, selected_files, archive_path):
        total_files = len(selected_files)
        failed = []

        with zipfile.ZipFile(
            archive_path,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:
            for index, file in enumerate(selected_files, start=1):
                source = file["path"]
                arcname = self._arcname_for(source)

                print(f"\rCompressing {index:,}/{total_files:,}", end="")

                try:
                    zipf.write(source, arcname)
                except (OSError, PermissionError) as e:
                    failed.append((source, str(e)))
                    continue

        print("\n")

        if failed:
            print(f"{len(failed):,} file(s) could not be added to the archive:\n")
            for source, error in failed[:20]:
                print(f"  FAILED: {source}\n    -> {error}")
            if len(failed) > 20:
                print(f"  ...and {len(failed) - 20:,} more.")

        return failed

    @staticmethod
    def verify(archive_path):
        """
        Confirms the zip wasn't left corrupted/truncated (e.g. stick
        pulled mid-write, disk full partway through). Returns a tuple
        (is_ok, detail):
          - (True, None) if the archive is intact
          - (False, "<reason>") if it's corrupted or unreadable
        """
        try:
            with zipfile.ZipFile(archive_path, "r") as zipf:
                bad_file = zipf.testzip()
                if bad_file:
                    return False, f"corrupted entry: {bad_file}"
                return True, None
        except zipfile.BadZipFile as e:
            return False, f"not a valid zip file ({e})"
        except OSError as e:
            return False, f"could not be read ({e})"