# -*- coding: utf-8 -*-
#
# Prototype App, Geometric functions, layers and symbols.
#
# Required ezdxf.
#
# J. Eduardo Risco 27-03-2019
#

import math

import ezdxf

from app import app

### Layers  ###


def create_layers(dwg, file_user):
    '''
    This function  reads a file ,creates the layers defined by the
    user, adding them to model.
    '''

    layer_color = set()
    for i in file_user:
        layer_color.add((i[1], i[2]))

    for l in layer_color:
		color = app.config['CAD_COLORS'].index(l[1])   
        dwg.layers.new(name=l[0], dxfattribs={'color': color})

    # Obligatory layers
    dwg.layers.new('Points', dxfattribs={'color': 0})
    dwg.layers.new('Number_Points', dxfattribs={'color': 0})
    dwg.layers.new('Altitude', dxfattribs={'color': 0})
    dwg.layers.new('Label', dxfattribs={'color': 5})
    
### Geometrical ###

def create_points(dwg, msp, points):
    '''
    This function insert all the points in the 'Points' layer,
    the altitude in the 'Altitude' layer and the code in the 'Label' layer.
    '''
    # Defining Text, Elevation, and Label Styles
    dwg.styles.new('elevation', dxfattribs={'font': 'arial.ttf', 'width': 0.1})
    dwg.styles.new('label', dxfattribs={'font': 'times.ttf', 'width': 0.5})

    for p in points:
        msp.add_point((p[1][0], p[1][1]), dxfattribs={'layer': 'Points'})
        msp.add_text(p[1][2],
                     dxfattribs={
            'style': 'elevation',
            'height': 0.35,
            'layer': 'Altitude'
        }).set_pos(((p[1][0] + 0.35, p[1][1] + 0.35)), align='LEFT')
        msp.add_text(p[2],
                     dxfattribs={
            'style': 'label',
            'height': 0.35,
            'layer': 'Label'
        }).set_pos(((p[1][0] + 0.35, p[1][1] + 0.90)), align='LEFT')
        msp.add_text(p[0],
                     dxfattribs={
            'style': 'elevation',
            'height': 0.40,
            'layer': 'Number_Points'
        }).set_pos(((p[1][0] - 0.35, p[1][1] - 0.35)), align='RIGHT')


def create_circles(msp, circles, file_user):
    '''
    This function creates circles with radius defined by the
    user, and adds them to the model, in the corresponding layer.
    '''
    layer = ''
    for c in circles:
        code_line = c[3][1]
        for l in file_user:
            if code_line == l[0]:
                layer = l[1]
        msp.add_circle(
            (c[1][0], c[1][1]), c[3][0], dxfattribs={'layer': layer})


def create_lines(msp, lines, file_user):
    '''
   This function creates user-defined lines,and adds them to the model,
   in the corresponding layer.It also solves the case of unmeasured points
   and incorporates them into the line.
   '''
    layer = ''
    for p in lines:
        code_line = p[0][2]
        lin_coord = []
        for i, coord_points in enumerate(p):
            if len(coord_points) > 3 and isinstance(
                    coord_points[3], (tuple, int, float)) and i >= 1:
                point_a = p[i - 1]
                point_b = p[i]
                coord_a_x = point_a[1][0]
                coord_a_y = point_a[1][1]
                coord_b_x = point_b[1][0]
                coord_b_y = point_b[1][1]
                azimut, d = calculate_azimut_distance(
                    point_a, point_b)
                if isinstance(coord_points[3], (int, float)):
                    azimut = calculate_angle(azimut, coord_points[3])
                    inc_x, inc_y = calculate_increment_x_y(
                        azimut, abs(coord_points[3]))
                    coord_c_x = coord_a_x + inc_x
                    coord_c_y = coord_a_y + inc_y
                    lin_coord.append((coord_c_x, coord_c_y))
                else:
                    lin_coord.append(point_b[1])
                    for s in coord_points[3]:
                        azimut = calculate_angle(azimut, s)
                        inc_x, inc_y = calculate_increment_x_y(azimut, abs(s))
                        coord_c_x = coord_b_x + inc_x
                        coord_c_y = coord_b_y + inc_y
                        lin_coord.append((coord_c_x, coord_c_y))
                        coord_b_x = coord_c_x
                        coord_b_y = coord_c_y

            if coord_points[1] not in lin_coord:
                lin_coord.append(coord_points[1])
        for l in file_user:
            if code_line == l[0]:
                layer = l[1]
        msp.add_lwpolyline(lin_coord, dxfattribs={'layer': layer})


def create_curves(msp, curves, file_user):
    '''
    This function creates user-defined curves,
    and adds them to the model, in the corresponding layer.
    '''
    layer = ''
    for p in curves:
        code_line = p[0][2]
        lin_coord = []
        for coord_points in p:
            lin_coord.append(coord_points[1])
        for l in file_user:
            if code_line == l[0]:
                layer = l[1]
        msp.add_spline(lin_coord, dxfattribs={'layer': layer})


def create_squares(msp, squares, file_user):
    '''
    This function creates user-defined squares,
    and adds them to the model, in the corresponding layer.
    '''
    layer = ''

    for i in range(0, len(squares), 2):
        code_line = squares[i][3]
        line = []
        point_a = squares[i]
        point_b = squares[i + 1]
        coord_a_x = point_a[1][0]
        coord_a_y = point_a[1][1]
        coord_b_x = point_b[1][0]
        coord_b_y = point_b[1][1]

        line.append((coord_a_x, coord_a_y))
        line.append((coord_b_x, coord_b_y))
        azimut, distance = calculate_azimut_distance(point_a, point_b)
        azimut = azimut + 90

        for l in file_user:
            if code_line == l[0]:
                layer = l[1]

        for n in range(2):
            inc_x, inc_y = calculate_increment_x_y(azimut, distance)
            coord_c_x = coord_b_x + inc_x
            coord_c_y = coord_b_y + inc_y
            line.append((coord_c_x, coord_c_y))
            coord_a_x = coord_b_x
            coord_a_y = coord_b_y
            coord_b_x = coord_c_x
            coord_b_y = coord_c_y
            azimut = azimut + 90

        line.append((point_a[1][0], point_a[1][1]))
        msp.add_lwpolyline(line, dxfattribs={'layer': layer})


def create_rectangles(msp, rectangles, file_user):
    '''
    This function creates user-defined rectangles,
    and adds them to the model, in the corresponding layer.
    '''

    layer = ''

    for i in range(0, len(rectangles), 3):
        code_line = rectangles[i][3]
        line = []
        point_a = rectangles[i]
        point_b = rectangles[i + 1]
        point_c = rectangles[i + 2]
        coord_a_x = point_a[1][0]
        coord_a_y = point_a[1][1]
        coord_b_x = point_b[1][0]
        coord_b_y = point_b[1][1]
        coord_c_x = point_c[1][0]
        coord_c_y = point_c[1][1]

        line.append((coord_a_x, coord_a_y))
        line.append((coord_b_x, coord_b_y))
        line.append((coord_c_x, coord_c_y))

        azimut, distance = calculate_azimut_distance(point_a, point_b)
        azimut = azimut + 180

        for l in file_user:
            if code_line == l[0]:
                layer = l[1]

        inc_x, inc_y = calculate_increment_x_y(azimut, distance)

        coord_d_x = coord_c_x + inc_x
        coord_d_y = coord_c_y + inc_y
        line.append((coord_d_x, coord_d_y))
        line.append((coord_a_x, coord_a_y))
        msp.add_lwpolyline(line, dxfattribs={'layer': layer})


def insert_symbols(msp, points, file_user):
    '''
    This function inserts symbols into the coded points.
    '''
    layer = ''
    for p in points:
        if len(p) == 4:
            if p[2]in('TC', 'TR'):
                code_point = p[3]
            elif p[2] == 'TX':
                code_point = p[3][1]
            else:
                code_point = p[2]
        else:
            code_point = p[2]

        for l in file_user:
            if code_point == l[0]:
                code_point=l[3]
                layer=l[1]
        msp.add_blockref(code_point, (p[1][0], p[1][1]),dxfattribs={'layer': layer})
          

### Mathematical ###


def calculate_azimut_distance(a, b):
    '''
    Function returns the calculated azimuth and distance between two points.
    '''

    coord_a_x = a[1][0]
    coord_a_y = a[1][1]
    coord_b_x = b[1][0]
    coord_b_y = b[1][1]
    inc_x = coord_b_x - coord_a_x
    inc_y = coord_b_y - coord_a_y

    angle = math.atan((inc_x) / (inc_y))
    distance = math.sqrt((inc_x)**2 + (inc_y)**2)

    if inc_x > 0 and inc_y > 0:
        azimut = math.degrees(angle)
    elif inc_x > 0 and inc_y < 0 or inc_x < 0 and inc_y < 0:
        azimut = math.degrees(angle) + 180
    else:
        azimut = math.degrees(angle) + 360
    return azimut, distance


def calculate_increment_x_y(azimut, distance):
    '''
    Function returns the increment of 'x' and 'y' from
    of an azimuth and a distanc
    '''

    inc_x = (math.sin(math.radians(azimut)) * distance)
    inc_y = (math.cos(math.radians(azimut)) * distance)
    return inc_x, inc_y


def calculate_angle(azimut, distance):
    '''
    Function returns azimuth variation using distance sign 
    '''

    if distance >= 0:
        azimut = azimut + 90
    else:
        azimut = azimut - 90
    return azimut
