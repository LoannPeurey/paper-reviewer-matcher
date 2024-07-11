"""
=========================
preparing conflicts
=========================

Use the affiliation column to find mentor and mentees that belong to the same university / organization
Generates then a PersonID for mentees and PaperID - PeresonIDList for mentors, where PersonIDList is a ;
separated list of people with the same affiliation

"""
import argparse
import sys
import logging

import numpy as np
import pandas as pd
import pathlib
from functools import partial

file_path = pathlib.Path(__file__).parent

INSTITUTION_COLUMNS = ['std_institution_1', 'std_institution_2']

def main(mentor_file, mentee_file, out_mentor_file, out_mentee_file):
    mentors = pd.read_csv(mentor_file)
    mentees = pd.read_csv(mentee_file)

    mentees['PersonID'] = mentees.index
    mentors['PaperID'] = mentors.index

    mentors = compute_conflicts(mentors, mentees)

    mentees.to_csv(out_mentee_file, index=False)
    mentors.to_csv(out_mentor_file, index=False)

def _parse_args(argv):
    parser = argparse.ArgumentParser(description='path of mentors/mentees files')
    parser.add_argument('--mentor-file', help='Path to data directory.',
                        default=file_path / '../raw_data/StandardizedMentorList.csv')
    parser.add_argument('--mentee-file', help='Path to metadata file base on path-data',
                        default=file_path / '../raw_data/StandardizedMenteeList.csv')
    parser.add_argument('--out-mentor-file', help='name of the classification file',
                        default=file_path / '../preprocessed_data/Mentors.csv')
    parser.add_argument('--out-mentee-file', help='Prefix output file.',
                        default=file_path / '../preprocessed_data/Mentees.csv')
    args = parser.parse_args(argv)
    args = vars(args)

    return args

def compute_conflicts(mentors, mentees):
    """
    Compute conflict for a given dataframe
    """
    find_corresponding_conflicts_people = partial(find_corresponding_conflicts, df=mentees)
    mentors['PersonIDList'] = mentors.apply(find_corresponding_conflicts_people, axis=1)

    return mentors

def find_corresponding_conflicts(affi, df):
    """
    find conflicts and append them for this row
    """
    conflicts = set()
    for coltee in INSTITUTION_COLUMNS:
        for coltor in INSTITUTION_COLUMNS:
            conflicts.update(df[df[coltee] == affi[coltor]].index)
    conflicts = df.loc[conflicts]
    return ';'.join(conflicts['PersonID'].astype(str).to_list())

if __name__ == '__main__':
    pgrm_name, argv = sys.argv[0], sys.argv[1:]
    args = _parse_args(argv)

    main(**args)

