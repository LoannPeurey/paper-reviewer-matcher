#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 09:36:18 2022
import and prepare data to be used in the matching process, it is 
@author: lpeurey
"""
import sys
from pathlib import Path
import os

file_path = Path(__file__).parent
#sys.path.append('../..')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from ccn.ccn_paper_reviewer_matching_2019 import assign_articles_to_reviewers, preprocess
import pandas as pd


ACADEMIA_LEVELS = {
"High School Student":1,
"Research enthusiast":1,
'Attending a mindfulness training program through UCLA':1,
'Science Communicator ' :1,
 
"Undergraduate student":2 ,
'Post-bac (graduated with undergrad degree but researching in academia)': 2,
'Postbac':2,
"Lab manager/Post-bacc RA":2 , 
"Lab Manager/Student":2, 
"M.Sc transitioning to PhD":2 , 
"MA student":2 , 
"MSc Student":2 ,
'MSc. Student':2, 
"Computational Linguistics Dual (CLD) Degree student (M.Sc. in CL and B.Tech in Computer Science)":2 , 
"M.Sc. Student (Completed)":2 ,
"MS Student ":2 , 
"Post bacc researcher":2 , 
"Post-bac technical associate":2 , 
"Post-bac Research Assistant":2 , 
"Research Assistant/Lab Manager":2 , 
"Research Assistant":2 , 
"Research Assistant / Lab Manager" : 2 , 
"Post-baccalaureate researcher":2 ,
"Post-baccalaureate researcher ":2 , 
"Research assistant (post-bacc)":2, 
"Clinical Research Assistant and Data Analyst" : 2, 
"Postbac researcher (pre-PhD)" : 2, 
'MSc in Neuropsychology/ Research assistant': 2,
'Research assistant (pregrad)':2, 
'Educator, graduated MA in 2020' : 2, 
'Postbac Researcher/Incoming MSc student':2,
'Post-bac research assistant':2,
'Research Assistant ' : 2,
'Research assistant (post-undergraduate)' : 2,
'MPhil Student ': 2,
'Not currently enrolled at an institution. Continuing research w/ former undergrad advisor': 2,

'Looking at Doctorate Programs/Labs':3,
'Research assistant (completed MA)' : 3,
'Graduating student' : 3, #placed one level above just in case (could be different graduations)
'Lab manger & incoming PhD student':3,
"PhD student":3 ,
'Lab Manager / Researcher':3,
'MD/PhD Student' : 3,
'Recent M.Sc. graduate looking for a job outside academia  ' : 3,

"Unemployed, but waiting on news for a postdoc position. I'm nominally part of the lab I hope to get the position in. ": 4, 
'Recent PhD Graduate': 4 , 
"Postdoc":4 , 
"Research Scientist":4 , 
"Research Scientist (in academia, post-postdoc)":4  , 
"Researcher outside of academia":4 , 
"Research Associate":4 , 
"Research Staff":4 , 
"Government but pursuing research":4 , 
'Employee':4,
'Cognitive Anthropologist postdoc but not in a specific program/yet. My main area is in bio neuro also interested in animal cognition but could not choose both on this form.':4,
'PhD Candidate and incoming research assistant professor at Brown University': 4,
'Assistant Lecturer & PhD Student ' : 4,

"Adjunct/Visiting Professor/Lecturer":5 , 
"Teacher":5 , 
"Instructor":5,
'Teacher, prospective researcher':5,

"Assistant Professor":6,

"Associate Professor":7 , 
"Former Associate Professor, current industry researcher":7,
'Research Faculty':7,

"Full Professor":8,
}

#complexity n*m where n=number of mentors, m=number of mentees
#using a sort and then go through the levels would be more efficient
#using a set instead of a list should be better
def add_higher_level_mentees(row,mentees):
    cur_level = ACADEMIA_LEVELS[row['Status']]
    to_add=[]
    for i, mentee in mentees.iterrows():
        if ACADEMIA_LEVELS[mentee['Status']] >= cur_level:
            to_add.append(str(mentee['PersonID']))
    if len(to_add):
        if len(row['PersonIDList']):
            return ';'.join(list(set(str(row['PersonIDList']).split(';') + to_add)))
        else:
            return ';'.join(to_add)
    else:
        return row['PersonIDList']


MAX_TIME_DIFF_ACCEPTABLE = 5
#complexity n*m where n=number of mentors, m=number of mentees
#using a sort and then go through the levels would be more efficient
#using a set instead of a list should be better
def add_mentees_in_far_timezone(row,mentees):
    cur_tdiff = row['timediff']
    if pd.isnull(cur_tdiff): return row['PersonIDList']
    to_add=[]
    for i, mentee in mentees.iterrows():
        if not pd.isnull(mentee['timediff']) and abs(mentee['timediff'] - cur_tdiff) > MAX_TIME_DIFF_ACCEPTABLE:
            to_add.append(str(mentee['PersonID']))
    if len(to_add):
        if len(row['PersonIDList']):
            return ';'.join(list(set(str(row['PersonIDList']).split(';') + to_add)))
        else:
            return ';'.join(to_add)
    else:
        return row['PersonIDList']

def build_abstract_mentor(row):
    """
    we build the abstract by concatenating the different area to match on
    the program uses tf-idf as a weighting solution, so the fields that should bare more importance
    should be repeated the same way for the mentor and mentee abstracts
    """
    res = ''
    res += ' ' + str(row["Main_Research_Area_1"])
    res += ' ' + str(row["Main_Research_Area_2"])
    res += ' ' + str(row["Main_Research_Area_3"])
    res += ' ' + str(row["Main_Topic"])
    #res += ' ' + str(row["language"]) language was not collected for mentees
    res += ' ' + str(row["MT-health"]).replace(';', ' ')
    #res += ' ' + str(row["MT-location-career"]).replace(';', ' ')
    res += ' ' + str(row["MT-career"]).replace(';', ' ')
    res += ' ' + str(row["Second_Topic"])
    #res += ' ' + str(row["ST-location-career"]).replace(';', ' ')
    res += ' ' + str(row["ST-career"]).replace(';', ' ')
    res += ' ' + str(row["ST-health"]).replace(';', ' ')
    return res

def build_abstract_mentee(row):
    """
        we build the abstract by concatenating the different area to match on
        the program uses tf-idf as a weighting solution, so the fields that should bare more importance
        should be repeated the same way for the mentor and mentee abstracts
        """
    res = ''
    res += ' ' + str(row["Main_Research_Area_1"]).replace(',', ' ')
    res += ' ' + str(row["Main_Research_Area_2"])
    res += ' ' + str(row["Main_Research_Area_3"])
    res += ' ' + str(row["Main_Topic"])
    res += ' ' + str(row["MT-health"]).replace(';', ' ')
    #res += ' ' + str(row["MT-location-career"]).replace(';', ' ')
    res += ' ' + str(row["MT-career"]).replace(';', ' ')
    res += ' ' + str(row["Second_Topic"])
    #res += ' ' + str(row["ST-location-career"]).replace(';', ' ')
    res += ' ' + str(row["ST-career"]).replace(';', ' ')
    res += ' ' + str(row["ST-health"]).replace(';', ' ')
    return res

def build_locations(row):
    res = ''
    res += ' ' + str(row["MT-location-career"]).replace(';', ' ')
    res += ' ' + str(row["ST-location-career"]).replace(';', ' ')
    return res

ADDITIONAL_TZ = {'Indian Standard time (IST)': 5,
                 'Indian Standard Time (IST)': 5,
                 'Mountain Daylight Time (MDT) - 6' : -6,
                 'GTM -3 Argentina': -3}

def tz_to_tdiff(x):
    if pd.isnull(x) or x == '': return pd.NA
    if x == 'Mountain Daylight Time (MDT) - 6' : return -6
    if x == "Coordinated Universal Time (UTC)":
        return 0
    else:
        try:
            diff = int(x[-2:])
            return diff
        except ValueError as e:
            if x in ADDITIONAL_TZ:
                return ADDITIONAL_TZ[x]
            else:
                raise ValueError(f"Unknown timezone : <{x}>")

def main(max_mentees, mentors_file, mentees_file, output_visual, output_list):
    mentors = pd.read_csv(mentors_file)
    mentors.fillna('',inplace=True)

    mentees = pd.read_csv(mentees_file)
    mentees.fillna('',inplace=True)

    #create the people dataframe which has PersonID and FullName
    people_df = mentees[["Name","PersonID"]]
    people_df.rename(columns={"Name":"FullName"},inplace=True)

    mentees = mentees.sort_values('Timestamp') #sort by date to keep last in case of duplicates
    mentors = mentors.sort_values('Timestamp')
    mentors = mentors.drop_duplicates('Username',keep='last')
    mentees = mentees.drop_duplicates('Username',keep='last')
    #sort back to IDs
    mentees = mentees.sort_values('PersonID')
    mentors = mentors.sort_values('PaperID')

    mentees['level'] = mentees['Status'].apply(lambda x: ACADEMIA_LEVELS[x])
    mentors['level'] = mentors['Status'].apply(lambda x: ACADEMIA_LEVELS[x])

    cross = pd.concat([mentors, mentees])
    cross['dup'] = cross.duplicated('Username')
    both = cross[cross['dup']]
    onlee = cross.drop_duplicates('Username', keep=False)


    #print(both.shape[0])

    PostDMenteeNotMentor = onlee[onlee['level'] >=4]
    PhdUnderMenteeNotMentor = onlee[onlee['level'] < 4]

    #print(PostDMenteeNotMentor.shape[0])
    #print(PhdUnderMenteeNotMentor.shape[0])

    #print(both.shape[0] + PostDMenteeNotMentor.shape[0] + PhdUnderMenteeNotMentor.shape[0])

    print('mentees : '+ str(mentees.shape[0]))
    print('mentors : '+ str(mentors.shape[0]))


    #prepare mentor df
    mentors['Title'] = ''
    mentors.rename(columns={
            "In order to match you with someone in a related subfield: What are your main research areas?  [Main Research Area 1]":"Main_Research_Area_1",
            "In order to match you with someone in a related subfield: What are your main research areas?  [Main Research Area 2]":"Main_Research_Area_2",
            "In order to match you with someone in a related subfield: What are your main research areas?  [Main Research Area 3]":"Main_Research_Area_3",
            "What main topic can you provide advice on? This will help us with the matching process (please note: for some topics you will be prompted for further details)":"Main_Topic",
            'If you can provide mentoring in a language different from English, please specify:': 'language',
            'Please specify what aspects of health you can discuss (check all that apply)': 'MT-health',
            "Please specify the country/location you can discuss (check all that apply)": "MT-location-career",
            'Please specify the career advancement topics you can discuss (check all that apply)': 'MT-career',
            'Please indicate the region/country for which you can provide careers advice ':'MT-career-location-empty',
            'Are there any other topics you can advise on as part of the mentor program?': 'Second_Topic',
            'Please specify the country/location you can discuss (check all that apply).1': 'ST-location-career',
            'Please specify the career advancement topics you\'re in a position to discuss (check all that apply)': 'ST-career',
            'Please indicate the region/country for which you can provide careers advice (click all that apply)': 'ST-career-location-empty',
            'Please specify what aspects of health you can discuss (check all that apply).1': 'ST-health',
            'Will you be participating in the mentoring program virtually or onsite in Sydney?': 'onsite',
            'If attending virtually, what time zone are you located in?': 'timezone',
            'Any other relevant information or questions you\'d like to pass along to the organizers?': 'comments',
            },inplace=True)

    #build the abstract for the mentors (add wanted fields)
    mentors["Abstract"] = mentors.apply(build_abstract_mentor , axis=1)
    mentors['locations'] = mentors.apply(build_locations , axis=1)

    #replace Nan values by empty string, add to the list every mentee that is higher up in level (or same) than the mentor
    mentors['PersonIDList'] = mentors.apply(add_higher_level_mentees,axis=1,mentees= mentees)


    #empty  PersonIDList is raises an error, putting a false PersonID as a placeholder
    mentors['PersonIDList'] = mentors.apply(lambda row: '99999' if row['PersonIDList'] == '' else row['PersonIDList'],axis=1)
    #print(mentors["PersonIDList"])

    mentors_mat = mentors[["PaperID","Title","PersonIDList", "Abstract"]]
    #mentors_MRA1["Title"] = mentors_MRA1['Abstract']

    #prepare mentees df
    mentees.rename(columns={
            "In order to match you with someone in a related subfield: What are your main research areas?  [Main Research Area 1]":"Main_Research_Area_1",
            "In order to match you with someone in a related subfield: What are your main research areas?  [Main Research Area 2]":"Main_Research_Area_2",
            "In order to match you with someone in a related subfield: What are your main research areas?  [Main Research Area 3]":"Main_Research_Area_3",
            'What is the main topic you would you like to discuss with your mentor? This will help us with the matching process (please note: for some topics you will be prompted for further details)': 'Main_Topic',
            'Please specify what aspects of health you wish to discuss (check all that apply)': 'MT-health',
            'Please specify the country/location you wish to discuss (check all that apply)': 'MT-location-career',
            'Please specify the career advancement topics you\'d like to discuss (check all that apply)' : 'MT-career',
            'Please indicate the region/country for which you are currently seeking careers advice ' : 'MT-career-location-empty',
            'Are there any other topics you\'d like to discuss as part of the mentor program?' : 'Second_Topic',
            'Please specify the country/location you wish to discuss (check all that apply).1' : 'ST-location-career',
            'Please specify the career advancement topics you\'d like to discuss (check all that apply).1': 'ST-career',
            'Please indicate the region/country for which you are currently seeking careers advice (click all that apply)': 'ST-career-location-empty',
            'Please specify what aspects of health you wish to discuss (check all that apply).1': 'ST-health',
            'Will you be participating in the mentoring program virtually or onsite in Sydney?': 'onsite' ,
            'If attending virtually, what time zone are you located in?': 'timezone',
            'Any other relevant information or questions you\'d like to pass along to the organizers?': 'comments',
            },inplace=True)

    mentees['timediff'] = mentees['timezone'].apply(tz_to_tdiff)
    mentors['timediff'] = mentors['timezone'].apply(tz_to_tdiff)

    # add to the list every mentee that has more than 5 hours of difference in timezone
    mentors['PersonIDList'] = mentors.apply(add_mentees_in_far_timezone,axis=1,mentees= mentees)

    mentees["Abstract"] = mentees.apply(build_abstract_mentee , axis=1)
    mentees['locations'] = mentees.apply(build_locations , axis=1)

    mentees_mat = mentees[["PersonID", "Abstract"]]

    # # TEST FOR TOO MANY PEOPLE
    # # this is removing all the Undergrad MA students and lower level people
    # mentees = mentees[mentees['level'] > 2]

    # # TEST first comes forst serves
    # # this is removing the last mentees that signed up until their number does not go over
    # # the number of mentors x max_mentees (by mentor)
    mentees = mentees.sort_values(by = 'Timestamp').head(mentors.shape[0] * max_mentees)
    
    res = assign_articles_to_reviewers(mentors,mentees,people_df, max_mentees=max_mentees)
    #print(res)
    res.to_csv(output_list,index=False)
    #res[['PaperID','ReviewerIDList']].to_csv("testIDs_locW.csv",index=False)

    compare = pd.DataFrame()
    for i, row in res.iterrows():
        ids = row['ReviewerIDList'].split(';')
        scores = row['scores'].split(';')
        n=0
        for idp in ids:
            mentees.loc[mentees['PersonID'].astype(str) == idp,'score'] = scores[n]
            n += 1
        compare = pd.concat([compare,mentors[mentors['PaperID']==row['PaperID']],mentees[mentees['PersonID'].astype(str).isin(row['ReviewerIDList'].split(';'))],pd.DataFrame([{'PaperID':'-'}])],ignore_index=True)

    #print(compare)
    # print(compare.columns)
    compare = compare[['PaperID','PersonID','score','Username', 'Name', 'Institution','Status','level','Main_Research_Area_1','Main_Research_Area_2','Main_Research_Area_3','Main_Topic','MT-health','MT-career','MT-location-career','Second_Topic','ST-career', 'ST-location-career','ST-health','onsite','timezone']]
    #print(compare)
    #compare.to_csv('test_compare.csv',index=False)
    compare.to_csv(output_visual,index=False)

if __name__ == '__main__':
    file_path = Path(__file__).parent
    mentors_file = file_path / Path("../preprocessed_data/Mentors_preview.csv")
    mentees_file = file_path / Path("../preprocessed_data/Mentees_preview.csv")

    output_visual = file_path / Path("../output/preliminary_matching_preview5.csv")
    output_list = file_path / Path("../output/match_list.csv")
    main(3,mentors_file,mentees_file, output_visual, output_list)
