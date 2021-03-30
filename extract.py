#!/usr/bin/python

# ------------------------------------------------------------------------------- #
# extract.py - run a extraction on a Canvas submission file                       #
# Creates extracted directory structure as described in README                    #
# Author: Colten G.                                                               #
# Date: 4/8/18                                                                    #
# ------------------------------------------------------------------------------- #
from __future__ import print_function

import argparse
import codecs

import os
import csv
from zipfile import ZipFile
import sys

import shutil
import tarfile


parser = argparse.ArgumentParser(description='Extract and rename files')
parser.add_argument('source', metavar='SOURCE_FILE', action='store',
                    help='The submission file from Canvas')
parser.add_argument('assignment', metavar='ASSIGNMENT', action='store',
                    help='The name of the folder that holds the assignments. ie. A3')
parser.add_argument('setName', metavar='SET_NAME', action='store',
                    help='The current set name. ie. Set3')
parser.add_argument('semester', metavar='SEMESTER', action='store',
                    help='The current semester. ie. spring2018')
parser.add_argument('courseList', metavar='SEMESTER_CSV', action='store',
                    help='The csv file that contains the map from username to section')


args = parser.parse_args()
source = args.source
assignment = args.assignment
setName = args.setName
semester = args.semester
courseList = args.courseList

try:
    importFile = csv.DictReader(codecs.open(courseList,  encoding="utf-8-sig"))
    classMap = {}
    for r in importFile:
        if r['Student'] == "" or r['Section'] == "":
            continue
        classMap[r['Student'].replace("-", "").replace(", ", "").replace(" ", "").lower()] = r['Section'].replace("'", "")[-1]
except Exception, e:
    print("Error loading semester csv", file=sys.stderr)
    exit(1)

if not os.path.exists(assignment):
    os.makedirs(assignment)

semesterPath = os.path.join(assignment, semester)

if not os.path.exists(semesterPath):
    os.makedirs(semesterPath)

tmpDir = os.path.join(semesterPath, 'tmp')

try:
    count = 0
    submissionsZip = ZipFile(source)
    for submissionOriginalFileName in submissionsZip.namelist():
        try:
            if (not submissionOriginalFileName.endswith('.tar.gz') and not submissionOriginalFileName.endswith('.tar') and not submissionOriginalFileName.endswith('.zip')):
                continue
            studentName = (submissionOriginalFileName.split('_'))[0]

            sectionPath = ""
            if studentName in classMap:
                sectionPath = os.path.join(semesterPath, classMap[studentName])
            else:
                sectionPath = os.path.join(semesterPath, 'unknownSection')
            studentNamePath = os.path.join(sectionPath, studentName)
            studentZipPath = os.path.join(tmpDir, submissionOriginalFileName)
            if not os.path.exists(tmpDir):
                os.makedirs(tmpDir)
            submissionsZip.extract(submissionOriginalFileName, tmpDir)
            if not os.path.exists(studentNamePath):
                os.makedirs(studentNamePath)
            found = False
            if '.zip' in submissionOriginalFileName:
                studentZip = ZipFile(studentZipPath)
                for studentFile in studentZip.namelist():
                    if os.path.join(setName.lower(), assignment.lower()) in os.path.normpath(studentFile.lower()):
                        if '.o' in studentFile:
                            continue
                        if '.out' in studentFile:
                            continue
                        studentZip.extract(studentFile, studentNamePath)
                        found = True
            elif (submissionOriginalFileName.endswith('.tar.gz')):
                tar = tarfile.open(studentZipPath, "r:gz")
                subdir_and_files = []
                for s in tar.getmembers():
                    if s.name.startswith(os.path.join(setName, assignment)):
                        subdir_and_files.append(s)

                tar.extractall(studentNamePath, subdir_and_files)
                if subdir_and_files:
                    found = True
                tar.close()
            elif (submissionOriginalFileName.endswith(".tar")):
                tar = tarfile.open(studentZipPath, "r:")
                subdir_and_files = []
                for s in tar.getmembers():
                    if s.name.startswith(os.path.join(setName, assignment)):
                        subdir_and_files.append(s)
                tar.extractall(studentNamePath, subdir_and_files)
                if subdir_and_files:
                    found = True
                tar.close()
            if not found:
                print("Did not extract assignment from: " + submissionOriginalFileName +
                      "\nCheck to see if " + os.path.join(setName, assignment) + " exists")
            count += 1
        except Exception, ex:
            print("Error Extracting: " + submissionOriginalFileName, file=sys.stderr)
            print(ex)
except Exception, ex2:
    print("Error Extracting from submission folder: ", file=sys.stderr)
    print(ex2)


if os.path.exists(tmpDir):
    shutil.rmtree(tmpDir)
