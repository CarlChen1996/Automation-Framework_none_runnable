import time
import msvcrt
import zipfile
import os


def get_keyboard_input(timeout):
    start_time = time.time()
    input_value = ''
    while True:
        if msvcrt.kbhit():
            byte_arr = msvcrt.getche()
            if ord(byte_arr) == 13:  # click 'enter'
                break
            elif ord(byte_arr) >= 32:  # read input characters into array
                input_value += "".join(map(chr, byte_arr))
        if len(input_value) == 0 and (time.time() - start_time) > timeout:
            break
    if len(input_value) > 0:
        return input_value
    else:
        input_value = "99"  # default value 99 to exit
        return input_value


def zip_file(source_file, result_file):
    zip = zipfile.ZipFile(result_file, 'w', zipfile.ZIP_DEFLATED)
    zip.write(source_file)
    zip.close()
    return result_file


def zip_dir(source_dir, result_file, include_root_folder=False):
    zip = zipfile.ZipFile(result_file, 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(source_dir):
        if include_root_folder:
            for filename in filenames:
                zip.write(os.path.join(dirpath, filename))
        else:
            archive_path = dirpath.replace(source_dir, '')
            for filename in filenames:
                zip.write(os.path.join(dirpath, filename), os.path.join(archive_path, filename))           
    zip.close()
    return result_file


def unzip(source_zip, result_path):
    zip = zipfile.ZipFile(source_zip)
    file_name_list = zip.namelist()
    for name in file_name_list:
        # result_path = c:\tmp, the files will be extract to c:\tmp\*
        file_handler = open(os.path.join(result_path + '\\', name), 'wb')
        file_handler.write(zip.read(name))
        file_handler.close()
    zip.close()
    return result_path
