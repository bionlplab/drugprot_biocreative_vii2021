import tensorflow as tf 
import numpy as np
import argparse
import os
from pprint import pprint
import tqdm
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import IterableDataset
from torch.nn import functional as F
import csv
from itertools import starmap

def parse_arguments():
    '''
    DESCRIPTION: Parse command line arguments
    '''

    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument('-d1', '--data_path_1', required = False, dest = 'data_path_1',
                        default = './REoutput/drugprot_pubmed/0',
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-d2', '--data_path_2', required = False, dest = 'data_path_2',
                        default = './REoutput/drugprot_pubmed_weighted_loss_scaled_26/0',
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-d3', '--data_path_3', required = False, dest = 'data_path_3',
                        default = './REoutput/drugprot_bio_attention_last_layer/0',
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-d4', '--data_path_4', required = False, dest = 'data_path_4',  
                        default = './REoutput/drugprot_bio_tag2/0',
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-d5', '--data_path_5', required = False, dest = 'data_path_5',  
                        default = './REoutput/drugprot_pubmed_lstm_last_layer/0',        
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-g', '--gt_path', required = False, dest = 'gt_path',
                        default = './KFdata/drugprot/0',
                        help = 'path to BERT dev file (TSV)')

    parser.add_argument('-o', '--out_path', required = False, dest = 'out_path',
			default = './REoutput/ensemble_CLS_D_M3/0')

    parser.add_argument('--train', action='store_true', help='train ensemble model')
    parser.add_argument('--eval', action='store_true', help='evaluate ensemble model') 

    return parser.parse_args()

class EnsembleIterableDataset(IterableDataset):

    def __init__(self, file1, file2, file3, file4, file5, file_gt):
        self.file1 = file1
        self.file2 = file2
        self.file3 = file3
        self.file4 = file4
        self.file5 = file5
        self.file_gt = file_gt
        
        self.relations = ["ACTIVATOR", "AGONIST", "AGONIST-ACTIVATOR", "AGONIST-INHIBITOR", "ANTAGONIST", "DIRECT-REGULATOR", "INDIRECT-DOWNREGULATOR", "INDIRECT-UPREGULATOR", "INHIBITOR", "PART-OF", "PRODUCT-OF", "SUBSTRATE", "SUBSTRATE_PRODUCT-OF", "False"]

        self.rel_to_idx = {r:i for i, r in enumerate(self.relations)}

    def line_mapper(self, line1, line2, line3, line4, line5):
        line1 = line1.strip('\n').split('\t')
        line1 = np.array(line1, dtype=np.float32)
        line2 = line2.strip('\n').split('\t')
        line2 = np.array(line2, dtype=np.float32)
        line3 = line3.strip('\n').split('\t')
        line3 = np.array(line3, dtype=np.float32)
        line4 = line4.strip('\n').split('\t')
        line4 = np.array(line4, dtype=np.float32)
        line5 = line5.strip('\n').split('\t')
        line5 = np.array(line5, dtype=np.float32)
        
        line = np.hstack((line1, line2, line3, line4, line5))

        line = torch.tensor(line, dtype=torch.float32)
        return line

    def label_mapper(self, line):
        label = line.strip('\n').split('\t')[2]
        label = self.rel_to_idx[label]
        label = torch.tensor(label, dtype=torch.long)
        
        return label

    def __iter__(self):
        file1_itr = open(self.file1)
        file2_itr = open(self.file2)
        file3_itr = open(self.file3)
        file4_itr = open(self.file4)
        file5_itr = open(self.file5)

        filegt_itr = open(self.file_gt)

        mapped_itr = starmap(self.line_mapper, zip(file1_itr, file2_itr, file3_itr, file4_itr, file5_itr))
        label_itr = map(self.label_mapper, filegt_itr)
        
        return zip(mapped_itr, label_itr)


class MyEnsemble(nn.Module):
    def __init__(self, input_dim,  hidden_dim, output_dim):
        super(MyEnsemble, self).__init__()

        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        #self.tanh = nn.Tanh()

        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        
        out = self.fc1(x)
        out = self.relu(out)
        #out = self.tanh(out)
        out = self.fc2(out)

        return out

def evaluation(model, model_path, test_loader, device):
    preds = os.path.join(args.out_path, 'test_results.tsv')
    model.load_state_dict(torch.load(model_path))
    model.eval()

    pred_list = []
    for (features, labels) in tqdm.tqdm(test_loader):

        features = features.to(device)
        labels = labels.to(device)
        
        outputs = model(features)
        pred_probab = nn.Softmax(dim=1)(outputs)
        probs = pred_probab.data.cpu().tolist()
        pred_list.extend(probs)

    fp = open(preds, 'w', encoding='utf8')
    writer = csv.writer(fp, delimiter='\t', lineterminator='\n')
    for p in pred_list:
        writer.writerow(p)

def main(args):

    train_data_1 = os.path.join(args.data_path_1, 'test_feature.tsv')
    train_data_2 = os.path.join(args.data_path_2, 'test_feature.tsv')
    train_data_3 = os.path.join(args.data_path_3, 'test_feature.tsv')
    train_data_4 = os.path.join(args.data_path_4, 'test_feature.tsv')
    train_data_5 = os.path.join(args.data_path_5, 'test_feature.tsv')
    train_gt = os.path.join(args.gt_path, 'train.tsv')

    test_data_1 = os.path.join(args.data_path_1, 'test_feature.tsv')
    test_data_2 = os.path.join(args.data_path_2, 'test_feature.tsv')
    test_data_3 = os.path.join(args.data_path_3, 'test_feature.tsv')
    test_data_4 = os.path.join(args.data_path_4, 'test_feature.tsv')
    test_data_5 = os.path.join(args.data_path_5, 'test_feature.tsv')
    test_gt = os.path.join(args.gt_path, 'test.tsv')

    model_path = os.path.join(args.out_path, 'ensemble_cpkt.pth')

    train_features = EnsembleIterableDataset(train_data_1, train_data_2, train_data_3, train_data_4, train_data_5, train_gt)
    test_features = EnsembleIterableDataset(test_data_1, test_data_2, test_data_3, test_data_4, test_data_5, test_gt)

    batch_train_size = 32
    batch_test_size = 8
    num_epochs = 3

    input_dim = 3840
    output_dim = 14
    hidden_dim = 512

    train_loader = torch.utils.data.DataLoader(train_features, batch_size=batch_train_size, drop_last=True)
    test_loader = torch.utils.data.DataLoader(test_features, batch_size=batch_test_size, drop_last=False)


    model = MyEnsemble(input_dim, hidden_dim, output_dim)

    device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
    model.to(device)


    ####weights_cls_a
    weights = [7.55, 9.96, 7.5, 7.5, 8.17, 6.06, 7.5, 7.44, 4.5, 8.64, 8.76, 6.75, 7.5, 5]

    class_weights = torch.FloatTensor(weights).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    ###Insantiate loss class
    #criterion = nn.CrossEntropyLoss()

    ##Instantiate Optimizer class
    learning_rate = 2e-5

    #optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    iter = 0
    #m = nn.Dropout(p=0.5)
    ###Training
    if args.train:
        for epoch in range(num_epochs):
            running_loss = 0.0
            print('Training at Epoch: {}'.format(epoch))
            for (features, labels) in tqdm.tqdm(train_loader):
                features = features.requires_grad_(False).to(device)
                #features = m(features)
                labels = labels.to(device)
                
                optimizer.zero_grad()
                
                outputs = model(features)
                loss = criterion(outputs, labels)
                loss.backward()
                
                optimizer.step()
                
                running_loss += loss.item()
                if iter % 50 == 49:
                    print('[%d, %5d] loss: %.3f' %
                    (epoch + 1, iter + 1, running_loss / 50))
                    running_loss = 0.0
                    
                iter += 1
                if iter % 500 == 499:
                    correct = 0
                    total = 0
                    for (features, labels) in test_loader:
                        features = features.requires_grad_(False).to(device)
                        outputs = model(features)
                        
                        _, predicted = torch.max(outputs.data, 1)
                        
                        total += labels.size(0)
                        
                        if torch.cuda.is_available():
                            correct += (predicted.cpu() == labels.cpu()).sum()
                        else:
                            correct += (predicted == labels).sum()

                    accuracy = 100 * correct / total

                    print('Iteration: {}. Loss: {}. Accuracy: {}'.format(iter, loss.item(), accuracy))

        torch.save(model.state_dict(), model_path)

    if args.eval:
        evaluation(model, model_path, test_loader,device)

if __name__ == '__main__':
    args = parse_arguments()
    main(args)
