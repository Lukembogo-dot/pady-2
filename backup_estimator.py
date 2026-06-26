import shutil
import os


class BackupEstimator:
    @staticmethod
    def estimate(selected_files, destination):
        total_size = sum(
            file["size"] for file in selected_files
        )

        total_files = len(selected_files)
        if not os.path.exists(destination):
            os.makedirs(destination)

        free_space = shutil.disk_usage(destination).free
        gb = total_size / (1024 ** 3)

        min_time = max(1, round(gb / 4))
        max_time = max(2, round(gb / 2))

        return {
            "total_files": total_files,
            "total_size": total_size,
            "free_space": free_space,
            "min_time": min_time,
            "max_time": max_time,
            "enough_space": free_space >= total_size
        }