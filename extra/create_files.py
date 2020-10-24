'''This script creates an example directory structure for raw_data_storage'''

import os

from pathlib import Path

scans = {
    '001': (1, 2),
    '002': (1,),
    '003': (1,),
}

exp_dir = Path('experiment')
sourcedata = exp_dir.joinpath('sourcedata')
hcp = exp_dir.joinpath('hcp')
bids = exp_dir.joinpath('bids')

bids_dirs = [
    'anat',
    'dwi',
    'func',
    'fmap',
]

hcp_dirs = [
    'T1w_MPR1',
    'T2w_CUBE1',
    'DWI_dir97_RL',
    'SpinEchoFieldMap_RL',
    'SpinEchoFieldMap_LR',
    'rfMRI_REST1_RL',
    'rfMRI_REST2_RL',
    'tfMRI_STORYMATH_RL',
]

for subject, sessions in scans.items():

    for session in sessions:

        # make sourcedata
        sd = sourcedata.joinpath(f'sub-{subject}', f'ses-{session}')
        sd.mkdir(parents=True, exist_ok=True)
        sd.joinpath(f'{subject}s{session:02d}.tar.gz').touch(exist_ok=True)

        # make bids
        subj_bids = bids.joinpath(f'sub-{subject}', f'ses-{session}')
        subj_bids.mkdir(parents=True, exist_ok=True)
        for bd in bids_dirs:
            subj_bids.joinpath(bd).mkdir(parents=True, exist_ok=True)

        # make hcp
        subj_hcp = hcp.joinpath(f'{subject}')
        for hd in hcp_dirs:
            subj_hcp.joinpath(f'{hd}_{session:02d}').mkdir(parents=True, exist_ok=True)
        
        
