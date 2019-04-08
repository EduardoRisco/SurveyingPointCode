# -*- coding: utf-8 -*-
#
# Module for uploading optional files.
# config_user and dxf_symbols
#
# Required PLY (Python Lex-Yacc).
# Required ezdxf.
#
# J. Eduardo Risco 27-03-2019
#

import ezdxf
import ply.lex as lex
import ply.yacc as yacc


config_file_init = []
errors_config_file_parser = []
errors_config_file_duplicate_elem = set()
symbols = []
file_symbols_dxf = ''

# Lexer part

tokens = (
    "TEXT",
    "INT",
    "COMA",
    "LPAREN",
    "RPAREN"
)

t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_INT(t):
    r'-?[0-9]+'
    t.value = int(t.value)
    return t


def t_TEXT(t):
    r'[a-zA-Z0-9_]+'
    t.type = 'TEXT'
    return t


t_COMA = r','

t_ignore = r' '


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    #print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer_config = lex.lex()

# Parser part


def p_linea(p):
    ''' linea : TEXT COMA TEXT COMA color COMA TEXT
              | TEXT COMA TEXT COMA color '''

    if len(p) == 8:
        p[0] = p[1], p[3], p[5], p[7]
    else:
        p[0] = (p[1], p[3], p[5])


def p_color(p):
    ''' color :  LPAREN INT COMA INT COMA INT RPAREN'''

    p[0] = p[2], p[4], p[6]


def p_error(p):
    if p:
        return p.value


def upload_config_file(input_file):
    '''
    This function reads a user configuration file,
    contains topographic codes, cad layers, colors and symbols.
    '''

    try:
        global config_file_init
        global errors_config_file_parser
        global errors_config_file_duplicate_elem
        errors_config_file_duplicate_elem = set()
        errors_config_file_parser = []
        config_file_init = []

        parser = yacc.yacc()
        f = open(input_file)
        line = f.readline()
        n_line = 0

        while line != "":
            n_line += 1
            c_line = parser.parse(line, lexer=lexer_config)
            if c_line == None or not c_line:
                # Capturing errors parser
                errors_config_file_parser.append([n_line, line])
            else:
                config_file_init.append(c_line)
            line = f.readline()
        f.close()

        if not get_errors_config_file() and not file_empty(get_errors_config_file(), get_config_file()):
            codes = []
            layer_color = []
            layer = []
            for conf in config_file_init:
                if len(codes) == 0:
                    codes.append(conf[0])
                    layer.append(conf[1])
                    layer_color.append((conf[1], conf[2]))
                else:
                    if conf[0] in codes:
                        # Capturing errors duplicate elements
                        error = 'Topographic code '+ conf[0]+ ' is duplicated'
                        errors_config_file_duplicate_elem.add(error)
                    codes.append(conf[0])
                    layer.append(conf[1])
                    layer_color.append((conf[1], conf[2]))       
    except (IOError, NameError) as e:
        print(e)


def upload_symbols_file(dxf_symbol_file):
    '''
    This function reads a dxf file with symbols.
    '''
    try:
        global error_symbol
        global symbols
        global file_symbols_dxf
        error_symbol = True
        symbols = []

        dwg = ezdxf.readfile(dxf_symbol_file)

        for b in dwg.blocks:
            if b.__getattribute__('name') not in(
                '_ArchTick',
                '_Open30') and (
                    b.__getattribute__('name').find('A$') == -1) and (
                    b.__getattribute__('name').find('*Paper') == -1) and (
                    b.__getattribute__('name').find('*Model') == -1):
                symbols.append(b.__getattribute__('name'))
                error_symbol = False

    except (IOError, NameError) as e:
        print(e)


def file_empty(list_items, list_errors):
    '''
    This function returns True if the file is empty, in other case it returns False.
    '''

    if not list_items and not list_errors:
        return True
    return False


def get_config_file():
    '''
    This function returns a config_user list if it exists, in other case it returns False.
    '''

    if file_empty(get_errors_config_file(), config_file_init) or (
            get_errors_config_file()) or get_errors_config_file_duplicate_elements():
        return False
    else:
        return config_file_init


def get_errors_config_file():
    '''
    This function returns a list of config_use errors,
    when the input data  doesn't have the correct format.
    '''
    if errors_config_file_parser:
        return errors_config_file_parser
    else:
        return False


def get_errors_config_file_duplicate_elements():
    '''
    This funtion  returns a list of errors,
    when there are duplicate items on different lines.
    '''
    if not get_errors_config_file() and errors_config_file_duplicate_elem:
        return errors_config_file_duplicate_elem
    else:
        return False


def get_symbols():
    '''
    This function returns a symbols list .
    '''
    if not symbols:
        return False
    else:
        return symbols


def error_symbols():
    '''
    This function returns true if there are no symbols in the dxf file.
    '''
    if not error_symbol:
        return False
    else:
        return True


def get_symbols_dxf_file():
    '''
    This function returns a symbols file .
    '''
    if not file_symbols_dxf:
        return False
    else:
        return file_symbols_dxf


def get_errors_config_file_duplicate_color(list_config):
    '''
    This function returns a list of errors, if any, of layers with 
    different color assigned. Input parameter a list with the user's configuration 
    '''

    layer_color = []
    layer = []
    errors = set()
    for conf in list_config:
        if len(layer) == 0:
            layer.append(conf[1])
            layer_color.append((conf[1], conf[2]))
        else:
            if conf[1] in layer and (conf[1], conf[2]) not in layer_color:
                error = 'The Layer '+ conf[1]+ 'has different colors assigned to it '
                errors.add(error)
            layer.append(conf[1])
            layer_color.append((conf[1], conf[2]))
    return errors
