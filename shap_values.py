import argparse
import os

import numpy as np
import pandas as pd
import torch
import shap
from tqdm import tqdm
import matplotlib.pyplot as plt

from resnet import resnet34
from utils import prepare_input

import pdb


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=str, default='data/CPSC', help='Data directory')
    parser.add_argument('--leads', type=str, default='all')
    parser.add_argument('--seed', type=int, default=42, help='Seed to split data')
    parser.add_argument('--use-gpu', default=False, action='store_true', help='Use GPU')
    return parser.parse_args()


def plot_shap(ecg_data, sv_data, leads, top_leads, patient_id, label):
    # patient-level interpretation along with raw ECG data
    nleads = len(top_leads)
    if nleads == 0:
        return
    nsteps = 5000 # ecg_data.shape[1], visualize last 10 s since many patients' ECG are <=10 s
    x = range(nsteps)
    ecg_data = ecg_data[:, -nsteps:]
    sv_data = sv_data[:, -nsteps:]
    threshold = 0.001 # set threshold to highlight features with high shap values
    fig, axs = plt.subplots(nleads, figsize=(9, nleads))
    fig.suptitle(label)
#     pdb.set_trace()
    for i, lead in enumerate(top_leads):
        sv_upper = np.ma.masked_where(sv_data[lead] >= threshold, ecg_data[lead])
        sv_lower = np.ma.masked_where(sv_data[lead] < threshold, ecg_data[lead])
        sv_lowest = np.ma.masked_where(sv_data[lead] > -threshold, ecg_data[lead])
        if nleads == 1:
            axe = axs
        else:
            axe = axs[i]
        axe.plot(x, sv_upper, x, sv_lower, x, sv_lowest)
#         axe.plot(x, sv_upper);
        axe.set_xticks([])
        axe.set_yticks([])
        axe.set_ylabel(leads[lead])
    plt.savefig(f'shap/shap1-{patient_id}.png')
    plt.close(fig)


def summary_plot(svs, y_scores):
    leads = np.array(['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'])
    svs2 = []
    n = y_scores.shape[0]
    for i in tqdm(range(n)):
        label = np.argmax(y_scores[i])
        sv_data = svs[label, i]
        svs2.append(np.sum(sv_data, axis=1))
    svs2 = np.vstack(svs2)
    svs_data = np.mean(svs2, axis=0)
    plt.plot(leads, svs_data)
    plt.savefig('./shap/summary.png')
    plt.clf()


def plot_shap2(svs, y_scores, leads, cmap=plt.cm.Blues):
    # population-level interpretation
    n = y_scores.shape[0]
    results = [[], [], [], [], [], [], [], [], []]
    print(svs.shape)
    for i in tqdm(range(n)):
        label = np.argmax(y_scores[i])
        results[label].append(svs[label, i])
    ys = []
    for label in range(y_scores.shape[1]):
        result = np.array(results[label])
        y = []
        for i, _ in enumerate(leads):
            y.append(result[:,i].sum())
        y = np.array(y) / np.sum(y)
        ys.append(y)
        plt.plot(leads, y)
    ys.append(np.array(ys).mean(axis=0))
    ys = np.array(ys)
    fig, axs = plt.subplots()
    im = axs.imshow(ys, cmap=cmap)
    axs.figure.colorbar(im, ax=axs)
    fmt = '.2f'
    xlabels = leads
    ylabels = ['SNR', 'AF', 'IAVB', 'LBBB', 'RBBB', 'PAC', 'PVC', 'STD', 'STE'] + ['AVG']
    axs.set_xticks(np.arange(len(xlabels)))
    axs.set_yticks(np.arange(len(ylabels)))
    axs.set_xticklabels(xlabels)
    axs.set_yticklabels(ylabels)
    thresh = ys.max() / 2
    for i in range(ys.shape[0]):
        for j in range(ys.shape[1]):
            axs.text(j, i, format(ys[i, j], fmt),
                    ha='center', va='center',
                    color='white' if ys[i, j] > thresh else 'black')
    np.set_printoptions(precision=2)
    fig.tight_layout()
    plt.savefig('./shap/shap2.png')
    plt.clf()
    

if __name__ == '__main__':
    args = parse_args()
    data_dir = os.path.normpath(args.data_dir)
    database = os.path.basename(data_dir)
    args.model_path = f'models/resnet34_{database}_{args.leads}_{args.seed}.pth'
    label_csv = os.path.join(data_dir, 'labels.csv')
    reference_csv = os.path.join(data_dir, 'reference.csv')
    classes = np.array(['SNR', 'AF', 'IAVB', 'LBBB', 'RBBB', 'PAC', 'PVC', 'STD', 'STE'])
    leads_all = np.array(['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'])
    if args.use_gpu and torch.cuda.is_available():
        device = torch.device('cuda:0')
    else:
        device = 'cpu'
    if args.leads == 'all':
        leads = leads_all
        use_leads = np.where(np.in1d(leads_all, leads_all))[0]
        nleads = 12
    else:
        leads = args.leads.split(',')
        use_leads = np.where(np.in1d(leads_all, leads))[0]
        nleads = len(leads)
    
    model = resnet34(input_channels=nleads).to(device)
    model.load_state_dict(torch.load(args.model_path, map_location=device))
    model.eval()

    background = 100
    result_path = f'results/A{background * 2}_{args.leads}_{args.seed}.npy'
    

    df_labels = pd.read_csv(label_csv)
    df_reference = pd.read_csv(os.path.join(args.data_dir, 'reference.csv'))
    df = pd.merge(df_labels, df_reference[['patient_id', 'age', 'sex', 'signal_len']], on='patient_id', how='left')

    # df = df[df['signal_len'] >= 15000]

    patient_ids = df['patient_id'].to_numpy()
    to_explain = patient_ids[:background * 2]

    background_patient_ids = df.head(background)['patient_id'].to_numpy()
   
    background_inputs = [os.path.join(data_dir, patient_id) for patient_id in background_patient_ids]
    background_inputs = torch.stack([torch.from_numpy(prepare_input(input)).float() for input in background_inputs]).to(device)
    background_inputs = background_inputs[:,use_leads,:];
    
    e = shap.GradientExplainer(model, background_inputs)

    if not os.path.exists(result_path):
        svs = []
        y_scores = []
        for patient_id in tqdm(to_explain):
            input = os.path.join(data_dir, patient_id)
            inputs = torch.stack([torch.from_numpy(prepare_input(input)).float()]).to(device)
            inputs = inputs[:,use_leads,:]
            y_scores.append(torch.sigmoid(model(inputs)).detach().cpu().numpy())
            sv = np.array(e.shap_values(inputs)) # (n_classes, n_samples, n_leads, n_points)
            svs.append(sv)
        svs = np.concatenate(svs, axis=1)
        y_scores = np.concatenate(y_scores, axis=0)
        np.save(result_path, (svs, y_scores))
    svs, y_scores = np.load(result_path, allow_pickle=True)

    # summary_plot(svs, y_scores)
#     plot_shap2(svs, y_scores, leads)

    preds = []
    top_leads_list = []
    for i, patient_id in enumerate(to_explain):
        ecg_data = prepare_input(os.path.join(data_dir, patient_id))
        pdb.set_trace()
        label_idx = np.argmax(y_scores[i])
        sv_data = svs[label_idx, i]
        
        sv_data_mean = np.mean(sv_data, axis=1)
        top_lead_thresh = 1e-4 # empirical threshold from original code
        top_leads = np.where(sv_data_mean > top_lead_thresh)[0] # select top leads
        preds.append(classes[label_idx])
        print(patient_id, classes[label_idx], leads[top_leads])

        plot_shap(ecg_data, sv_data, leads, top_leads, patient_id, classes[label_idx])
