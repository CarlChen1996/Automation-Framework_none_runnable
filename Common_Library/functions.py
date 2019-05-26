import time
import msvcrt


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
