from local_scanner import LocalScanner


class CategorySelector:

    @staticmethod
    def select(categories, stats):

        print("\n")
        print("=" * 50)
        print("FILE CATEGORIES")
        print("=" * 50)

        mapping = {
            "1": "photos",
            "2": "videos",
            "3": "documents",
            "4": "other"
        }

        print(
            f"[1] Photos "
            f"({stats['photos']['count']:,} files "
            f"{LocalScanner.format_size(stats['photos']['size'])})"
        )

        print(
            f"[2] Videos "
            f"({stats['videos']['count']:,} files "
            f"{LocalScanner.format_size(stats['videos']['size'])})"
        )

        print(
            f"[3] Documents "
            f"({stats['documents']['count']:,} files "
            f"{LocalScanner.format_size(stats['documents']['size'])})"
        )

        print(
            f"[4] Other "
            f"({stats.get('other', {'count': 0})['count']:,} files "
            f"{LocalScanner.format_size(stats['other']['size'])})"
        )

        print("\nA - Select All")
        print("Q - Quit")

        choice = input(
            "\nSelect categories: "
        ).strip().upper()

        if choice == "Q":
            return None

        if choice == "A":
            selected = []
            for category_files in categories.values():
                selected.extend(category_files)
            return selected

        selected_files = []

        for item in choice.split(","):
            item = item.strip()
            if item in mapping:
                selected_files.extend(
                    categories[mapping[item]]
                )

        return selected_files