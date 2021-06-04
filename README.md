# Interpretable Deep Learning for Automatic Diagnosis of 12-lead Electrocardiogram
# +ECE 228 SP 21 Project, Prof. Gerstoft (Group 22)

This repository contains code for *Interpretable Deep Learning for Automatic Diagnosis of 12-lead Electrocardiogram*. Electrocardiogram (ECG) is a widely used reliable, non-invasive approach for cardiovascular disease diagnosis. With the rapid growth of ECG examinations and the insufficiency of cardiologists, accurately automatic diagnosis of ECG signals has become a hot research topic. Deep learning methods have demonstrated promising results in predictive healthcare tasks. In this work, we developed a deep neural network for multi-label classification of cardiac arrhythmias in 12-lead ECG records. Experiments on a public 12-lead ECG dataset showed the effectiveness of our method. The proposed model achieved an average area under the receiver operating characteristic curve (AUC) of 0.970 and an average F1 score of 0.813. Using single-lead ECG as model input produced lower performance than using all 12 leads. The best-performing leads are lead I, aVR, and V5 among 12 leads. Finally, we employed the SHapley Additive exPlanations (SHAP) method to interpret the model's behavior at both patient-level and population-level.

## Model Architecture

<img src="https://imgur.com/BIvuVUc.png" width="300">

> Deep neural network architecture for cardiac arrhythimas diagnosis.

<img src="https://i.imgur.com/FF0IS4v.png" width="300">

> Our modified model with bidirectional GRU layer.

## Requirements

### Dataset

The 12-lead ECG dataset used in this study is the CPSC2018 training dataset which is released by the 1st China Physiological Signal Challenge (CPSC) 2018 during the 7th International Conference on Biomedical Engineering and Biotechnology. Details of the CPSC2018 dataset can be found [here](https://bit.ly/3gus3D0). To access the processed data, click [here](https://www.dropbox.com/s/unicm8ulxt24vh8/CPSC.zip?dl=0). Commands to download and setup the dataset are detailed in the **Run** section.

### Software

- Python 3.7.4
- Matplotlib 3.1.1
- Numpy 1.17.2
- Pandas 0.25.2
- PyTorch 1.2.0
- Scikit-learn 0.21.3
- Scipy 1.3.1
- Shap 0.35.1
- Tqdm 4.36.1
- Wfdb 2.2.1

## Run

### Getting the Data

```sh
mkdir dataset
cd dataset
wget https://www.dropbox.com/s/unicm8ulxt24vh8/CPSC.zip
unzip CPSC.zip
```

OR, run the following from the git folder:    

```sh
./util_script.sh --getdata 
```

`1462c6fb5ca4ead17f8569bcc6a28012` is the md5sum of the zip file downloaded. 

### Getting the Pre-Trained DL Models

```sh
./util_script.sh --getmodel
```

`517edde2cda74c76f11f5189226ea6c4` is the md5sum of the zip file downloaded.

these models will be stored in `./model`

### Preprocessing and Baseline 12 Lead DL Model 

```sh
$ python preprocess.py --data-dir dataset/CPSC # Preprocessing
$ python main.py --data-dir dataset/CPSC --leads all --use-gpu # training
$ python predict.py --data-dir dataset/CPSC --leads all --use-gpu >> ./results/12lead_baseline_test.txt # evaluation
```

Since the pre-trained models are already available, **you may not need to train the model**. Run this script for performing pre-processing:

```sh
$ ./util_script.sh --preproc
```

### Running Tests

12 Lead bidirectional-GRU testing:
```sh
$ python predict.py --data-dir dataset/CPSC --leads all --use-gpu --biGRU 1 >> ./results/bigru_test.txt 
```

6, 3 or 1 Lead testing:
```sh
$ python predict.py --data-dir dataset/CPSC --leads I,II,III,aVR,aVL,aVF --use-gpu >> ./results/6lead_test.txt # 6 Lead
$ python predict.py --data-dir dataset/CPSC --leads I,II,V2 --use-gpu >> ./results/3lead_test.txt # 3 Lead
$ python predict.py --data-dir dataset/CPSC --leads I --use-gpu >> ./results/1lead_test.txt # 1 Lead
```

12, 1 Lead Downsampling testing:
```sh
$ python predict.py --data-dir dataset/CPSC --leads all --use-gpu --downsamp-rate 5 >> ./results/12lead_downsamp_test.txt
$ python predict.py --data-dir dataset/CPSC --leads I --use-gpu --downsamp-rate 5 >> ./results/1lead_downsamp_test.txt
```

OR to, run all tests together:
```sh
$ ./util_script.sh --testall
```

This would produce all results in `./results`.

### File Organization

* `preprocess.py`: Data preprocessing. Takes the dataset and procures labels and partitions set into folds randomly. The fold partitioning is truly random without a set seed. Therefore, it cannot be repeated. 8 folds for training, 1 for validation and 1 for testing are randomly chosen according to a seed. This seed defaults to 42, and means that the train and test process are probably repeatable for a particular preprocessed dataset.
* `dataset.py`: Dataset object that inherits from torch dataset. It produces elements of the dataset for the DataLoader. It can scale/shift data for data augmentation during training phase.
* `main.py`: Main file used for model training and instantiation
* `predict.py`: Script for running prediction based on already-trained model
* `resnet.py`: Torch model building and class. `resnet34` is the baseline DL model. `resnet34_GRU` is our bi-GRU model.   