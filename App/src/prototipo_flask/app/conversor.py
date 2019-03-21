# -*- coding: utf-8 -*-
#
# Prototipo App, conversor a dxf
#
# Se requiere PLY (Python Lex-Yacc).
# Se requiere ezdxf.
#
# J. Eduardo Risco 15-03-2019
#

import ply.lex as lex
import ply.yacc as yacc

import ezdxf
from app.geometric_tools import create_layers, create_points, create_circles, create_lines, create_curves, create_square, create_rectangles

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

        if isinstance(p[1], tuple):
            p[0] = p[1] + (p[2],)
        else:
            p[0] = p[1], p[2]
    else:
        p[0] = p[1]


def p_error(p):
    if p:
        return p.value


def upload_txt(entrada):

    try:
        global errores
        global lineas
        global curvas
        global line
        global err
        global capas_topografia
        global puntos
        global circulos
        global cuadrados
        global rectangulos

        parser = yacc.yacc()
        err = False
        capas_topografia = set()  # Conjunto de capas existentes
        dicc_capas = {}  # Diccionario que almacena los puntos
        lineas = []
        curvas = []
        puntos = []
        linea = []
        curva = []
        errores = []
        circulos = []
        cuadrados = []
        rectangulos = []
        codigo_capa = ""

        f = open(entrada)
        line = f.readline()
        n_line = 0

        while line != "":
            n_line += 1
            # Pasamos el parser
            punto = parser.parse(line)
            # Deteccón de archivo de entrada erroneo
            if not punto:
                err = True
                # Captura de errores
                errores.append([n_line, line])

            else:
                # Obtención del código de capa
                if len(punto) == 4 and (punto[2] == "TR" or punto[2] == "TC"):
                    codigo_capa = punto[3]
                elif punto[2] == "TX":
                    codigo_capa = punto[3][1]
                else:
                    codigo_capa = punto[2]
                # Comprobación que las capas no existan en el diccionario
                # si no existen se crean
                # y se añade el primer punto a esa capa
                if codigo_capa not in capas_topografia:
                    dicc_capas[codigo_capa] = [punto]
                    capas_topografia.add(codigo_capa)
                else:
                    # Se añaden los puntos que tengan el mismo codigo
                    # a su elemento correspondiente en el diccionario
                    if codigo_capa in dicc_capas:
                        lista = dicc_capas.get(codigo_capa)
                        lista.append(punto)
                        dicc_capas[codigo_capa] = lista
            line = f.readline()

        # Extracción de lineas y curvas

        for ptos in dicc_capas:
            linea_iniciada = False
            curva_iniciada = False
            for pto in dicc_capas.get(ptos):
                puntos.append(pto)
                if pto[2] not in ('TC', 'TR', 'TX'):
                    if len(pto) > 3 and not isinstance(pto[3],
                                                       (tuple, int, float)):
                        if pto[3] == 'I':
                            # Si la linea está iniciada
                            if linea_iniciada:
                                # Si encuentro 'I' cierro la linea y empiezo
                                # otra
                                lineas.append(linea)
                                linea = []
                                linea.append(pto)
                                linea_iniciada = True
                            # Si no existe linea en esa capa, se crea la 1ª
                            # linea
                            else:
                                linea = []
                                linea.append(pto)
                                linea_iniciada = True
                        elif pto[3] == 'IC':
                            # Si la curva está iniciada
                            if curva_iniciada:
                                # Si encuentro 'IC' cierro la curva y empiezo
                                # otra
                                curvas.append(curva)
                                curva = []
                                curva.append(pto)
                                curva_iniciada = True
                            # Si no existe curva en esa capa, se crea la 1ª
                            # curva
                            else:
                                curva = []
                                curva.append(pto)
                                curva_iniciada = True
                        # Se añaden puntos a la curva
                        elif pto[3] == 'C' and curva_iniciada:
                            curva.append(pto)
                    elif len(pto) == 4 and linea_iniciada:
                        linea.append(pto)
                    # Se añaden puntos a la linea
                    elif linea_iniciada:
                        linea.append(pto)
                # Crear lista con circulos
                elif pto[2] == 'TX':
                    circulos.append(pto)
                # Crear lista con cuadrados
                elif pto[2] == 'TC':
                    cuadrados.append(pto)
                # Crear lista con rectangulos
                elif pto[2] == 'TR':
                    rectangulos.append(pto)

            # Si no hay mas elementos en la capa, cerramos lineas y curvas
            if linea:
                lineas.append(linea)
                linea = []
            if curva:
                curvas.append(curva)
                curva = []

        f.close()

    except (IOError, NameError) as e:
        print(e)


def genera_dxf():

    # Ejemplo de archivo de usuario , código de campo-capa, capa de cad y
    # color de capa.
    file_user = [
        [
            'E', 'Edificio', (38, 140, 89)], [
            'A', 'Acera', 0], [
                'FA', 'Farola', 2], [
                    'TEL', 'Telecomunicaciones', 3], [
                        'RE', 'Red_Electrica', 161], [
                            'SAN', 'Saneamiento', 220], [
                                'M', 'Muro', 1], [
                                    'B', 'Bordillo', 0], [
                                        'B1', 'Bordillo', 0], [
                                            'R', 'Relleno', 0], [
                                                'ARB', 'Arbol', 60], [
                                                    'C', 'Calzada', 141], [
                                                        'C1', 'Calzada', 141]]

    # Salida archivo correcto #### Pendiente de modificar en función de los
    # errores obtenidos
    if line == "" and not err:
        dwg = ezdxf.new('AC1018')

        # Crear el espacio modelo donde se añaden todos los elementos del
        # dibujo.
        msp = dwg.modelspace()

        # Crear capas necesarias.
        create_layers(dwg, file_user)
        # Añadir puntos al modelo.
        create_points(dwg, msp, puntos)
        # Añadir círculos al modelo.
        create_circles(msp, circulos, file_user)
        # Añadir lineas al modelo.
        create_lines(msp, lineas, file_user)
        # Añadir curvas al modelo.
        create_curves(msp, curvas, file_user)
        # Añadir cuadrados al modelo.
        create_square(msp, cuadrados, file_user)
        # Añadir rectangulos al modelo.
        create_rectangles(msp, rectangulos, file_user)

        # test

        l = 0
        c = 0
        for el in dwg.entities:
            if isinstance(el, ezdxf.modern.lwpolyline.LWPolyline):
                l = l + 1
            elif isinstance(el, ezdxf.modern.spline.Spline):
                c = c + 1
        print('Se han añadido', l, 'lineas, ',
              c, 'curvas, al archivo dxf creado')

        dwg.saveas("./tmp/salida.dxf")

    else:
        # Salida archivo error
        print('Archivo erroneo')
        print(get_errors())
        print(get_capas())


def get_errors():

    if errores:
        return errores
    return False


def get_errors_square():

    if len(cuadrados) % 2 != 0:
        return True
    return False


def get_errors_rectangle():

    if len(rectangulos) % 3 != 0:
        return True
    return False


def get_capas():

    if capas_topografia:
        return capas_topografia
    return False
