#!/usr/bin/python3
# -*- coding: utf-8 -*

"""
    SAMPLE SHEET CONTROL
"""

import argparse
import sys
import pandas as pd
from utils import exceptions as ex
from utils import colors as cl

PARSER = argparse.ArgumentParser(description='Control & sampleSheet parse')
PARSER.add_argument('--sample_sheet', required=False, help='sampleSheet')

ARG = PARSER.parse_args()

def control_char(protected, sample_sheet, colonne):
    """Try Catch control"""
    try:
        char_found = []
        for char_protec in protected:
            if len(sample_sheet[sample_sheet[colonne].astype(str).str.contains(char_protec, case=False)]) > 0:
                if char_protec not in char_found:
                    char_found.append(char_protec)

        if len(char_found) > 0:
            raise ex.ForbidenChar

    except ex.ForbidenChar:
        print("\n{}{}{}WARNING{}{}{}".format(cl.YELLOW, cl.BOLD, cl.UNDERLINED,\
            cl.RESETUNDERLINED, cl.RESETBOLD, cl.DEFAULT))
        print("Des caractères proscrits ont été retrouvé dans la colonne {}{}{} :"\
            .format(cl.YELLOW, colonne, cl.DEFAULT))

        for count, ele in enumerate(char_found, 1):
            print("{} : {}{}{}".format(count, cl.RED, ele, cl.DEFAULT))

        return 1
    return 0

def reading_sample_sheet(sample):
    """Read and control sample_sheet format"""

    # Variable declaration
    idx = 0
    value = []

    client = ["SampleName", "Index1", "Indexseq1", "Index2", "Indexseq2",\
        "Concentration_(ng/ul)", "Volume_fourni"]

    header = ["FCID", "SampleSheetName", "Ligne", "No_Sample_si_en_tube", "Puits_si_en_plaque",\
        "SampleName", "Index1", "Indexseq1", "Index2", "Indexseq2", "Séquençage",\
        "Concentration_(ng/ul)", "Volume_fourni"]

    alpha = ['&', 'é', '"', "'", 'è', 'ç', 'à', '@', "~", 'ù', ',', '\t', '\n', " ",\
        "B", "D", "E", "F", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R",\
        "S", "U", "V", "W", "X", "Y", "Z"]

    num = ["A", "T", "C", "G", "#"]

    protected = ['\.', '&', 'é', '"', "'", 'è', 'ç', 'à', '@',\
        'ù', ',', '\t', '\n', " ", "#", "~"]

    num.extend(alpha)

    #Reading of sample_sheet
    try:
        sample_sheet = pd.read_excel(sample, sep=",", sheet_name="Sheet1")
    except FileNotFoundError:
        print("\nLe fichier '{}{}{}' est introuvable, vérifier \
            le nom du fichier passé en argument.".format(cl.RED, sample, cl.DEFAULT))
        sys.exit(1)

    #Verification columns number
    try:
        if len(sample_sheet.columns) != 13:
            raise ex.LenWrong
    except ex.LenWrong:
        print("\nLe nombre de colonnes de la sample sheet n'est pas celui normalement attendu")
        sys.exit(1)

    sample_sheet.columns = header

    #Remove presentation row
    while idx < 21:
        sample_sheet.drop([idx], inplace=True)
        idx += 1

    #Replace empty cell by "1337"
    sample_sheet.fillna(1337, inplace=True)

    #Control the containing char in a specific column
    value.append(control_char(protected, sample_sheet, "SampleName"))
    value.append(control_char(protected, sample_sheet, "Index1"))
    value.append(control_char(protected, sample_sheet, "Index2"))
    value.append(control_char(alpha, sample_sheet, "Indexseq1"))
    value.append(control_char(alpha, sample_sheet, "Indexseq2"))
    value.append(control_char(num, sample_sheet, "Concentration_(ng/ul)"))
    value.append(control_char(num, sample_sheet, "Volume_fourni"))

    #Verify if empty cell are found in the data for column write by client.
    try:
        columne_name = []
        for columne in client:
            if len(sample_sheet[sample_sheet[columne] == 1337]) > 0:
                columne_name.append(columne)

        if len(columne_name) > 0:
            raise ex.ForbidenChar

    except ex.ForbidenChar:
        print("\n{}{}{}WARNING{}{}{}".format(cl.YELLOW, cl.BOLD, cl.UNDERLINED,\
            cl.RESETUNDERLINED, cl.RESETBOLD, cl.DEFAULT))
        print("Des cases non remplies sont présents dans la (les) colonne(s) :")

        for count, ele in enumerate(columne_name, 1):
            print("{} : {}{}{}{}{}{}{}".format(count, cl.LIGHTRED, cl.BOLD, cl.UNDERLINED, ele,\
                cl.RESETUNDERLINED, cl.RESETBOLD, cl.DEFAULT))

        value.append(1)

    #If no mistake are founds, print OK for quality control
    if 1 not in value:
        print("\nLa sample sheet semble être correctement formaté\n\n"\
            "caractères particuliers : {0}{1}{2}\n"\
            "Nombre de colonnes : {0}{3}{2}".format(cl.GREEN, "0", cl.DEFAULT, "13"))

if __name__ == "__main__":
    reading_sample_sheet(ARG.sample_sheet)
