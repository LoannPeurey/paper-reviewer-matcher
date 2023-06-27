from glob import glob
import numpy as np
import pandas as pd
import scipy.sparse as sp
from paper_reviewer_matcher import (
    preprocess, compute_affinity,
    create_lp_matrix, linprog,
    create_assignment
)


def assign_articles_to_reviewers(article_df, reviewer_df, people_df, max_mentees):
    """
    Perform reviewer-assignment from dataframe of article, reviewer, and people

    Parameters
    ==========
    article_df: a dataframe that has columns `PaperID`, `Title`, `Abstract`, and `PersonIDList`
        where PersonIDList contains string of simicolon separated list of PersonID
    reviewer_df: a dataframe that has columns `PersonID` and `Abstract`
    people_df:  dataframe that has columns `PersonID`, `FullName`
    max_mentees: int , maximum number of mentees for a single mentor

    We assume `PersonID` is an integer

    Output
    ======
    article_assignment_df: an assigned reviewers dataframe, each row of article will have 
        list of reviewers in `ReviewerIDList` column and their name in reviewer_names
    """
    papers = list((article_df['Title'] + ' ' + article_df['Abstract']).map(preprocess))
    reviewers = list(reviewer_df['Abstract'].map(preprocess))
    
    
    papers_loc = list((article_df['locations']).map(preprocess))
    reviewers_loc = list(reviewer_df['locations'].map(preprocess))
    weight_loc = 0.5

    # Calculate conflict of interest based on co-authors
    coauthors_df = pd.DataFrame([[int(r.PaperID), int(co_author)]
                                for _, r in article_df.iterrows()
                                for co_author in r.PersonIDList.split(';')],
                                columns = ['PaperID', 'PersonID'])
    article_df['paper_id'] = list(range(len(article_df)))
    reviewer_df['person_id'] = list(range(len(reviewer_df)))
    coi_df = coauthors_df.merge(article_df[['PaperID', 'paper_id']], 
                                on='PaperID').merge(reviewer_df[['PersonID', 'person_id']], 
                                on='PersonID')[['paper_id', 'person_id']]
        
    # calculate affinity matrix
    A = compute_affinity(
        papers, reviewers,
        n_components=3, min_df=2, max_df=0.8,
        weighting='tfidf', projection='pca'
    )
    # print('======= Abstract matching ===========')
    # print(A)
    # print('-------shape------')
    # print(A.shape)
    # print('=====================================')
    
    # calculate affinity matrix for locations
    B = compute_affinity(
        papers_loc, reviewers_loc,
        n_components=2, min_df=2, max_df=0.8,
        weighting='tfidf', projection='pca'
    )
    # print('======= locations matching ===========')
    # print(B)
    # print('-------shape------')
    # print(B.shape)
    # print('=====================================')

    papers_onsite = list((article_df['onsite']).map(preprocess))
    reviewers_onsite = list(reviewer_df['onsite'].map(preprocess))
    # calculate affinity matrix for onsite or not onsite
    C = compute_affinity(
        papers_onsite, reviewers_onsite,
        n_components=2, min_df=2, max_df=0.8,
        weighting='tfidf', projection='pca'
    )
    weight_onsite = 0.5
    
    A = A + (weight_loc * B) + (weight_onsite * C)
    
    # trim distance that are too high
    A_trim = []
    for r in range(len(A)):
        a = A[r, :]
        #a[np.argsort(a)[0:2]] = 0 #too violent, results in too many 0s
        A_trim.append(a)
    A_trim = np.vstack(A_trim)

    # assign conflict of interest to have high negative cost
    for i, j in zip(coi_df.paper_id.tolist(), coi_df.person_id.tolist()):
        A_trim[i, j] = -1000

    # print(A_trim)
    # min and max (we want a max of 3 reviewers(mentees) per paper(mentor) and exactly 1 mentor per mentee)
    v, K, d = create_lp_matrix(A_trim, 
                               min_reviewers_per_paper=2, max_reviewers_per_paper=max_mentees,
                               min_papers_per_reviewer=1, max_papers_per_reviewer=1)
    x_sol = linprog(v, K, d)['x']
    b = create_assignment(x_sol, A_trim)
    reviewer_ids = list(reviewer_df.PersonID)

    reviewer_name_dict = {r['PersonID']: r['FullName'] for _, r in people_df.iterrows()} # map reviewer id to reviewer name
    assignments = []
    for i in range(len(b)):
        assignments.append([i, 
                            [reviewer_ids[b_] for b_ in np.nonzero(b[i])[0]], 
                            [reviewer_name_dict[reviewer_ids[b_]] for b_ in np.nonzero(b[i])[0]],
                            [A_trim[i][b_] for b_ in np.nonzero(b[i])[0]],
                            ])
#    for i in range(len(b)):
#        assignments.append([article_df[article_df['paper_id'] == i].iloc[0]['PaperID'], 
#                            [reviewer_df[reviewer_df['person_id'] == b_].iloc[0]['PersonID']] for b_ in np.nonzero(b[i])[0]], 
#                            [reviewer_name_dict[reviewer_df[reviewer_df['person_id'] == b_].iloc[0]['PersonID']]] for b_ in np.nonzero(b[i])[0]],
#                            [A_trim[i][b_] for b_ in np.nonzero(b[i])[0]],
#                            ])
    assignments_df = pd.DataFrame(assignments, columns=['paper_id', 'ReviewerIDList', 'reviewer_names', 'scores'])
    assignments_df['ReviewerIDList'] = assignments_df.ReviewerIDList.map(lambda e: ';'.join(str(e_) for e_ in e))
    assignments_df['reviewer_names'] = assignments_df.reviewer_names.map(lambda x: ';'.join(x))
    assignments_df['scores'] = assignments_df.scores.map(lambda x: ';'.join(str(x_) for x_ in x))
    article_assignment_df = article_df.merge(assignments_df, on='paper_id').drop('paper_id', axis=1)
    return article_assignment_df


if __name__ == '__main__':
    CCN_PATH = '/path/to/*.csv'
    article_path, reviewer_path, people_path = [path for path in glob(CCN_PATH) 
                                                if 'CCN' in path and 'fixed' not in path]
    # there is a problem when encoding lines in the given CSV so we have to use ISO-8859-1 instead
    article_df = pd.read_csv(article_path) # has columns `PaperID`, `Title`, `Abstract`, `PersonIDList`
    reviewer_df = pd.read_csv(reviewer_path, encoding="ISO-8859-1") # has columns `PersonID`, `Abstract`
    people_df = pd.read_csv(people_path, encoding="ISO-8859-1") # has columns `PersonID`, `FullName`
    article_assignment_df = assign_articles_to_reviewers(article_df, reviewer_df, people_df)
    article_assignment_df.to_csv('article_assignment.csv', index=False)