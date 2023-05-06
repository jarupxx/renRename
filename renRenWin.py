import os
import sys
import random
import string
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
        # ファイル名を取得し、エクスプローラー順でソートする
        sorted_filename = os.listdir(temp_subfolder_path)
        sorted_filename = sorted(sorted_filename, key=cmp_to_key(natural_sort_cmp))
        for filename in sorted_filename:
            file_path = os.path.join(temp_subfolder_path, filename)
            file_extension = os.path.splitext(filename)[1]  # ファイルの拡張子を取得する
            temp_filename = f"{num:03d}{file_extension}"  # ファイル名を連番にリネームする
            temp_file_path = os.path.join(save_subfolder_name, temp_filename)
            os.rename(file_path, temp_file_path)
            num += 1
            # print(filename, 'to', temp_filename)
        os.rmdir(temp_subfolder_path)

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

if __name__ == "__main__":
    check_winreg()
    try:
        path = sys.argv[1]
        if not os.path.isdir(path):
            print(f"{path} is not a valid directory path.")
            raise ValueError(f"{path} is not a valid directory path.")
        rename_and_move_files(path)
    except (IndexError, ValueError):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
        except:
            pass
        while True:
            path = sg.popup_get_folder('Select folder that you want to serialized', title='renRenWin')
            if path is None:
                sys.exit()
            if os.path.isdir(path):
                break
        rename_and_move_files(path)
