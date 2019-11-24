#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 11:13:35 2019

@author: Jonathan Cook

This module exists to curate the Combined_Annotations.xlsx file found in the
Google Drive folder.

Brief descriptions of what a function's purpose can be found directly beneath
its header.

Functions are sotred based on use with a section describing comment above
each function group.

Note that these are rather specific functions for the purpose of cleaning and
using a particularly formatted Excel Sheet. This is not a perfectly general
module.

All code is written under pep8 guidelines for readability so if you must add
anyything new please follow their rules.
"""


import pandas as pd
import numpy as np
import statistics as stats


# Functions clean or organize columns based on string content


def get_sheet(fileName, sheetName):
    """
    Clean column names for input sheet.
    Exctract records marked 'include' for a given sheet.
    """
    thisSheet = pd.read_excel(fileName, sheetName)
    # clean column names
    thisSheet.columns = thisSheet.columns.str.strip()
    thisSheet.columns = thisSheet.columns.str.lower()
    thisSheet.columns = thisSheet.columns.str.replace(" ", "_")
    thisSheet.columns = thisSheet.columns.str.replace("-", "_")
    thisSheet.columns = thisSheet.columns.str.replace("/", "_")
    thisSheet.columns = thisSheet.columns.str.replace("(", "_")
    thisSheet.columns = thisSheet.columns.str.replace(")", "_")
    # extract rows tagged "include" & return cleaned dataframe
    thisSheet.exclude_include.str.lower()
    outSheet = thisSheet[thisSheet.exclude_include == "include"]
    return outSheet


def clean_column(inCol):
    """
    Clean up string values in cells by lowering and removing white spaces
    or special characters
    """
    for i in range(0, len(inCol)):
        thisStr = inCol[i]
        thisStr = thisStr.strip()
        thisStr = thisStr.lower()
        thisStr = thisStr.replace(" ", "_")
        thisStr = thisStr.replace("/", "_")
        thisStr = thisStr.replace("/ ", "_")
        thisStr = thisStr.replace(" /", "_")
        thisStr = thisStr.replace("__", "_")
        if thisStr == "in_vitro_in_vivo":
            inCol[i] = "in_vivo"
        elif thisStr == "in_vivo_in_vitro_clinical_trial":
            inCol[i] = "in_vivo"
        elif thisStr == "in_vivo_in_vitro":
            inCol[i] = "in_vivo"
        elif thisStr == "clinical_observational_study":
            inCol[i] = "clinical_observational"
        else:
            inCol[i] = thisStr
    return inCol


def clean_names(names):
    """
    Clean up the updated names from the data sheet. Remove values after any
    '/' values
    """
    for i in range(0, len(names)):
        thisName = names[i]
        stopPoint = thisName.find('/')
        if stopPoint > 0:
            thisName = thisName[0:stopPoint]
        thisName = thisName.strip()
        thisName = thisName.lower()
        names[i] = thisName
    return names


def disease_dict(inSheet):
    """
    Construct a dictionary object of drug names
    Imported from Yiwen's initial script
    """
    drugs = inSheet.drug_names.unique()
    dis = dict()
    for name in drugs:
        diseases = inSheet[inSheet["drug_names"] == name]["disease"]
        diseases = diseases.unique().tolist()
        dis[name] = ", ".join(diseases)
    dis_name = pd.DataFrame.from_dict(dis, orient="index").reset_index()
    dis_name.columns = ["drug_name", "disease"]
    return dis_name


# Functions combine specified columns within sheets


def update_names(inSheet):
    """
    Search for updated drug name values and replace existing non_cancer_drug
    value if needed.
    """
    idxList = inSheet.index
    newNames = []
    for i in range(0, len(idxList)):
        if pd.isna(inSheet.updated_drug_name[idxList[i]]):
            # no udated drug name
            newNames.append(inSheet.non_cancer_drugs[idxList[i]])
        else:
            # there is an updated drug name found
            newNames.append(inSheet.updated_drug_name[idxList[i]])
    return newNames


def update_studies(inSheet):
    """
    Search for any values in study_type_new_ and create whole study type
    column
    """
    idxList = inSheet.index
    studies = []
    for i in range(0, len(idxList)):
        if pd.isna(inSheet.study_type_new[idxList[i]]):
            # no udated study type
            studies.append(inSheet.study_type[idxList[i]])
        else:
            # there is an updated drug name found
            studies.append(inSheet.study_type_new[idxList[i]])
    return studies


# Functions count occurences of specified variables


def get_count(inSheet, inCol):
    """
    compare unique drug name values and count occurences of study types and
    associations per name
    """
    uNames = inSheet.drug_names.unique()
    uVals = inSheet[inCol].unique()
    outFrame = pd.DataFrame()
    for i in range(0, len(uVals)):
        # create output dataframe of all zeros to be added to later
        outFrame[uVals[i]] = np.zeros(len(uNames), dtype=int)
    for j in range(0, len(uNames)):
        # loop through each unique name value
        thisName = uNames[j]
        for k in range(0, len(inSheet)):
            # loop through each row in overall trimmed sheet for each
            # unique value
            if thisName == inSheet['drug_names'][k]:
                # unique drug found in larger dataframe
                outFrame[inSheet[inCol][k]][j] += 1
    return outFrame


def performed_count(inSheet):
    """
    Sums values of each row in the count dataframe to determine number of
    studies performed
    """
    totalCounts = np.zeros(len(inSheet), dtype=int)
    for i in range(0, len(inSheet)):
        totalCounts[i] = inSheet.loc[i].sum()

    return totalCounts


def score_each_study(inSheet):
    """
    Read allTrimmed sheet and apply branching scored method
    """
    scoreVector = []
    for i in range(0, len(inSheet)):
        row = inSheet.loc[i]
        study = row.study_type
        if study == "in_vivo":
            eVal = 2
        elif study == "in_vitro":
            eVal = 1
        elif study == "clinical_trial":
            eVal = 5
        elif study == "clinical_observational":
            eVal = 3
        elif study == "clinical_case_report":
            eVal = 2
        elif study == "other":
            eVal = 0
        assoc = row.assoc
        if assoc == "inconclusive" or assoc == "no_effect":
            eVal = -eVal / 3
        elif assoc == "detrimental":
            eVal = -eVal
        scoreVector.append(eVal)
    return scoreVector


def sum_scores(inSheet):
    """
    Sum scores from branching scoring methodology into a single vector
    with records unique to drug names
    """
    uNames = inSheet.drug_names.unique()
    scoreSum = []
    for j in range(0, len(uNames)):
        # loop through each unique name value
        thisName = uNames[j]
        for k in range(0, len(inSheet)):
            # loop through each row in overall trimmed sheet for each
            # unique value
            if thisName == inSheet['drug_names'][k]:
                # unique drug found in larger dataframe
                scoreSum[j] = scoreSum[j] + inSheet['scores'][k]
    return scoreSum


def scale_rows(inSheet):
    """
    scale count of different scores from count framed score dataframe
    """
    scoreVec = np.zeros(len(inSheet))
    for i in range(0, len(inSheet)):
        # loop through each row
        row = inSheet.loc[i]
        for j in range(0, len(inSheet.columns)):
            # loop through each column at each row
            scalar = inSheet.columns[j]
            scoreVec[i] = scoreVec[i] + (scalar * row[scalar])
    return scoreVec


# Function utilizes above functions to generate an output file for LineUp Demo


def make_csv():
    """
    Function written by Jonathan Cook to process Combined_Annotations for his
    LineUp.js demo
    """
    fullFile = pd.ExcelFile("Combined_Annotations.xlsx")

    # import each sheet of data in combined annotations
    firstBatch = get_sheet(fullFile, "First_Batch")
    secondBatch = get_sheet(fullFile, "Second_Batch")
    thirdBatch = get_sheet(fullFile, "Third_Batch")
    tightBatch = get_sheet(fullFile, "Tight_Samples")
    randomBatch = get_sheet(fullFile, "Random_Sample")

    # generate a massive dataframe for all sheets (use to loop through)
    allSheets = pd.concat([firstBatch, secondBatch, thirdBatch, tightBatch,
                           randomBatch], ignore_index=True)

    # extract and clean drug names across all sheets
    allNames = clean_names(update_names(allSheets))

    # extract and clean studies across all sheets
    allStudies = clean_column(update_studies(allSheets))

    # extract and clean all associations across all sheets
    allAssoc = clean_column(list(allSheets.association))

    # generate a new dataframe of non-unique names, studies, and associations
    allTrimmed = pd.DataFrame()
    allTrimmed['drug_names'] = allNames
    allTrimmed['disease'] = allSheets.disease
    allTrimmed['study_type'] = allStudies
    allTrimmed['assoc'] = allAssoc
    allTrimmed['scores'] = score_each_study(allTrimmed)

    # get count of value frequency and create an array with count values
    studiesCount = get_count(allTrimmed, 'study_type')
    assocCount = get_count(allTrimmed, 'assoc')

    # get total number of studies performed using assocCount dataframe
    studyNum = performed_count(assocCount)

    # get combination array of disease names
    dis = disease_dict(allTrimmed)

    # sort disease name dataframe for appending to final dataframe object
    dis = dis.sort_values(by='drug_name')

    # create final datafram with counts
    countFrame = pd.DataFrame()
    countFrame['drug_name'] = allTrimmed.drug_names.unique()
    countFrame = countFrame.join(studiesCount)
    countFrame = countFrame.join(assocCount)
    countFrame['number_studies'] = studyNum

    # get number of score value occurrences from allTrimmed, and run through
    # another function to use branching scoring methodology
    scoreFrame = get_count(allTrimmed, 'scores')
    countFrame['overall_score'] = scale_rows(scoreFrame)

    # sort countFrame by drug names for appending disease
    countFrame = countFrame.sort_values(by='drug_name')
    countFrame['disease'] = dis['disease']

    # sort final frame by methodology score
    countFrame = countFrame.sort_values(by='overall_score', ascending=False)

    # generate csv file from countFrame
    countFrame.to_csv("JC_out.csv")

print("Module Loaded\n")