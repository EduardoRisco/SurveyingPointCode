# -*- coding: utf-8 -*-
#
# Prototype App, converter to dxf
#
# Required PLY (Python Lex-Yacc).
# Required ezdxf.
#
# J. Eduardo Risco 21-03-2019
#

import ply.lex as lex
import ply.yacc as yacc

import ezdxf
from app.geometric_tools import create_layers, create_points, create_circles
from app.geometric_tools import create_lines, create_curves, create_squares 
from app.geometric_tools import create_rectangles
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
    '''This function reads a file with topographic survey data, 
    translating the points codes in several geometric elements.
    '''

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
        capas_topografia = set()
        dicc_capas = {}
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
            # Using the parser
            punto = parser.parse(line)
            # Detection of incorrect input file
            if not punto:
                err = True
                # Capturing Errors
                errores.append([n_line, line])

            else:
                # Getting the layer code
                if len(punto) == 4 and (punto[2] == "TR" or punto[2] == "TC"):
                    codigo_capa = punto[3]
                elif punto[2] == "TX":
                    codigo_capa = punto[3][1]
                else:
                    codigo_capa = punto[2]
                # Verification that the layers do not exist in the dictionary
                # if they do not exist they are created
                # and the first point is added to that layer
                if codigo_capa not in capas_topografia:
                    dicc_capas[codigo_capa] = [punto]
                    capas_topografia.add(codigo_capa)
                else:
                    # Add points having the same code to their
                    # corresponding element in the dictionary
                    if codigo_capa in dicc_capas:
                        lista = dicc_capas.get(codigo_capa)
                        lista.append(punto)
                        dicc_capas[codigo_capa] = lista
            line = f.readline()

        # Decoding of lines, curves and other elements
        for ptos in dicc_capas:
            linea_iniciada = False
            curva_iniciada = False
            for pto in dicc_capas.get(ptos):
                puntos.append(pto)
                if pto[2] not in ('TC', 'TR', 'TX'):
                    if len(pto) > 3 and not isinstance(pto[3],
                                                       (tuple, int, float)):
                        if pto[3] == 'I':
                            if linea_iniciada:
                                # If another 'I' is found, the line closes
                                # and another line begins.
                                lineas.append(linea)
                                linea = []
                                linea.append(pto)
                                linea_iniciada = True
                            # If there is no line in that layer,
                            # the first line will be created.
                            else:
                                linea = []
                                linea.append(pto)
                                linea_iniciada = True
                        elif pto[3] == 'IC':
                            if curva_iniciada:
                                # If another 'IC' is found, the curve closes
                                # and another curve begins.
                                curvas.append(curva)
                                curva = []
                                curva.append(pto)
                                curva_iniciada = True
                            # If there is no curve in that layer,
                            # the first curve will be created.
                            else:
                                curva = []
                                curva.append(pto)
                                curva_iniciada = True
                        # Add points to the curve
                        elif pto[3] == 'C' and curva_iniciada:
                            curva.append(pto)
                    elif len(pto) == 4 and linea_iniciada:
                        linea.append(pto)
                    # Add points to the line
                    elif linea_iniciada:
                        linea.append(pto)
                # Save existing circles
                elif pto[2] == 'TX':
                    circulos.append(pto)
                # Save existing squares
                elif pto[2] == 'TC':
                    cuadrados.append(pto)
                # Save existing rectangles
                elif pto[2] == 'TR':
                    rectangulos.append(pto)

            # If there are no more elements in the layer,
            # lines and curves are closed.
            if linea:
                lineas.append(linea)
                linea = []
            if curva:
                curvas.append(curva)
                curva = []

        f.close()

    except (IOError, NameError) as e:
        print(e)


def genera_dxf(download_folder):
    '''
    This function generates a dxf file.
    '''

    # Example of user file, topographical code, cad layer and layer color.
    file_user = [
        ['E', 'Edificio', (38, 140, 89)], ['A', 'Acera', 0],
        ['FA', 'Farola', 2], ['TEL', 'Telecomunicaciones', 3],
        ['RE', 'Red_Electrica', 161], ['SAN', 'Saneamiento', 220],
        ['M', 'Muro', 1], ['B', 'Bordillo', 0],
        ['B1', 'Bordillo', 0], ['R', 'Relleno', 0],
        ['ARB', 'Arbol', 60], ['C', 'Calzada', 141],
        ['C1', 'Calzada', 141]]

    #### Pendiente de modificar en función de los errores obtenidos ####
    if line == "" and not err:
        dwg = ezdxf.new('AC1018')

        # Create the model space.
        msp = dwg.modelspace()

        # Creating required layers.
        create_layers(dwg, file_user)
        # Adding points to model.
        create_points(dwg, msp, puntos)
        # Adding circles to model.
        create_circles(msp, circulos, file_user)
        # Adding lines to model.
        create_lines(msp, lineas, file_user)
        # Adding curves to model.
        create_curves(msp, curvas, file_user)
        # Adding squares to model.
        create_squares(msp, cuadrados, file_user)
        # Adding rectangles to model.
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

        dwg.saveas(download_folder)

    else:
        # Error file output
        print('Archivo erroneo')
        print(get_errors())
        print(get_capas())


def get_errors():
    '''
    This function returns the errors of the input file
    '''

    if errores:
        return errores
    return False


def get_errors_square():
    '''
    This function returns error, if the number of elements
    defined to form squares, is not correct.
    '''

    if len(cuadrados) % 2 != 0:
        return True
    return False


def get_errors_rectangle():
    '''
    This function returns error, if the number of elements
    defined to form rectangles, is not correct.
    '''

    if len(rectangulos) % 3 != 0:
        return True
    return False


def get_capas():
    '''
    This function returns a list with topographic codes. 
    '''

    if capas_topografia:
        return capas_topografia
    return False
