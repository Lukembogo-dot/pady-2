import os


class WorkspaceManager:
    @staticmethod
    def create(destination):
        temp_dir = os.path.join(
            destination,
            ".backup_temp"
        )
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    @staticmethod
    def cleanup(temp_dir):
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
