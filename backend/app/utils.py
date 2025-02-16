import os
import shutil
import logging

logger = logging.getLogger(__name__)

def delete_file(file_path):
    """
    Deletes a file if it exists.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"Deleted file: {file_path}")
        return True
    return False
