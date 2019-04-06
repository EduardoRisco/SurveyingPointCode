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


config_user_init = []
errors_config_user_parser = []
errors_config_user_duplicate_elem = set()
symbols = []
table_config = []
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
    print("Illegal character '%s'" % t.value[0]) 
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


def upload_file_config(input_file):
    '''
    This function reads a user configuration file,
    contains topographic codes, cad layers, colors and symbols.
    '''

    try:
        global config_user_init
        global errors_config_user_parser
        global errors_config_user_duplicate_elem
        errors_config_user_duplicate_elem = set()
        errors_config_user_parser = []
        config_user_init = []

        parser = yacc.yacc()
        f = open(input_file)
        line = f.readline()
        n_line = 0

        while line != "":
            n_line += 1
            c_line = parser.parse(line, lexer=lexer_config)
            if c_line == None or not c_line:
                # Capturing errors parser
                errors_config_user_parser.append([n_line, line])
            else:
                config_user_init.append(c_line)
            line = f.readline()
        f.close()

        if not get_errors_config_user():
            codes = []
            layer_color = []
            layer = []
            for conf in config_user_init:
                if len(codes) == 0:
                    codes.append(conf[0])
                    layer.append(conf[1])
                    layer_color.append((conf[1], conf[2]))
                else:
                    if conf[0] in codes:
                        # Capturing errors duplicate elements
                        error = ('Topographic code ',
                                 conf[0], ' is duplicated')
                        errors_config_user_duplicate_elem.add(error)
                    if conf[1] in layer:
                        if (conf[1], conf[2]) not in layer_color:
                            error = (
                                'The Layer ', conf[1],
                                'has different colors assigned to it ')
                            errors_config_user_duplicate_elem.add(error)
                    codes.append(conf[0])
                    layer.append(conf[1])
                    layer_color.append((conf[1], conf[2]))
        
    except (IOError, NameError) as e:
        print(e)


def extract_symbols(dxf_symbol):
    '''
    This function reads a dxf file with symbols.
    '''
    try:
        global error_symbol
        global symbols
        global file_symbols_dxf
        error_symbol=True
        file_symbols_dxf = dxf_symbol
        symbols = []

        dwg = ezdxf.readfile(dxf_symbol)

        for b in dwg.blocks:
            if b.__getattribute__('name') not in(
                '_ArchTick',
                '_Open30') and (
                    b.__getattribute__('name').find('A$') == -1) and (
                    b.__getattribute__('name').find('*Paper') == -1) and (
                    b.__getattribute__('name').find('*Model') == -1):
                symbols.append(b.__getattribute__('name'))
                error_symbol=False

    except (IOError, NameError) as e:
        print(e)


def get_config_user():
    '''
    This function returns a config_user list .
    '''

    if get_errors_config_user() or get_errors_config_user_duplicate_elements():
        return False
    else:
        return config_user_init


def get_errors_config_user():
    '''
    This function returns a list of config_use errors,
    when the input data  doesn't have the correct format.
    '''
    if errors_config_user_parser:
        return errors_config_user_parser
    else:
        return False


def get_errors_config_user_duplicate_elements():
    '''
    This funtion  returns a list of errors,
    when there are duplicate items on different lines.
    '''
    if not get_errors_config_user() and errors_config_user_duplicate_elem:
        return errors_config_user_duplicate_elem
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

def get_error_symbols():
    '''
    This function returns true if there are no symbols in the dxf file.
    '''
    if not error_symbol:
        return False
    else:
        return True        


def get_symbols_file_dxf():
    '''
    This function returns a symbols file .
    '''
    if not file_symbols_dxf:
        return False
    else:
        return file_symbols_dxf


def get_config_table():
    '''
    This function returns an initial configuration automatically
    generated with the uploaded files.
    '''
    if table_config:
        return table_config
    else:
        False
