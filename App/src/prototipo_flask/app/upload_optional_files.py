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
    raise SyntaxError("syntax error on line %d near '%s'" %
                      (t.lineno, t.value))


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



def upload_file_config(entrada):
    '''
    This function reads a user configuration file,
    contains topographic codes, cad layers, colors and symbols.
    '''
    try:
        global config_user_init
        global errors_config_user_parser
        errors_config_user_parser = []
        config_user_init = []

        parser = yacc.yacc()
        f = open(entrada)
        line = f.readline()
        n_line = 0

        while line != "":
            n_line += 1
            c_line = parser.parse(line, lexer=lexer_config)
            if c_line == None or not c_line:
                errors_config_user_parser.append([n_line, line])
            else:
                config_user_init.append(c_line)

            line = f.readline()
        f.close()

        print(get_config_user())
        print(get_errors_config_user())

    except (IOError, NameError) as e:
        print(e)


def configuration_table():
    pass


file_symbols = "tmp/simbolos.dxf"


def extract_symbols(dxf_symbol=file_symbols):
    '''
    This function reads a dxf file with symbols.
    '''
    try:
        global symbols
        global file_symbols_dxf
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

    except (IOError, NameError) as e:
        print(e)


def get_config_user():
    '''
    This function returns a config_user list .
    '''

    if errors_config_user_parser:
        return False
    else:
        return config_user_init


def get_errors_config_user():
    '''
    This function returns a error list from config_user.
    '''
    if errors_config_user_parser:
        return errors_config_user_parser
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


def get_symbols_file_dxf():
    '''
    This function returns a symbols file .
    '''
    if not file_symbols_dxf:
        return False
    else:
        return file_symbols_dxf