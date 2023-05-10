import glob
import os
import shutil
import sys
import random
import string
import logging
from plyer import notification
from natsort import natsorted

def get_all_subfolders(path):
    subfolders = [f.path for f in os.scandir(path) if f.is_dir()]
    for subfolder in list(subfolders):
        subfolders.extend(get_all_subfolders(subfolder))
    return subfolders

def rename_and_move_files(path):
    subfolders = glob.glob(f"{path}/*/")
    subfolders = [(d.rstrip('\\')) for d in subfolders]
    for subfolder in subfolders:
        print('Target:', subfolder)
        # 元のフォルダ
        save_subfolder_name = subfolder
        # 作業フォルダ
        source = string.ascii_letters + string.digits
        random_str = ''.join([random.choice(source) for _ in range(8)])
        temp_subfolder_name = f"{os.path.basename(subfolder)}" + "_Temp" + random_str
        temp_subfolder_path = os.path.join(path, temp_subfolder_name)
        logging.warning('temp_subfolder_name: %s", temp_subfolder_path: %s', temp_subfolder_name, temp_subfolder_path)
        # 元のフォルダをリネームして元のフォルダを作り直す
        os.rename(subfolder, temp_subfolder_path)
        os.makedirs(save_subfolder_name)
        # ファイル名を取得し、自然順ソートでソートする
        sorted_filename = glob.glob(f"{temp_subfolder_path}/*.*")
        sorted_filename = natsorted(sorted_filename)
        # ファイル数からフォーマットを指定する
        d_abs = len(str(abs(len(sorted_filename))))
        if d_abs > 3:
            UID_FORMAT = '{:0' + str(d_abs) + 'd}'
        else:
            UID_FORMAT = '{:03d}'
        logging.warning('in Files: %s", UID_FORMAT: %s', len(sorted_filename), UID_FORMAT)
        num = 0
        for filename in sorted_filename:
            num += 1
            uid = UID_FORMAT.format(num)
            file_path = os.path.join(temp_subfolder_path, filename)
            file_extension = os.path.splitext(filename)[1]  # ファイルの拡張子を取得する
            temp_filename = f"{uid}{file_extension}"  # ファイル名を連番にリネームする
            temp_file_path = os.path.join(save_subfolder_name, temp_filename)
            os.rename(file_path, temp_file_path)
            logging.warning('Path to %s from %s', temp_file_path, file_path)
        try:
            os.rmdir(temp_subfolder_path)
        except OSError:
            # 2階層以下はそのまま元のフォルダに移動する
            for item in os.listdir(temp_subfolder_path):
                item_path = os.path.join(temp_subfolder_path, item)
                shutil.move(item_path, save_subfolder_name)
            os.rmdir(temp_subfolder_path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    logging.disable( logging.CRITICAL )
    logging.debug('program begins.')
    py_name = os.path.basename(__file__)
    try:
        path = sys.argv[1]
        logging.debug('path = {}'.format(path))
        if not os.path.isdir(path):
            print(f"{path} is not a valid directory path.")
            raise ValueError(f"{path} is not a valid directory path.")
        rename_and_move_files(path)
        notification.notify(title = py_name, message="Done.", timeout=5)
    except (IndexError, ValueError):
        print("Usage:", py_name, "C:\path")
