# -*- coding: utf-8 -*-
#
# Prototipo App, conversor a dxf
#
# Se requiere PLY (Python Lex-Yacc).
#
# J. Eduardo Risco 12-02-2019
#

import ply.lex as lex
import ply.yacc as yacc

import ezdxf

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


lex.lex()

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
            p[0] = p[1] + (p[2],)
        else:
            p[0] = p[1], p[2]
    else:
        p[0] = p[1]


def p_error(p):
    if p:
        print("Syntax error in imput at '%s'" % p.value)


def genera_dxf(entrada):

    try:
        parser = yacc.yacc()
        err = False
        capas = set()  # Conjunto de capas existentes
        dicc_capas = {}  # Diccionario que almacena los puntos
        lineas = []
        curvas = []
        puntos = []
        linea = []
        curva = []

        f = open(entrada)
        line = f.readline()
        n_line = 1
        while line != "":
            # Pasamos el parser
            punto = parser.parse(line)
            # Deteccón de archivo de entrada erroneo
            if not punto:
                err = True
                break
            # print(punto)
            codigo_capa = punto[2]
            # Comprobación que las capas no existan en el diccionario
            # si no existen se crean
            # y se añade el primer punto a esa capa
            if codigo_capa not in capas:
                dicc_capas[codigo_capa] = [punto]
                capas.add(codigo_capa)
            else:
                # Se añaden los puntos que tengan el mismo codigo
                # a su elemento correspondiente en el diccionario
                if codigo_capa in dicc_capas:
                    lista = dicc_capas.get(codigo_capa)
                    lista.append(punto)
                    dicc_capas[codigo_capa] = lista
            line = f.readline()
            n_line += 1

        # Extracción de lineas y curvas

        for ptos in dicc_capas:
            linea_iniciada = False
            curva_iniciada = False
            for pto in dicc_capas.get(ptos):
                puntos.append(pto)
                if pto[2] not in ('TC', 'TR', 'TX'):
                    if len(pto) > 3:
                        if pto[3] == 'I':
                            # Si la linea está iniciada
                            if linea_iniciada:
                                # Si encuentro 'I' cierro la linea y empiezo otra
                                lineas.append(linea)
                                linea = []
                                linea.append(pto)
                                linea_iniciada = True
                            # Si no existe linea en esa capa, se crea la 1ª linea
                            else:
                                linea = []
                                linea.append(pto)
                                linea_iniciada = True
                        elif pto[3] == 'IC':
                            # Si la curva está iniciada
                            if curva_iniciada:
                                # Si encuentro 'IC' cierro la curva y empiezo otra
                                curvas.append(curva)
                                curva = []
                                curva.append(pto)
                                curva_iniciada = True
                            # Si no existe curva en esa capa, se crea la 1ª curva
                            else:
                                curva = []
                                curva.append(pto)
                                curva_iniciada = True
                        # Se añaden puntos a la curva
                        elif pto[3] == 'C' and curva_iniciada:
                            curva.append(pto)
                    # Se añaden puntos a la linea
                    elif linea_iniciada:
                        linea.append(pto)
            # Si no hay mas elementos en la capa, cerramos lineas y curvas
            if linea:
                lineas.append(linea)
                linea = []
            if curva:
                curvas.append(curva)
                curva = []

        f.close()

        # Salida archivo correcto
        if line == "" and not err:
            dwg = ezdxf.new('AC1015')

            # Se crea el espacio modelo donde se añaden todos los elementos del dibujo
            msp = dwg.modelspace()

            # Tratamiento de lineas
            for ptos in lineas:
                lin_coord = []
                for coord_puntos in ptos:
                    # Se extraen solo las coordenadas del punto (x,y,z)
                    lin_coord.append(coord_puntos[1])
                # Funcion para añadir lineas al modelo (polylineas)
                msp.add_lwpolyline(lin_coord)

            # Tratamiento de curvas
            for ptos in curvas:
                lin_coord = []
                for coord_puntos in ptos:
                    # Se extraen solo las coordenadas del punto (x,y,z)
                    lin_coord.append(coord_puntos[1])
                # Funcion para añadir curvas al modelo
                msp.add_spline(lin_coord)

            #test    

            l = 0
            c = 0
            for el in dwg.entities:
                if type(el) == ezdxf.modern.lwpolyline.LWPolyline:
                    l = l+1
                elif type(el) == ezdxf.modern.spline.Spline:
                    c = c+1
            print('Se han añadido', l, 'lineas, ',
                  c, 'curvas, al archivo dxf creado')

            dwg.saveas("./tmp/salida.dxf")


        else:
            # Salida archivo error
            print('Archivo erroneo:', entrada)

    except (IOError, NameError) as e:
        print(e)
