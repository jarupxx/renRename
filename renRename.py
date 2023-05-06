import os
import sys
import random
import string
from natsort import natsorted

def get_all_subfolders(path):
    subfolders = [f.path for f in os.scandir(path) if f.is_dir()]
    for subfolder in list(subfolders):
        subfolders.extend(get_all_subfolders(subfolder))
    return subfolders

def rename_and_move_files(path):
    subfolders = get_all_subfolders(path)
    for subfolder in subfolders:
        # 元のフォルダ
        save_subfolder_name = subfolder
        # 作業フォルダ
        source = string.ascii_letters + string.digits
        random_str = ''.join([random.choice(source) for _ in range(8)])
        temp_subfolder_name = f"{os.path.basename(subfolder)}" + random_str
        temp_subfolder_path = os.path.join(path, temp_subfolder_name)
        # 元のフォルダをリネームして元のフォルダを作り直す
        os.rename(subfolder, temp_subfolder_path)
        os.makedirs(save_subfolder_name)
        i = 1
        # ファイル名を取得し、自然順ソートでソートする
        sorted_filename = os.listdir(temp_subfolder_path)
        sorted_filename = natsorted(sorted_filename)
        for filename in sorted_filename:
            print(filename)
            file_path = os.path.join(temp_subfolder_path, filename)
            file_extension = os.path.splitext(filename)[1]  # ファイルの拡張子を取得する
            temp_filename = f"{i:03d}{file_extension}"  # ファイル名を連番にリネームする
            temp_file_path = os.path.join(save_subfolder_name, temp_filename)
            os.rename(file_path, temp_file_path)
            i += 1
        os.rmdir(temp_subfolder_path)

if __name__ == "__main__":
    try:
        path = sys.argv[1]
        rename_and_move_files(path)
    except IndexError:
        py_name = os.path.basename(__file__)
        print("How to use:", py_name, "C:\path")
