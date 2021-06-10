#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_dataset_stats(labels_filename):
    '''
    This function uses the preprocessed labels.csv file to extract
    statistics in the data. 
    :input: labels_filename : full path to labels.csv
    :output: label_per_bs   : number of class labels per item in dataset
    :output: xvals          : Class labels
    :output: yvals          : Number of entries per class label
    '''
    df = pd.read_csv(labels_filename)
    
    nsnr = 0
    naf = 0
    niavb = 0
    nlbbb = 0
    nrbbb = 0
    npac = 0
    npvc = 0
    nstd = 0
    nste = 0
    
    for i in range(len(df.index)):
        if (df.iloc[i]['SNR'] == 1):
            nsnr = nsnr + 1
        if (df.iloc[i]['AF'] == 1):
            naf = naf + 1
        if (df.iloc[i]['IAVB'] == 1):
            niavb = niavb + 1
        if (df.iloc[i]['LBBB'] == 1):
            nlbbb = nlbbb + 1
        if (df.iloc[i]['RBBB'] == 1):
            nrbbb = nrbbb + 1
        if (df.iloc[i]['PAC'] == 1):
            npac = npac + 1
        if (df.iloc[i]['PVC'] == 1):
            npvc = npvc + 1
        if (df.iloc[i]['STD'] == 1):
            nstd = nstd + 1
        if (df.iloc[i]['STE'] == 1):
            nste = nste + 1
            
    col_list = list(df)
    col_list.remove('fold')
    col_list.remove('patient_id')
    df['sum'] = df[col_list].sum(axis=1)
    label_per_obs = np.asarray(df['sum']);

    dictvals = {'SNR':nsnr, 'AF':naf, 'IAVB':niavb, 'LBBB':nlbbb, 'RBBB':nrbbb, 'PAC':npac, 'PVC':npvc, 'STD':nstd, 'STE':nste }
    xvals = list(dictvals.keys())
    yvals = list(dictvals.values())

    return label_per_obs, xvals, yvals


filename_list = ["dataset/CPSC/labels.csv","dataset/WFDB_PTBXL/labels.csv"];
label_per_obs_cpsc, xvals_cpsc, yvals_cpsc = get_dataset_stats(filename_list[0])
label_per_obs_ptb, xvals_ptb, yvals_ptb = get_dataset_stats(filename_list[1])


plt.bar(xvals_ptb, yvals_ptb, color=(0.2, 0.5, 0.8, 0.9))
plt.bar(xvals_cpsc, yvals_cpsc, color=(0.9, 0.4, 0.2, 0.8))
plt.ylim(0 ,3000)
plt.text(0.5, 2800,"^ 18092",color=(0.2, 0.5, 0.9, 1),fontsize=12)
plt.legend(["PTB-XL","CPSC"],fontsize=16)
plt.xlabel("Diagnostic Classes",fontsize=16)
plt.ylabel("# of labels",fontsize=16)

plt.savefig(f'results/dataset_label_occurrence.png')

print("Number of labels per data point:")
print("mean", "std", "max")
print(np.mean(label_per_obs_cpsc),np.std(label_per_obs_cpsc),np.max(label_per_obs_cpsc))
print(np.mean(label_per_obs_ptb),np.std(label_per_obs_ptb),np.max(label_per_obs_ptb))

