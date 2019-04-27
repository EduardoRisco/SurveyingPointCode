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

import os

import ezdxf
import ply.lex as lex
import ply.yacc as yacc

from app import app

config_file_init = []
errors_config_file_parser = []
errors_config_file_duplicate_elem = []
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
    r'[a-zA-ZÀ-ÿ0-9ñÑ_]+'
    t.type = 'TEXT'
    return t


t_COMA = r','

t_ignore = r' '


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    t.lexer.skip(1)


lexer_config = lex.lex()

# Parser part


def p_linea(p):
    """ linea : TEXT COMA TEXT COMA color COMA TEXT
              | TEXT COMA TEXT COMA color """

    if len(p) == 8:
        p[0] = p[1], p[3], p[5], p[7]
    else:
        p[0] = (p[1], p[3], p[5])


def p_color(p):
    """ color :  LPAREN INT COMA INT COMA INT RPAREN"""

    p[0] = p[2], p[4], p[6]


def p_error(p):
    if p:
        return p.value


def upload_config_file(input_file):
    """
    This function reads a user configuration file,
    contains topographic codes, cad layers, colors and symbols.
    """

    try:
        global config_file_init
        global errors_config_file_parser
        global errors_config_file_duplicate_elem
        errors_config_file_duplicate_elem = []
        errors_config_file_parser = []
        config_file_init = []

        parser = yacc.yacc()
        with open(input_file, encoding='utf-8') as f:

            line = f.readline()
            n_line = 0
            while line != "":
                n_line += 1
                c_line = parser.parse(line, lexer=lexer_config)
                if c_line is None or not c_line:
                    # Capturing errors parser
                    errors_config_file_parser.append([n_line, line])
                else:
                    config_file_init.append(c_line)
                line = f.readline()

        if not get_errors_config_file():
            codes = []
            layer_color = []
            layer = []
            n_line = 0
            for conf in config_file_init:
                n_line += 1
                if len(codes) == 0:
                    codes.append(conf[0])
                    layer.append(conf[1])
                    layer_color.append((conf[1], conf[2]))

                else:
                    if conf[0] in codes:
                        # Capturing errors duplicate elements
                        error = 'Topographic code ' + \
                            conf[0] + ' is duplicated'
                        errors_config_file_duplicate_elem.append(
                            [n_line, error])
                    codes.append(conf[0])
                    layer.append(conf[1])
                    layer_color.append((conf[1], conf[2]))
    except (IOError, NameError) as e:
        print(e)


def upload_symbols_file(dxf_symbol_file):
    """
    This function reads a dxf file with symbols.
    """
    try:
        global error_symbol
        global symbols
        global file_symbols_dxf
        error_symbol = True
        file_symbols_dxf = dxf_symbol_file
        symbols = []

        dwg = ezdxf.readfile(file_symbols_dxf)

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


def get_config_file():
    """
    This function returns a config_user list if it exists, in other case it returns False.
    """

    if  not config_file_init or get_errors_config_file() or (
            get_errors_config_file()) or get_errors_config_file_duplicate_elements():
        return False
    else:
        return config_file_init


def get_errors_config_file():
    """
    This function returns a list of config_use errors,
    when the input data  doesn't have the correct format.
    """
    if errors_config_file_parser:
        return errors_config_file_parser
    else:
        return False


def get_errors_config_file_duplicate_elements():
    """
    This funtion  returns a list of errors,
    when there are duplicate items on different lines.
    """
    if not get_errors_config_file() and errors_config_file_duplicate_elem:
        return errors_config_file_duplicate_elem
    else:
        return False


def get_errors_config_file_duplicate_color(list_config, code_layers):
    """
    This function returns a list of errors, if any, of layers with 
    different color assigned. Input parameter a list with the user's configuration 
    """
    if not list_config:
        return False
    else:
        layer_color = []
        layer = []
        errors = set()
        for conf in list_config:
            layer_name = '0' if conf[1] == '' else conf[1]
            if len(layer) == 0:
                layer.append(conf[1])
                layer_color.append((conf[1], conf[2]))
            else:
                if (conf[0] in code_layers and conf[1] in layer and (
                        conf[1], conf[2]) not in layer_color):
                    error = 'The Layer ' + layer_name + \
                        ' has different colors assigned to it '
                    errors.add(error)
                layer.append(conf[1])
                layer_color.append((conf[1], conf[2]))
        return errors


def file_empty(file):
    """
    This function returns True if the file is empty, in other case it returns False.
    """

    if os.stat(file).st_size == 0:
        return True
    return False


def get_symbols():
    """
    This function returns a symbols list .
    """
    if not symbols:
        return False
    else:
        return symbols


def error_symbols():
    """
    This function returns true if there are no symbols in the dxf file.
    """
    if not error_symbol:
        return False
    else:
        return True


def get_symbols_dxf_file():
    """
    This function returns a symbols file .
    """
    if not file_symbols_dxf:
        return False
    else:
        return file_symbols_dxf


def get_errors_cad_color_palette(list_config, code_layers):
    """
    This function returns a list of errors, 
    if the color is not in the cad color palette.
    Input parameter a list with the user's configuration
    """
    if not list_config:
        return False
    else:
        errors = set()
        for conf in list_config:
            if conf[2] not in app.config['CAD_COLORS'] and conf[0] in code_layers:
                error = 'Layer '+conf[1] + ': rgb' + str(conf[2]) + \
                        ' color is not defined in the cad color palette '
                errors.add(error)
        return errors
