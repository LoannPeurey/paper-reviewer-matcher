"""
Code snippet for producing CCN Mind Matching session 2018. 
We create affinity matrix of people-people using topic modeling 
then solve linear programming problem and apply networkx to solve the schedule problem
"""

import numpy as np
import pandas as pd
from paper_reviewer_matcher import (
    preprocess, compute_affinity,
    create_lp_matrix, linprog,
    create_assignment
)
import random
import networkx as nx
from itertools import chain
from collections import Counter


def build_line_graph(people):
    """
    Edge coloring and Vizing's theorem solution 
    can be found from Stack Overflow question below

    ref: https://stackoverflow.com/questions/51758406/creating-time-schedule-from-list-of-people-and-who-they-have-to-meet
    """
    G = nx.Graph()
    G.add_edges_from(((p, q) for p, L in people for q in L))
    return nx.line_graph(G)


def color_graph(G):
    return nx.greedy_color(G)


def format_answer(coloring):
    res = {}
    N = max(coloring.values()) + 1
    for meeting in coloring:
        time_slot = coloring[meeting]
        for meeting_member in (0, 1):
            if meeting[meeting_member] not in res:
                res[meeting[meeting_member]] = [None] * N
            res[meeting[meeting_member]][time_slot] = meeting[1-meeting_member]
    return res


def nest_answer(people, formatted):
    return [[p, formatted[p]] for p, v in people]


def schedule_to_timeslot(schedule, n_timeslot=15):
    """
    Create personal schedule from list of schedule
    """
    schedule_df = pd.DataFrame(schedule, columns=['person', 'person_to_meet'])
    person_to_meet_df = pd.DataFrame(schedule_df.person_to_meet.values.tolist(), 
                                    columns=range(1, n_timeslot))
    # schedule to dataframe
    schedule_df = pd.concat((schedule_df[['person']], person_to_meet_df), axis=1)

    # create person list and map to row/ column
    person_list = pd.unique(list(schedule_df['person']))
    P_map = {v: k for k, v in enumerate(person_list)}


    timeslot_list = []
    for i in range(1, n_timeslot):
        timeslot_df = schedule_df[['person', i]].dropna().astype(int).reset_index(drop=True)
        P = np.zeros((len(person_list), len(person_list)), dtype=int)
        
        # adding table number
        count = 1
        for _, r in schedule_df.iterrows():
            if not pd.isnull(r['person']) and not pd.isnull(r[i]) and P[P_map[r['person']], P_map[r[i]]] == 0 and P[P_map[r[i]], P_map[r['person']]] == 0:
                P[P_map[r['person']], P_map[r[i]]] = count
                P[P_map[r[i]], P_map[r['person']]] = count
                count += 1
    
        # fill in pair of people (add random pair of people)
        left_person = list(set(person_list) - set(pd.unique(list(timeslot_df.person) + list(timeslot_df[i].dropna().astype(int)))))
        random.shuffle(left_person)

        random_pair = list(zip(left_person[0:int(len(left_person)/2)], left_person[int(len(left_person)/2)::]))
        for p1, p2 in random_pair:
            count += 1
            P[P_map[p1], P_map[p2]] = count
            P[P_map[p2], P_map[p1]] = count
            
        additional_pair = \
            [[p1, p2, int(P[P_map[p1], P_map[p2]])] for p1, p2 in random_pair] + \
            [[p2, p1, int(P[P_map[p1], P_map[p2]])] for p1, p2 in random_pair]
        left_person_df = pd.DataFrame(additional_pair, columns=['person', i, 'table_number'])
        
        # concatenate
        table_number = [int(P[P_map[r['person']], P_map[r[i]]]) for _, r in timeslot_df.iterrows()]
        timeslot_df['table_number'] = table_number
        timeslot_df = pd.concat((timeslot_df, left_person_df))
        timeslot_list.append(timeslot_df)

    # for all person, make schedule
    person_schedule_all = []
    for p in person_list:
        person_schedule = []
        for t_df in timeslot_list:
            person_schedule.append(t_df[t_df.person == p])
        person_schedule_all.append(pd.concat(person_schedule))
    
    return person_schedule_all # list of dataframe each contains schedule


def create_dating_schedule(person_df, n_meeting=10):
    """
    Function to create speed dating schedule at CCN 2018 conference

    Parameters
    ==========
    person_df: pandas dataframe contains - PersonID, FullName, Abstract
    n_meeting: int, number of meeting we would like to have

    Output
    ======
    schedule: list, list of person id and person ids to meet in the 
        following format: [PersonID, [PersonID to meet]]
    """
    # linear programming
    persons_1 = list(map(preprocess, list(person_df['Abstract'])))
    persons_2 = list(map(preprocess, list(person_df['Abstract'])))

    A = compute_affinity(
        persons_1, persons_2,
        n_components=10, min_df=1, max_df=0.8,
        weighting='tfidf', projection='pca'
    )
    # constraints, conflict of interest
    A[np.arange(len(A)), np.arange(len(A))] = -1000

    # for dating at CCN
    v, K, d = create_lp_matrix(
        A, 
        min_reviewers_per_paper=n_meeting, max_reviewers_per_paper=n_meeting,
        min_papers_per_reviewer=n_meeting, max_papers_per_reviewer=n_meeting
    )
    x_sol = linprog(v, K, d)['x']
    b = create_assignment(x_sol, A)

    output = []
    for i in range(len(b)):
        r = [list(person_df['PersonID'])[b_] for b_ in np.nonzero(b[i])[0]]
        output.append([list(person_df.PersonID)[i], r])

    # make optimal schedule
    schedule = nest_answer(output, format_answer(color_graph(build_line_graph(output))))

    return schedule


def partition_cluster(D):
    """
    Given a distance matrix, performing hierarchical clustering to rank it
    """
    import fastcluster
    import scipy.cluster.hierarchy as hierarchy
    linkage = fastcluster.linkage(D,
                                  method='centroid',
                                  preserve_input=True)
    partition = hierarchy.fcluster(linkage,
                                   t=0.5,
                                   criterion='distance') # distance
    return partition


def convert_names_to_ids(names, person_id_map, threshold=85):
    """
    Convert string of names with separated comma to list of IDs using fuzzy string match

    Parameters
    ==========
    names: str, string in the following format 'FirstName1 LastName1, ...'
    person_id_map: dict, dictionary mapping id to name

    Example
    =======
    >> convert_names_to_ids('Jone Doe, Sarah Doe', 
                            {1: 'Jone Doe', 2: 'Sarah Deo'}, threshold=85) # output [1, 2]
    """
    from fuzzywuzzy import fuzz

    matched_ids = []
    names = [name.strip() for name in names.split(',')]
    for name in names:
        matched_ids.extend([idx for (idx, n) in person_id_map.items() if fuzz.ratio(n, name) >= threshold])
    return pd.unique(matched_ids)


if __name__ == '__main__':
    """
    Example script to create dating schedule for CCN 2018 conference
    """
    person_df = pd.ExcelFile('CCN18_MindMatchData.xlsx').parse('Grid Results')
    person_df['FullName'] = person_df['NameFirst'] + ' ' + person_df['NameLast']
    person_df['PersonID'] = np.arange(len(person_df))
    person_id_map = {r['PersonID']: r['FullName'] for _, r in person_df.iterrows()}
    person_affil_map = {r['PersonID']: r['Affiliation'] for _, r in person_df.iterrows()}

    schedule = create_dating_schedule(person_df)
    n_timeslot = len(schedule[0][-1]) + 1
    person_schedule_all = schedule_to_timeslot(schedule, n_timeslot=n_timeslot)

    # print out
    n_meeting = 6
    output_text = []
    for person_schedule_df in person_schedule_all:
        output_text.extend(['You are: ', str(person_id_map[person_schedule_df.person.unique()[0]])])
        output_text.extend(['--------------------'])
        output_text.extend(['Dating schedule'])
        output_text.extend(['--------------------'])
        r = 0
        for i in range(1, n_meeting + 1):
            person_to_meet = [l for l in list(person_schedule_df[i]) if not pd.isnull(l)]
            if len(person_to_meet) > 0:
                table_number = person_schedule_df['table_number'].iloc[r]
                output_text.extend(['timeslot: %d, table number: %d, date: %s' % 
                                    (i, table_number, person_id_map[person_to_meet[0]])])
                r += 1
            else:
                output_text.extend(['timeslot: %d, Waiting area!' % i])
        output_text.extend([''])
    
    # save to text file
    with open('output_date_schedule.txt', 'w') as f:
        for l in output_text:
            f.write("{}\n".format(l))