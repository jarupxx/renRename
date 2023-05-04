import os
import sys
import random
import string

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
        for filename in os.listdir(temp_subfolder_path):
            file_path = os.path.join(temp_subfolder_path, filename)
            file_extension = os.path.splitext(filename)[1]  # ファイルの拡張子を取得する
            temp_filename = f"{i:03d}{file_extension}"  # ファイル名を連番にリネームする
            temp_file_path = os.path.join(save_subfolder_name, temp_filename)
            os.rename(file_path, temp_file_path)
            i += 1
        os.rmdir(temp_subfolder_path)

if __name__ == "__main__":
    path = sys.argv[1]
    rename_and_move_files(path)
