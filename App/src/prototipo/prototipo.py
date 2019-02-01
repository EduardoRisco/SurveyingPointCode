# -*- coding: utf-8 -*-
#
# Prototipo que comprueba si un archivo tiene el formato correcto o no.
#
# Se requiere PLY (Python Lex-Yacc).
#
# J. Eduardo Risco 31-01-2019

import ply.lex as lex
import ply.yacc as yacc

# Lexer part

tokens = (
    "ID",
    "INT",
    "FLOAT",
    "COMA",
    "COD_GEOM",
    "COD_ELEM_SING",
)

reserved = {
    'I': "COD_GEOM",
    'IC': "COD_GEOM",
    'C': "COD_GEOM",
    'TC': "COD_ELEM_SING",
    'TR': "COD_ELEM_SING",
    'TX': "COD_ELEM_SING",
}


def t_ID(t):
    r'[a-zA-Z]+'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_FLOAT(t):
    r'-?([0-9]*\.[0-9]+)'
    t.value = float(t.value)
    return t


def t_INT(t):
    r'-?[0-9]+'
    t.value = int(t.value)
    return t


t_COMA = r','

t_ignore = r' '


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    raise SyntaxError("syntax error on line %d near '%s'" %
                      (t.lineno, t.value))


lex.lex(debug=1)

# Parser part


def p_linea(p):
    ''' linea : INT COMA coordenadas COMA codigo '''
    p[0] = (p[1], p[3]) + p[5]


def p_coordenadas(p):
    ''' coordenadas : FLOAT COMA FLOAT COMA FLOAT '''
    p[0] = p[1], p[3], p[5]


def p_codigo(p):
    ''' codigo : codigo_capa codigo_geometrico
               | codigo_elemento_singular codigo_valor_texto
               | codigo_capa codigo_no_accesible
               | codigo_elemento_singular
               | codigo_capa '''

    if len(p) == 3:
        p[0] = p[1], p[2]
    else:
        p[0] = (p[1],)


def p_codigo_capa(p):
    ''' codigo_capa : ID '''
    p[0] = p[1]


def p_codigo_geometrico(p):
    ''' codigo_geometrico : COD_GEOM '''
    p[0] = p[1]


def p_codigo_elemento_singular(p):
    ''' codigo_elemento_singular :  COD_ELEM_SING '''
    p[0] = p[1]


def p_codigo_valor_texto(p):
    ''' codigo_valor_texto : FLOAT ID
                           | INT ID
                           | FLOAT
                           | INT
                           | ID '''

    if len(p) == 3:
        p[0] = p[1], p[2]
    else:
        p[0] = p[1]


def p_codigo_no_accesible(p):
    ''' codigo_no_accesible : FLOAT
                            | INT 
                            | codigo_no_accesible FLOAT
                            | codigo_no_accesible INT  '''

    if len(p) == 3:

        if type(p[1]) == tuple:
            p[0] = p[1]+(p[2],)
        else:
            p[0] = p[1], p[2]
    else:
        p[0] = p[1]


def p_error(p):
    if p:
        print("Syntax error in imput at '%s'" % p.value)


parser = yacc.yacc(debug=1)

# test

if __name__ == "__main__":

    try:
        err = False
        for i in ('entrada/ejemplo1.txt', 'entrada/ejemplo2.txt'):
            print('')
            f = open(i)
            line = f.readline()
            n = 1
            while line != "":
                p = parser.parse(line)
                if not p:
                    err = True
                line = f.readline()
                print(p)
                n = n+1
                if line == "" and not err:
                    print('Archivo ok:', i)
                    print('Número de lineas :', n)
            f.close()
            if err:
                print('Archivo erroneo:', i)
    except (IOError, NameError) as e:
        print(e)