import os
import shutil


class LocalCopyEngine:
    def __init__(self, scan_roots):
        """
        scan_roots: the same list of folders LocalScanner walked.
        Used to figure out a sensible relative path for each file
        (e.g. so a file under Documents/Projects/x.txt lands at
        temp_dir/Documents/Projects/x.txt, not flattened or absolute).
        """
        self.scan_roots = scan_roots

    def _relative_destination(self, source_path, temp_dir):
        for root in self.scan_roots:
            if os.path.commonpath([root, source_path]) == os.path.normpath(root):
                root_name = os.path.basename(os.path.normpath(root))
                relative = os.path.relpath(source_path, root)
                return os.path.join(temp_dir, root_name, relative)

        # Fallback: file wasn't under any known root (shouldn't normally
        # happen), so just drop it under its drive letter + path to avoid
        # collisions between files of the same name from different folders.
        drive, tail = os.path.splitdrive(source_path)
        tail = tail.lstrip("\\/")
        return os.path.join(temp_dir, drive.replace(":", ""), tail)

    def copy_files(self, selected_files, temp_dir):
        total_files = len(selected_files)
        failed = []

        for index, file in enumerate(selected_files, start=1):
            source = file["path"]
            destination = self._relative_destination(source, temp_dir)

            print(
                f"\rCopying {index:,}/{total_files:,}",
                end=""
            )

            try:
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.copy2(source, destination)
            except (OSError, shutil.Error) as e:
                failed.append((source, str(e)))
                continue

        print("\n")

        if failed:
            print(f"{len(failed):,} file(s) could not be copied:\n")
            for source, error in failed[:20]:
                print(f"  FAILED: {source}\n    -> {error}")
            if len(failed) > 20:
                print(f"  ...and {len(failed) - 20:,} more.")

        return failed
