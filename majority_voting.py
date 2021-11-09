import argparse
import pandas as pd
import csv
import os
import numpy as np

def parse_arguments():
    '''
    DESCRIPTION: Parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='process user given parameters')    
    parser.add_argument('-d1', '--data_path_1', required = False, dest = 'data_path_1',
                        default = './REoutput/drugprot_electra_bertlarge/1',
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-d2', '--data_path_2', required = False, dest = 'data_path_2',
                        default = './REoutput/drugprot_electra_bertlarge/2',
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-d3', '--data_path_3', required = False, dest = 'data_path_3',
                        default = './REoutput/drugprot_electra_bertlarge/3',
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-d4', '--data_path_4', required = False, dest = 'data_path_4',
                        default = './REoutput/drugprot_electra_bertlarge/4',
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-d5', '--data_path_5', required = False, dest = 'data_path_5',
                        default = './REoutput/drugprot_electra_bertlarge/5',
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-o', '--out_path', required = False, dest = 'out_path',
                        default = './REoutput/majority_run4')
    
    return parser.parse_args()

def decide_major_vote(pr1, pr2, pr3, pr4, pr5, num_relations):

    models = [pr1, pr2, pr3, pr4, pr5]

    vote1 = pr1.astype(np.float64).idxmax()
    vote2 = pr2.astype(np.float64).idxmax()
    vote3 = pr3.astype(np.float64).idxmax()
    vote4 = pr4.astype(np.float64).idxmax()
    vote5 = pr5.astype(np.float64).idxmax()

    n = 5
    arr = [vote1, vote2, vote3, vote4, vote5]
    vote_to_voter = {vote:i for i, vote in enumerate(arr)}

    maxCount = 0
    index = -1  # sentinels
    for i in range(n):
 
        count = 0
        for j in range(n):
 
            if(arr[i] == arr[j]):
                count += 1
 
        # update maxCount if count of
        # current element is greater
        if(count > maxCount):
 
            maxCount = count
            index = i
 
    # if maxCount is greater than n/2
    # return the corresponding element
    if (maxCount > n//2):
        vote =  (arr[index])
        #print(vote)
 
    else:
        #print("No Majority Element")
        vote = num_relations - 1
        #vote = (arr[index])

    if vote in vote_to_voter:
        model = models[vote_to_voter[vote]]

    else:
        model = np.zeros(num_relations)
        model[-1] = 1
        
    return model

def main(args):

    pred_file1 = os.path.join(args.data_path_1, 'test_results.tsv')
    pred_file2 = os.path.join(args.data_path_2, 'test_results.tsv')
    pred_file3 = os.path.join(args.data_path_3, 'test_results.tsv')
    pred_file4 = os.path.join(args.data_path_4, 'test_results.tsv')
    pred_file5 = os.path.join(args.data_path_5, 'test_results.tsv')

    pred_majority = os.path.join(args.out_path, 'test_results.tsv')

    relations = ["ACTIVATOR",
                "AGONIST",
                "AGONIST-ACTIVATOR",
                "AGONIST-INHIBITOR",
                "ANTAGONIST",
                "DIRECT-REGULATOR",
                "INDIRECT-DOWNREGULATOR",
                "INDIRECT-UPREGULATOR",
                "INHIBITOR",
                "PART-OF",
                "PRODUCT-OF",
                "SUBSTRATE",
                "SUBSTRATE_PRODUCT-OF",
                "False"]


    pred1 = pd.read_csv(pred_file1, sep='\t', header=None, dtype=str, skip_blank_lines=True,
         encoding = 'utf-8')

    pred2 = pd.read_csv(pred_file2, sep='\t', header=None, dtype=str, skip_blank_lines=True, encoding = 'utf-8')

    pred3= pd.read_csv(pred_file3, sep='\t', header=None, dtype=str, skip_blank_lines=True, encoding = 'utf-8')

    pred4 = pd.read_csv(pred_file4, sep='\t', header=None, dtype=str, skip_blank_lines=True, encoding = 'utf-8')

    pred5 = pd.read_csv(pred_file5, sep='\t', header=None, dtype=str, skip_blank_lines=True, encoding = 'utf-8')

    idx_to_rel = {i:r for i, r in enumerate(relations)}

    bp = open(pred_majority, 'w', encoding='utf8')
    writer = csv.writer(bp, delimiter='\t', lineterminator='\n')

    a = 0
    for i in range(len(pred1)):

        pr1 = pred1.iloc[i][:]
        pr2 = pred2.iloc[i][:]
        pr3 = pred3.iloc[i][:]
        pr4 = pred4.iloc[i][:]
        pr5 = pred5.iloc[i][:]
        
        major_vote = decide_major_vote(pr1, pr2, pr3, pr4, pr5, len(relations))
        writer.writerow(major_vote) 
        #best_pred_idx = pred.iloc[i][:].astype(np.float64).idxmax()
        #rel = idx_to_rel[major_vote]
        #writer.writerow([pmid, rel, arg1, arg2])

    bp.close()

if __name__ == '__main__':
    args = parse_arguments()

    main(args)
