#!/bin/sh

usage()
{
    echo "usage: util_script.sh [-options]
    Options:
    	-d | --getdata      : Download Dataset
    	-m | --getmodel     : Download Pre-Trained Model
    	-p | --preproc		: Preprocess the data
    	-t | --testall      : Test all models
    	-h | --help         : Print this help message"
}


if test "$#" = 0; then
    usage
fi

DOWNDATA=0
DOWNMODEL=0
TESTMODEL=0
PREPROC=0

while [ "$1" != "" ]; do
    case $1 in
    	-d | --getdata )    DOWNDATA=1
                                ;;
    	-m | --getmodel )   DOWNMODEL=1
                                ;;
		-t | --testall )    TESTMODEL=1
								;;
        -p | --preproc )    PREPROC=1
								;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

if [ "$DOWNDATA" = "1" ]; then
	echo "Downloading dataset: ~3 Minute job"
	mkdir ./dataset
	cd dataset
	wget https://www.dropbox.com/s/unicm8ulxt24vh8/CPSC.zip
	unzip CPSC.zip
	cd ..
	echo "Done"
fi


if [ "$DOWNMODEL" = "1" ]; then
	echo "Downloading Pre-Trained Models: ~1 Minute job"
	mkdir ./models
	cd models
	wget https://www.dropbox.com/s/ivrv1g61mcs6s6j/ece228_group22_models.zip
	unzip ece228_group22_models.zip
	cd ..
	echo "Done"
fi

if [ "$PREPROC" = "1" ]; then
	echo "Performing Data Pre-Processing: ~2 Minute job"
	python preprocess.py --data-dir dataset/CPSC
	echo "Done"
fi

if [ "$TESTMODEL" = "1" ]; then
	echo "Testing All"

	echo "Testing 12 Lead Baseline"
	python predict.py --data-dir dataset/CPSC --leads all --use-gpu >> ./results/12lead_baseline_test.txt 

	echo "Test Bi-GRU 12 Lead Model"
	python predict.py --data-dir dataset/CPSC --leads all --use-gpu --biGRU 1 >> ./results/bigru_test.txt 

	echo "Test 6 Lead Model"
	python predict.py --data-dir dataset/CPSC --leads I,II,III,aVR,aVL,aVF --use-gpu >> ./results/6lead_test.txt # 6 Lead

	echo "Test 3 Lead Model"
	python predict.py --data-dir dataset/CPSC --leads I,II,V2 --use-gpu >> ./results/3lead_test.txt # 3 Lead

	echo "Test 1 Lead Model"
	python predict.py --data-dir dataset/CPSC --leads I --use-gpu >> ./results/1lead_test.txt # 1 Lead

	echo "Test 100 Hz 12 Lead Model"
	python predict.py --data-dir dataset/CPSC --leads all --use-gpu --downsamp-rate 5 >> ./results/12lead_downsamp_test.txt

	echo "Test 100 Hz 1 Lead Model"
	python predict.py --data-dir dataset/CPSC --leads I --use-gpu --downsamp-rate 5 >> ./results/1lead_downsamp_test.txt

	echo "Done"
fi
