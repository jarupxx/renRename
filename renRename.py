import glob
import os
import shutil
import sys
import random
import string
import logging
import time
from plyer import notification
from natsort import natsorted

def get_all_subfolders(path):
    subfolders = glob.glob(f"{path}/*/")
    subfolders = [(d.rstrip('\\')) for d in subfolders]
    for subfolder in subfolders:
        rename_and_move_files(subfolder)

def rename_and_move_files(subfolder):
    print('Target:', subfolder)
    # 元のフォルダー
    save_subfolder_name = subfolder
    # 作業フォルダー
    source = string.ascii_letters + string.digits
    random_str = ''.join([random.choice(source) for _ in range(8)])
    temp_subfolder_path = subfolder + "_Temp" + random_str
    logging.warning('temp_subfolder_path: %s', temp_subfolder_path)
    # 元のフォルダーをリネームして元のフォルダーを作り直す
    os.rename(subfolder, temp_subfolder_path)
    os.makedirs(save_subfolder_name)
    # ファイル名を取得し、自然順ソートでソートする
    sorted_filename = [f for f in os.listdir(temp_subfolder_path) if os.path.isfile(os.path.join(temp_subfolder_path, f))]
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
        # 2階層以下はそのまま元のフォルダーに移動する
        for item in os.listdir(temp_subfolder_path):
            item_path = os.path.join(temp_subfolder_path, item)
            shutil.move(item_path, save_subfolder_name)
        os.rmdir(temp_subfolder_path)

def record_start_time():
    return time.time()

def notify_end(start_time, threshold=3):
    print('Done.')
    end_time = time.time()
    processing_time = end_time - start_time
    if processing_time > threshold:
        notification.notify(title=py_name, message="Done.", timeout=5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    logging.disable( logging.CRITICAL )
    logging.debug('program begins.')
    py_name = os.path.basename(__file__)
    try:
        path = sys.argv[1]
        logging.debug('path = {}'.format(path))
        # パスのチェック
        if os.path.isfile(path):
            path, orig_file_name = os.path.split(path)
            if path == "":
                path = os.getcwd()
            logging.warning('file path: %s', path)
            start_time = record_start_time()
            rename_and_move_files(path)
            notify_end(start_time)
            sys.exit()
        elif os.path.isdir(path):
            # ルートディレクトリは許可しない
            if os.path.abspath(path) == os.path.abspath(os.path.join(path, os.pardir)):
                print(f"root is not allow path: {path}")
                raise ValueError(f"root is not allow path: {path}")
        start_time = record_start_time()
        get_all_subfolders(path)
        notify_end(start_time)
    except (IndexError, ValueError):
        print("Usage:", py_name, '"C:\\path"')
