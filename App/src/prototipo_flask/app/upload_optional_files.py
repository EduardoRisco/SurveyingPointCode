# -*- coding: utf-8 -*-
#
# Module for uploading optional files.
# confir_user and dxf_symbols
#
# Required ezdxf.
#
# J. Eduardo Risco 27-03-2019
#

import csv

import ezdxf

config_user_init= []
errors_config_user_init = []
symbols = []
file_symbols_dxf = ''


#file_config_user = 'tmp/config_usuario_correcta.txt'


def upload_file_config(entrada):
    '''
    This function reads a user configuration file,
    contains topographic codes, cad layers, colors and symbols.
    '''
    try:
        global config_user_init
        global errors_config_user_init
        errors_config_user_init = []
        config_user_init = []

        with open(entrada) as File:
            reader = csv.DictReader (File,delimiter=';',strict=True)
            for row in reader:
               config_user_init.append(dict(row))

        print(get_config_user())       

    except (IOError, NameError) as e:
        print(e)


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

    if errors_config_user_init:
        return False
    else:
        return config_user_init


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


