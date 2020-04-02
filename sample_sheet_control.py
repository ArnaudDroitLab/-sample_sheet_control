#!/usr/bin/python3
# -*- coding: utf-8 -*

"""
    SAMPLE SHEET CONTROL
"""

import argparse
import sys
import warnings
import pandas as pd
from utils import exceptions as ex
from utils import colors as cl

PARSER = argparse.ArgumentParser(description='Control & sampleSheet parse')
PARSER.add_argument('-s', '--sample_sheet', required=False, help='sampleSheet')

ARG = PARSER.parse_args()

warnings.simplefilter(action='ignore', category=FutureWarning)

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

    client = ["SampleName", "Index1", "Index2",\
        "Concentration_(ng/ul)", "Volume_fourni"]

    header = ["FCID", "SampleSheetName", "Ligne", "No_Sample_si_en_tube", "Puits_si_en_plaque",\
        "SampleName", "Index1", "Indexseq1", "Index2", "Indexseq2", "Séquençage",\
        "Concentration_(ng/ul)", "Volume_fourni"]

    alpha = ['&', 'é', '"', "'", 'è', 'ç', 'à', '@', "~", 'ù', ',', '\t', '\n', " ", "#",\
        "B", "D", "E", "F", "H", "I", "J", "K", "L", "M", "O", "P", "Q", "R",\
        "S", "U", "V", "W", "X", "Y", "Z"]

    num = ["A", "T", "C", "G", "N"]

    protected = ['\.', '&', 'é', '"', "'", 'è', 'ç', 'à', '@',\
        'ù', ',', '\t', '\n', " ", "#", "~"]

    num.extend(alpha)
    alpha.extend(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

    #Reading of sample_sheet and data index
    try:
        sample_sheet = pd.read_excel(sample, sep=",", sheet_name="Sheet1")
        idi_index = pd.read_csv("data/IDI_index.csv", sep=",")
        neb_index = pd.read_csv("data/NEB_index_filter.csv", sep=",")
    except FileNotFoundError:
        print("\nL'un des fichiers suivant '{}{}{}' est introuvable, vérifier \
            le nom du fichier passé en argument ainsi que la présence des fichiers\
            'IDI_index.csv' & 'NEB_index_filter.csv' dans le répertoir data.".format(cl.RED, sample, cl.DEFAULT))
        sys.exit(1)

    #Index data information tolist()
    index_list = idi_index["i5_index"].tolist()
    index_list.extend(idi_index["i7_index"].tolist())

    index_list_neb = neb_index["I7_INDEX_READ"].tolist()
    index_list_neb.extend(neb_index["I5_INDEX_READ_NOVASEQ"].tolist())
    index_list_neb = list(set(index_list_neb))

    index_list.extend(index_list_neb)

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

    #Specific control on identifier sequences
    grouped = sample_sheet.groupby("Ligne")

    for name, group in grouped:
        index_seq_len_1, index_seq_len_2, index_seq_1, index_seq_2 = ([] for _ in range(4))
        diff_seq = False
        try:
            if group.Indexseq1.count() < len(group.Indexseq1):
                raise ex.EmptyCellIdx1
            if group.Indexseq2.count() == len(group.Indexseq2):
                for idx, row in group.iterrows():
                    index_seq_len_1.append(len(row["Indexseq1"]))
                    index_seq_len_2.append(len(row["Indexseq2"]))
                    index_seq_1.append(row["Indexseq1"])
                    index_seq_2.append(row["Indexseq2"])

                index_seq = index_seq_1
                index_seq.extend(index_seq_2)

                for idx in index_seq:
                    if idx not in index_list:
                        diff_seq = True

                try:
                    if len(set(index_seq_len_1)) > 1 or len(set(index_seq_len_2)) > 1: raise ex.LenWrong
                    if set(index_seq_len_2).pop() != 0 and set(index_seq_len_1).pop() != set(index_seq_len_2).pop(): raise ex.InegalLen
                except ex.LenWrong:
                    print("{} erreur -> {} Les séquences d'index pour la ligne {}{}{} ont des longueurs variable"\
                    .format(cl.RED, cl.DEFAULT, cl.YELLOW, name, cl.DEFAULT))
                    value.append(1)
                except ex.InegalLen:
                    print("{} erreur -> {} Les séquences d'index 1 et 2 pour la ligne {}{}{} n'ont pas la même longueur"\
                    .format(cl.RED, cl.DEFAULT, cl.YELLOW, name, cl.DEFAULT))
                    value.append(1)
                try:
                    if len(set(index_seq_1)) != len(index_seq_1) or len(set(index_seq_2)) != len(index_seq_2): raise ex.NotUnique
                except ex.NotUnique:
                    print("{} erreur -> {} Les séquences d'index pour la ligne {}{}{} ne sont pas unique"\
                    .format(cl.RED, cl.DEFAULT, cl.YELLOW, name, cl.DEFAULT))
                    value.append(1)
                try:
                    if diff_seq: raise ex.NotListed
                except ex.NotListed:
                    print("{} warning -> {} Certaines séquences d'index pour la ligne {}{}{} ne sont pas listé dans l'ensemble\
                    des index disponible".format(cl.YELLOW, cl.DEFAULT, cl.YELLOW, name, cl.DEFAULT))
                    value.append(1)
            elif group.Indexseq2.count() < len(group.Indexseq2) and group.Indexseq2.count() != 0:
                raise ex.EmptyCell

        except ex.EmptyCell:
            print("{} erreur -> {} Des cellules vides dans la colone 'Index_seq_2' sont retrouvé pour la ligne {}{}{}"\
            .format(cl.RED, cl.DEFAULT, cl.YELLOW, name, cl.DEFAULT))
            value.append(1)

        except ex.EmptyCellIdx1:
            print("{} erreur -> {} Des cellules vides dans la colone 'Index_seq_1' sont retrouvé pour la ligne {}{}{}"\
            .format(cl.RED, cl.DEFAULT, cl.YELLOW, name, cl.DEFAULT))
            value.append(1)


    #Replace empty cell by "1337oxd7"
    sample_sheet.fillna("", inplace=True)

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
            if len(sample_sheet[sample_sheet[columne] == ""]) > 0:
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
