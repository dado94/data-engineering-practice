import os, shutil

def cleanup_folder(path):
    print(f"Cleaning up folder {path}")
    # cleaning up test folder
    for f in os.listdir(path):
        objectt_path = os.path.join(path, f)
        if os.path.isfile(objectt_path):
            os.remove(objectt_path)
        else:
            if os.path.isdir(objectt_path):
                shutil.rmtree(objectt_path)
