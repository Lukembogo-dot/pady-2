import os
import socket
import sys
import shutil

from local_scanner import LocalScanner
from category_selector import CategorySelector
from file_filter import FileFilter
from backup_estimator import BackupEstimator
from estimate_ui import EstimateUI
from archive_namer import ArchiveNamer
from streaming_zip import StreamingZipEngine


def get_stick_destination():
    """
    Returns the folder the running script/exe lives in - this is the
    USB stick itself when run via the packaged .exe, or the project
    folder during development.
    """
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller-built exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def main():
    print("\nWelcome to Pady - Portable PC Backup Tool!\n")

    pc_name = socket.gethostname()
    print(f"This PC: {pc_name}")
    print(f"Current user: {os.environ.get('USERNAME', os.environ.get('USER', 'unknown'))}")

    scan_roots = LocalScanner.default_profile_folders()

    print("\nWill scan the following folders:")
    for folder in scan_roots:
        exists = "OK" if os.path.isdir(folder) else "NOT FOUND - skipping"
        print(f"  {folder}  [{exists}]")

    scanner = LocalScanner(scan_roots)

    if not scanner.scan_roots:
        print("\nNone of the expected profile folders were found. Aborting.")
        return

    all_files = scanner.get_all_files()
    print(f"\nDiscovered {len(all_files):,} files.")

    if not all_files:
        print("\nNo files found to back up.")
        return

    categories = scanner.categorize_files(all_files)
    stats = scanner.build_statistics(categories)

    selected_files = CategorySelector.select(categories, stats)

    if selected_files is None:
        print("\nBackup cancelled.")
        return

    if not selected_files:
        print("\nNo files selected.")
        return

    selected_files = FileFilter.prompt_and_apply(selected_files)

    if not selected_files:
        print("\nNothing left to back up after filtering.")
        return

    destination = get_stick_destination()
    print(f"\nBackup will be saved to:\n{destination}")

    free_space = shutil.disk_usage(destination).free
    print(
        f"\nAvailable free space on stick: "
        f"{LocalScanner.format_size(free_space)}"
    )

    archive_path = ArchiveNamer.generate(pc_name, destination)
    print(f"\nArchive will be created as:\n{archive_path}")

    print(f"\nSelected {len(selected_files):,} files.")
    print("\nFirst 10 files detected:")
    for file in selected_files[:10]:
        print(
            f"{LocalScanner.format_size(file['size'])}"
            f" -> "
            f"{file['path']}"
        )

    estimate = BackupEstimator.estimate(selected_files, destination)

    proceed = EstimateUI.display(estimate, destination)

    if not proceed:
        print("\nBackup cancelled.")
        return

    zipper = StreamingZipEngine(scan_roots)

    try:
        zipper.create_zip(selected_files, archive_path)
    except Exception as e:
        print(f"\nZIP Error: {e}")
        return

    print("Verifying archive integrity...")
    is_ok, detail = StreamingZipEngine.verify(archive_path)
    if not is_ok:
        print(f"\nWARNING: archive may be corrupted ({detail}).")
        print("Try running the backup again.")
        return

    print("\nBackup completed successfully.")
    print(f"Saved to: {archive_path}")


if __name__ == "__main__":
    main()