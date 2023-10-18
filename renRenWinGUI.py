import glob
import os
import shutil
import sys
import random
import string
import logging
import time
from plyer import notification
import PySimpleGUI as sg
import winreg
import ctypes
from ctypes import windll, create_unicode_buffer
from functools import cmp_to_key

def get_all_subfolders(path):
    subfolders = [f.path for f in os.scandir(path) if f.is_dir()]
    for subfolder in list(subfolders):
        subfolders.extend(get_all_subfolders(subfolder))
    return subfolders

def natural_sort_cmp(a, b):
    # StrCmpLogicalW 関数を使用して、自然順ソートのための比較関数を作成する
    cmp_func = windll.Shlwapi.StrCmpLogicalW
    return cmp_func(a, b)

def rename_and_move_files(path):
    # 開始時刻を記録する
    start_time = time.time()

    subfolders = glob.glob(f"{path}/*/")
    subfolders = [(d.rstrip('\\')) for d in subfolders]
    for subfolder in subfolders:
        print('Target:', subfolder)
        # 元のフォルダー
        save_subfolder_name = subfolder
        # 作業フォルダー
        source = string.ascii_letters + string.digits
        random_str = ''.join([random.choice(source) for _ in range(8)])
        temp_subfolder_name = f"{os.path.basename(subfolder)}" + "_Temp" + random_str
        temp_subfolder_path = os.path.join(path, temp_subfolder_name)
        logging.warning('temp_subfolder_name: %s", path: %s', temp_subfolder_name, temp_subfolder_path)
        # 元のフォルダーをリネームして元のフォルダーを作り直す
        os.rename(subfolder, temp_subfolder_path)
        os.makedirs(save_subfolder_name)
        # ファイル名を取得し、エクスプローラー順でソートする
        sorted_filename = [f for f in os.listdir(temp_subfolder_path) if os.path.isfile(os.path.join(temp_subfolder_path, f))]
        sorted_filename = sorted(sorted_filename, key=cmp_to_key(natural_sort_cmp))
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
    print('Done.')
    # 処理が3秒超えたら通知をする
    end_time = time.time()
    processing_time = end_time - start_time
    if processing_time > 3:
        notification.notify(title=py_name, message="Done.", timeout=5)

def check_winreg():
    # レジストリの値を取得
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                     r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer")
    name = "NoStrCmpLogical"
    try:
        value, _ = winreg.QueryValueEx(key, name)
        if value == 1:
            print("Unsupported policy setting:\nTurn off numerical sorting in File Explorer 'NoStrCmpLogical'.")
            input("Press any key to exit.")
            sys.exit()
    except FileNotFoundError:
        pass

    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                     r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer")
    name = "NoStrCmpLogical"
    try:
        value, _ = winreg.QueryValueEx(key, name)
        if value == 1:
            print("Unsupported policy setting:\nTurn off numerical sorting in File Explorer 'NoStrCmpLogical'.")
            input("Press any key to exit.")
            sys.exit()
    except FileNotFoundError:
        pass

def make_gui():
    sg.theme('DarkGray2')

    # GUIのレイアウト
    layout = [
        [sg.Text('Select folder that you want to serialized.')],
        [sg.Input(), sg.FolderBrowse()],
        [sg.Checkbox('Enable logging.'), sg.Column([[sg.Button('Serialized', size=(24,1))]],
        element_justification='right', expand_x=True, expand_y=True,)]
    ]

    # ウィンドウの作成
    window = sg.Window('renRenWin', layout)

    # イベントループ
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break
        elif event == 'Serialized':
            path = values[0]
            enable_logging = values[1]
            if enable_logging == True:
                logging.disable( logging.DEBUG )
                logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s', filename="rename.log")
            if path is None:
                sys.exit()
            if os.path.isdir(path):
                # パスのチェック ルートディレクトリは許可しない
                if os.path.abspath(path) == os.path.abspath(os.path.join(path, os.pardir)):
                    print(f"root is not allow path: {path}")
                    raise ValueError(f"root is not allow path: {path}")
                    sys.exit()
                rename_and_move_files(path)
    window.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    logging.disable( logging.CRITICAL )
    logging.debug('program begins.')
    py_name = os.path.basename(__file__)
    # DPIを指定する
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except:
        pass
    check_winreg()
    try:
        path = sys.argv[1]
        logging.debug('path = {}'.format(path))
        # パスのチェック ルートディレクトリは許可しない
        if not os.path.isdir(path):
            print(f"{path} is not a valid directory path.")
            raise ValueError(f"{path} is not a valid directory path.")
        if os.path.isdir(path):
            if os.path.abspath(path) == os.path.abspath(os.path.join(path, os.pardir)):
                print(f"root is not allow path: {path}")
                raise ValueError(f"root is not allow path: {path}")
        rename_and_move_files(path)
    except (IndexError, ValueError):
        print("Usage:", py_name, '"C:\\path"')
        make_gui()
