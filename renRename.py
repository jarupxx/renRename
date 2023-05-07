import os
import sys
import random
import string
from plyer import notification
from natsort import natsorted

def get_all_subfolders(path):
    subfolders = [f.path for f in os.scandir(path) if f.is_dir()]
    for subfolder in list(subfolders):
        subfolders.extend(get_all_subfolders(subfolder))
    return subfolders

def rename_and_move_files(path):
    subfolders = get_all_subfolders(path)
    for subfolder in subfolders:
        num = 1
        print('Target:', subfolder)
        # 元のフォルダ
        save_subfolder_name = subfolder
        # 作業フォルダ
        source = string.ascii_letters + string.digits
        random_str = ''.join([random.choice(source) for _ in range(8)])
        temp_subfolder_name = f"{os.path.basename(subfolder)}" + "Temp_" + random_str
        temp_subfolder_path = os.path.join(path, temp_subfolder_name)
        # 元のフォルダをリネームして元のフォルダを作り直す
        os.rename(subfolder, temp_subfolder_path)
        os.makedirs(save_subfolder_name)
        # ファイル名を取得し、自然順ソートでソートする
        sorted_filename = os.listdir(temp_subfolder_path)
        sorted_filename = natsorted(sorted_filename)
        for filename in sorted_filename:
            file_path = os.path.join(temp_subfolder_path, filename)
            file_extension = os.path.splitext(filename)[1]  # ファイルの拡張子を取得する
            temp_filename = f"{num:03d}{file_extension}"  # ファイル名を連番にリネームする
            temp_file_path = os.path.join(save_subfolder_name, temp_filename)
            os.rename(file_path, temp_file_path)
            num += 1
            # print(filename, 'to', temp_filename)
        os.rmdir(temp_subfolder_path)

if __name__ == "__main__":
    py_name = os.path.basename(__file__)
    try:
        path = sys.argv[1]
        if not os.path.isdir(path):
            print(f"{path} is not a valid directory path.")
            raise ValueError(f"{path} is not a valid directory path.")
        rename_and_move_files(path)
        notification.notify(title = py_name, message="Done", timeout=5)
    except (IndexError, ValueError):
        print("How to use:", py_name, "C:\path")
