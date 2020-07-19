import ctypes
import os

os.add_dll_directory(os.getcwd())

user_dll = ctypes.WinDLL('user.dll')
process_query_proto = ctypes.WINFUNCTYPE(ctypes.c_double, ctypes.c_char_p)
update_symbols_proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_char_p)

process_query_params = (1, 'pquery', 0),
update_symbols_params = (1, 'psymbols', 0),

process_query_ = process_query_proto(('process_query', user_dll), process_query_params)
update_symbols_ = update_symbols_proto(('update_symbols', user_dll), update_symbols_params)


def process_query(query):
    return process_query_(ctypes.c_char_p(query))


def update_symbols(symbols):
    symbols_str = ''
    for i, key in enumerate(symbols):
        val = symbols[key]
        val = val.replace('\n', '_')
        val = val.replace(' ', '_')
        symbols_str += f'{key}: {val}'
        if i != len(symbols) - 1:
            val += '\n'
    symbols_str = bytes(symbols_str, 'ascii')
    return update_symbols_(ctypes.c_char_p(symbols_str))
