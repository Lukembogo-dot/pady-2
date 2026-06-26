import os
from datetime import datetime, timedelta


class FileFilter:
    """
    Narrows down an already-categorized file selection so the backup
    fits on a smaller drive, without changing which categories were
    chosen. Three independent filters, all optional:

      - max_age_days: drop files older than N days (by modified time)
      - max_file_size_bytes: drop individual files bigger than this
        (mainly useful for video - a couple of huge files often
        account for most of a category's size)
      - exclude_substrings: drop any file whose path contains one of
        these substrings (e.g. a known junk folder)
    """

    @staticmethod
    def apply(
        selected_files,
        max_age_days=None,
        max_file_size_bytes=None,
        exclude_substrings=None
    ):
        exclude_substrings = exclude_substrings or []
        cutoff_date = None
        if max_age_days is not None:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)

        kept = []
        dropped_old = 0
        dropped_large = 0
        dropped_excluded = 0

        for file in selected_files:
            path = file["path"]

            if exclude_substrings and any(s in path for s in exclude_substrings):
                dropped_excluded += 1
                continue

            if max_file_size_bytes is not None and file["size"] > max_file_size_bytes:
                dropped_large += 1
                continue

            if cutoff_date is not None:
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(path))
                    if mtime < cutoff_date:
                        dropped_old += 1
                        continue
                except OSError:
                    # can't stat it, leave it out rather than guess
                    dropped_old += 1
                    continue

            kept.append(file)

        return {
            "kept": kept,
            "dropped_old": dropped_old,
            "dropped_large": dropped_large,
            "dropped_excluded": dropped_excluded
        }

    @staticmethod
    def prompt_and_apply(selected_files):
        """
        Simple interactive prompt for the common case. Returns the
        filtered file list. Any blank answer skips that filter.
        """
        print("\n" + "=" * 50)
        print("NARROW DOWN SELECTION (optional - press Enter to skip)")
        print("=" * 50)

        max_age_days = None
        age_input = input(
            "Only include files modified in the last N days "
            "(e.g. 180), or Enter to skip: "
        ).strip()
        if age_input:
            try:
                max_age_days = int(age_input)
            except ValueError:
                print("Ignoring invalid number, skipping age filter.")

        max_file_size_bytes = None
        size_input = input(
            "Skip individual files larger than N MB "
            "(e.g. 500), or Enter to skip: "
        ).strip()
        if size_input:
            try:
                max_file_size_bytes = int(size_input) * 1024 * 1024
            except ValueError:
                print("Ignoring invalid number, skipping size filter.")

        exclude_input = input(
            "Exclude paths containing (comma separated, e.g. node_modules,Temp), "
            "or Enter to skip: "
        ).strip()
        exclude_substrings = (
            [s.strip() for s in exclude_input.split(",") if s.strip()]
            if exclude_input else []
        )

        if not (max_age_days or max_file_size_bytes or exclude_substrings):
            return selected_files

        result = FileFilter.apply(
            selected_files,
            max_age_days=max_age_days,
            max_file_size_bytes=max_file_size_bytes,
            exclude_substrings=exclude_substrings
        )

        print(
            f"\nFiltered out: {result['dropped_old']:,} too old, "
            f"{result['dropped_large']:,} too large, "
            f"{result['dropped_excluded']:,} excluded by path."
        )
        print(f"Remaining: {len(result['kept']):,} files.")

        return result["kept"]