conda create -n alt python=3.8.12
conda activate alt
pip install torch==1.9.1+cu111 torchvision==0.10.1+cu111 torchaudio==0.9.1 -f https://download.pytorch.org/whl/torch_stable.html
cd ALT_SpeechBrain
pip install -r requirements.txt
pip install --editable .
pip install transformers
pip install datasets
pip install sklearn
pip install setuptools==59.5.0
pip install tensorboard

# Download RNNLM_mix from ALT's README.md respository link
# Add the path for this to DALI/ALT and replace the !PLACEHOLDER value for the attribute 'pretrained_lm_path' in hparams/train_wav2vec2_tb.yaml.

Collect the DALI audio
Perform source separation using audio-processing's MDX with custom script
Use segment_DALI_audio_by_lines.py to filter, segment and generate json for train, valid and test subsets.
Then run DALI/ALT/dali_prepare.py to convert json to csv files for use in training