"""
Data preparation for DALI datasets

Authors
* Xiangming Gu 2022
"""
import re
import os
import csv
import pdb
import json
import argparse
from collections import Counter
import logging
import torch
import torchaudio
import torchaudio.functional as F
from tqdm import tqdm
SAMPLERATE = 16000


# Create and configure logger
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('dali_prepare.log'),
        logging.StreamHandler()
    ]
)

# Create logger
logger = logging.getLogger(__name__)


def prepare_audio_train_valid(
    root,
    save_folder,
    skip_prep = False,
    threshold = 0.1,  # threshold: remove the utterances whose duration is less than the threshold
):
    """
    This function prepares the csv files for train and valid splits of DALI dataset
    """
    if skip_prep:
        return
    
    # save folder
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    resample_folder = os.path.join(root, 'data')
    os.makedirs(resample_folder, exist_ok=True)
    anno_path = os.path.join(root, 'metadata.json') #'metadata_splitted_normalized.json')
    debug_file = "debug.txt"
    
    # open json files
    with open(anno_path, 'r') as f:
        data = json.load(f)
    f.close()
    
    # # collect missing keys
    # check_key_matches = False
    # if check_key_matches:
    #     missing_keys = []
    #     keys_from_dir = [os.path.splitext(fn)[0] for fn in os.listdir(resample_folder)]
    #     for k in tqdm(data.keys()):
    #         if k not in keys_from_dir:
    #             # logging.info(f"Key {k} not found in the directory")
    #             missing_keys.append(k)
    #     missing_percent = len(missing_keys)/len(keys_from_dir)

    #     # remove missing keys
    #     answer = input(
    #         f"""Some entires in the metadata file are missing,
    #         accounting for {missing_percent}% of what\'s in the audio directory.
    #         Do you want to remove these from the file? (y/n)"""
    #     )
    #     if answer.lower() == 'y':
    #         for k in missing_keys:
    #             del data[k]
    #     with open(os.path.join(root, 'metadata.json'), 'w') as f: json.dump(data, f)   

    csv_lines_train = [["ID", "duration", "wav", "wrd"]]
    csv_lines_valid = [["ID", "duration", "wav", "wrd"]]

    for key in tqdm(data.keys()):
        # fetch values
        value = data[key]
        wrds = value["lyrics"]
        split = value["split"]

        resample_path = os.path.join(resample_folder, key + '.wav')

        # remove extra blank spaces
        wrds = wrds.split(' ')
        wrds = list(filter(None, wrds))
        if len(wrds) == 0:
            print("No targets")
            continue
        wrds = ' '.join(wrds)

        # load audio
        try:
            signal, fs = torchaudio.load(resample_path)
        except RuntimeError as e:
            logger.debug(f'path {resample_path} caused error: {e}')
            pdb.set_trace()
        if signal.shape[1] == 0:
            with open(debug_file, "w") as f:
                f.write(resample_path)
            continue
        if fs != SAMPLERATE:
            signal = F.resample(signal, orig_freq=fs, new_freq=SAMPLERATE)
        duration = signal.shape[1] / SAMPLERATE

        if duration < threshold:
            continue
        
        # construct csv files
        csv_line = [
            key, str(duration), resample_path, wrds,
        ]

        # append
        if split == "train":
            csv_lines_train.append(csv_line)
        elif split == "valid":
            csv_lines_valid.append(csv_line)

    # create csv files for each split
    csv_save_train = os.path.join(save_folder, "train.csv")
    with open(csv_save_train, mode="w") as csv_f:
        csv_writer = csv.writer(
            csv_f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        for line in csv_lines_train:
            csv_writer.writerow(line)
    
    csv_save_valid = os.path.join(save_folder, "valid.csv")
    with open(csv_save_valid, mode="w") as csv_f:
        csv_writer = csv.writer(
            csv_f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        for line in csv_lines_valid:
            csv_writer.writerow(line)


# not completed
def prepare_audio_test(
    root,
    save_folder,
    skip_prep = False,
    threshold = 0.1,  # threshold: remove the utterances whose duration is less than the threshold
):
    """
    This function prepares the csv files for test splits of DALI dataset
    """
    if skip_prep:
        return
    data_folder = os.path.join(root, 'data')
    anno_path = os.path.join(root, 'metadata.json')
    save_csv = os.path.join(save_folder, 'test.csv')
    print(f"Save data in the path: {save_csv}")
    
    # open json files
    with open(anno_path, 'r') as f:
        data = json.load(f)
    f.close()

    csv_lines = [["ID", "duration", "wav", "wrd"]]

    for key in tqdm(data.keys()):
        # fetch values
        value = data[key]
        wrds = value["lyrics"]

        # determine target path
        path = os.path.join(data_folder, key + '.wav')

        # load audio
        signal, fs = torchaudio.load(path)
        if fs != SAMPLERATE:
            signal = F.resample(signal, orig_freq=fs, new_freq=SAMPLERATE)
        duration = signal.shape[1] / SAMPLERATE

        if duration < threshold:
            continue
        
        # construct csv files
        csv_line = [
            key, str(duration), path, wrds,
        ]

        # append
        csv_lines.append(csv_line)

    # create csv files for each split
    
    csv_save_train = os.path.join(save_csv)
    with open(csv_save_train, mode="w") as csv_f:
        csv_writer = csv.writer(
            csv_f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        for line in csv_lines:
            csv_writer.writerow(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--train_folder",
        type=str,
        default="/home/brendanoconnor/Documents/datasets/lyrics/singing/DALI/audio/DALI_train_val_segmented",
        help="The saved path for DALI training data folder"
    )
    parser.add_argument(
        "--test_folder",
        type=str,
        default="/home/brendanoconnor/Documents/datasets/lyrics/singing/DALI/audio/DALI_test_segmented",
        help="The saved path for DALI test data folder"
    )
    parser.add_argument(
        "--save_folder",
        type=str,
        default="/home/brendanoconnor/Documents/datasets/lyrics/singing/DALI/csv_data",
        help="The saved path for prepared csv files"
    )
    args = parser.parse_args()
    prepare_audio_train_valid(root=args.train_folder, save_folder=args.save_folder)
    # prepare_audio_test(root=args.test_folder, save_folder=args.save_folder)
    