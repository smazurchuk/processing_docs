```python 
import os
import re
import json

import pandas as pd
import nibabel as nib

from pathlib import Path
from bids import BIDSLayout
from argparse import ArgumentParser

ADDED_METADATA = {
    'task_name': {'Description': 'task name for func files'},
    'run_num': {'Description': 'the run number'},
    'include_deconvolve': {'Description': 'include the func file in 3dDeconvolve'},
    'volumes': {'Description': 'number of volumes in mri'},
}


def get_parser():
    """Define parser object"""
    parser = ArgumentParser(description='Adjusts scans.tsv after heudiconv completeion')

    # REQUIRED
    parser.add_argument('bids_dir', action='store', help='the bids directory')

    # OPTIONAL
    parser.add_argument('--participants', action='store', nargs='+', required=True,
                        help='''participants to correct. All sessions are 
                                corrected. If not specified, all participants
                                in bids_dir will be corrected''')

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    layout = BIDSLayout(Path(args.bids_dir).resolve())

    all_participants = layout.get_subjects()
    participants = args.participants

    invalid_participants = set(participants).difference(all_participants)
    if invalid_participants:
        raise Exception(f'Invalide participants: {invalid_participants}')

    for participant in participants:

        # scans.tsv can be located at these levels:
        #   subject
        #   session

        scans = layout.get(suffix='scans', 
                           extension='tsv', 
                           subject=participant)

        for scan in scans:    

            scan_path = Path(scan.path)
            json_path = scan_path.parent / (scan_path.stem + '.json')
            df = scan.get_df()

            # equivalent fields in json meta data
            # task_name = TaskName
            # run_num = NA
            # include_deconvolve = NA
            # volumes = NumberOfTemporalPositions or dcmmeta_shape

            df['task_name'] = df['filename'].str.extract(r'task-([a-zA-Z0-9]+)', expand=False)
            df['run_num'] = df['filename'].str.extract(r'run-(\d+)', expand=False)
            df['include_deconvolve'] = pd.notnull(df['task_name'])

            filenames = [scan_path.parent / x for x in df['filename']]
            df['volumes'] = [nib.load(x).header['dim'][4] for x in filenames]

            df.to_csv(scan_path, sep='\t', na_rep='n/a', index=False)

            try:
                with open(json_path, 'r') as f:
                    json_data = json.load(f)
            except FileNotFoundError:
                json_data = {}

            json_data.update(ADDED_METADATA)
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)

            print(f'Updated {scan.filename}')

        print(f'Finished participant {participant}')

if __name__ == '__main__':
    main()
 

```