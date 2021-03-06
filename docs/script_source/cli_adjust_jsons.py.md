```python 
import os
import json

from pathlib import Path
from bids import BIDSLayout
from datetime import datetime
from argparse import ArgumentParser

def get_parser():
    """Define parser object"""
    parser = ArgumentParser(description='Corrects json files in bids format')
    parser.add_argument('bids_dir', action='store', help='the bids directory') 
    parser.add_argument('--participants', action='store', nargs='+',
                        help='''participants to correct. All sessions are 
                                corrected. If not specified, all participants
                                in bids_dir will be corrected''')

    func = parser.add_argument_group('func', 'func options')
    func.add_argument('--hyperband', action='store', type=int,
                      help="the hyperband factor")
    func.add_argument('--tr', action='store', type=float, 
                      help='repetition time')

    sliceTiming = func.add_mutually_exclusive_group()
    sliceTiming.add_argument('--slicetiming', action='store', type=float,
                             nargs='+', help='''the time at which slices are 
                                                acquired in a single fMRI brain 
                                                scan. These value must be less 
                                                than the TR.''')
    sliceTiming.add_argument('--remove-slicetiming', action='store_true',
                             help='remove SliceTiming field')

    fmap = parser.add_argument_group('fmap', 'fmap options')
    fmap.add_argument('--match-se-fieldmaps', action='store_true',
                      help='''Match field maps together and fill IntendedFor 
                              field for spin-echo field map json files''')

    func_fmap = parser.add_argument_group('func+fmap', 'func+fmap options')

    return parser

def get_scan_time(meta):
    return datetime.strptime(meta['AcquisitionTime'], "%H:%M:%S.%f")

def match_fms(fms1, fms2):
    '''pairs each json in each list based on `AcquisitionTime` in metadata'''

    matches = []
    for d1, m1 in fms1.items():
        curMatch = list(fms2)[0]
        t1 = get_scan_time(m1)
        t2 = get_scan_time(fms2[curMatch])
        curDiff = abs((t1 - t2).total_seconds())
        for d2, m2 in fms2.items():
            t2 = get_scan_time(m2)
            checkDiff = abs((t1 - t2).total_seconds())
            if checkDiff < curDiff:
                curMatch = d2
                curDiff = checkDiff
        matches.append((d1, curMatch))

    return matches

def match_funcs_to_fm_pairs(pairs, fm_info, func_info):

    intended_for = {x: [] for x in pairs}

    for func_image, func_metadata in func_info.items():
        cur_pair = pairs[0]
        t1 = get_scan_time(func_metadata)
        t2 = get_scan_time(fm_info[cur_pair[0]])
        t3 = get_scan_time(fm_info[cur_pair[1]])
        cur_min = min(abs(t1 - t2).total_seconds(),
                      abs(t1 - t3).total_seconds())

        for pair in pairs:
            t2 = get_scan_time(fm_info[pair[0]])
            t3 = get_scan_time(fm_info[pair[1]])
            check_min = min(abs(t1 - t2).total_seconds(),
                            abs(t1 - t3).total_seconds())
            if check_min < cur_min:
                cur_pair = pair
                cur_min = check_min

        intended_for[cur_pair].append(func_image)

    return intended_for
        
def main():
    parser = get_parser()
    args = parser.parse_args()
    
    bids_dir = Path(args.bids_dir).resolve()
    layout = BIDSLayout(str(bids_dir))

    participants = args.participants if args.participants else layout.get_subjects()

    process_func = (args.hyperband or
                    args.tr or
                    args.slicetiming or
                    args.remove_slicetiming)

    process_fmap = (args.match_se_fieldmaps)

    if process_func:
        jsons = layout.get(return_type='file', datatype='func', suffix='bold',
                           extension='json', subject=participants)
        for one_json in jsons:
            with open(one_json) as f:
                meta_data = json.load(f)

            if args.hyperband:
                meta_data['MultibandAccelerationFactor'] = args.hyperband

            if args.tr:
                meta_data['RepetitionTime'] = args.tr

            if args.slicetiming:
                meta_data['SliceTiming'] = args.SliceTiming

            if args.remove_slicetiming:
                try:
                    meta_data.pop('SliceTiming')
                except KeyError:
                    pass

            print('Writing file {}'.format(one_json))
            with open(one_json, 'w') as f:
                json.dump(meta_data, f, indent=2)

    if process_fmap:
        for subject in participants:
            subject_dir = str(bids_dir.joinpath(f'sub-{subject}')) + '/'

            all_fms = layout.get(datatype='fmap', 
                                 suffix='epi', 
                                 extension='nii.gz',
                                 subject=subject)

            session = {fm.get_entities().get('session') for fm in all_fms}
            ses_fms = {ses: [] for ses in session}
            for fm in all_fms:
                ses_fms[fm.get_entities().get('session')].append(fm)

            for session, fms in ses_fms.items():
                fm_info = {x: x.get_metadata() for x in fms}

                # assume only 1 pair of directions
                neg_fms = {}
                pos_fms = {}
                for k, v in fm_info.items():
                    phase_encoding_direction = v['PhaseEncodingDirection']
                    if phase_encoding_direction.endswith('-'):
                        if phase_encoding_direction in neg_fms:
                            neg_fms[phase_encoding_direction].append(k)
                        else:
                            neg_fms[phase_encoding_direction] = [k]
                    else:
                        if phase_encoding_direction in pos_fms:
                            pos_fms[phase_encoding_direction].append(k)
                        else:
                            pos_fms[phase_encoding_direction] = [k]

                if len(neg_fms) != 1:
                    raise Exception(f'Found more than 1 negative phase encoding diretion.\n'
                                    f'Directions: {neg_fms.keys()}')

                if len(pos_fms) != 1:
                    raise Exception(f'Found more than 1 positive phase encoding direction.\n'
                                    f'Directions: {pos_fms.keys()}')

                # check if phase encoding directions are opposites
                pos_direction = list(pos_fms)[0]
                neg_direction = list(neg_fms)[0]
                if (pos_direction + '-') != neg_direction:
                    raise Exception('Found unmatched phase encoding directions:\n'
                                    f'pos: {pos_direction} neg: {neg_direction}')

                # check if phase encoding directions have same number of field maps
                num_pos = len(pos_fms[pos_direction])
                num_neg = len(neg_fms[neg_direction])
                if num_pos != num_neg:
                    raise Exception('There are unequal number of positive and negative field maps\n'
                                    f'Num positive: {num_pos}\n',
                                    f'Num negative: {num_neg}\n')

                if args.match_se_fieldmaps:
                    funcs = layout.get(datatype='func',
                                       suffix='bold', 
                                       extension='nii.gz',
                                       session=session,
                                       subject=subject)
                    func_info = {x: x.get_metadata() for x in funcs}

                    fms1 = {x: fm_info[x] for x in pos_fms[pos_direction]}
                    fms2 = {x: fm_info[x] for x in neg_fms[neg_direction]}

                    matched_fms = match_fms(fms1, fms2)
                    for fm1, fm2 in matched_fms:
                        fm_info[fm1]['FieldMapPair'] = fm2.path
                        fm_info[fm2]['FieldMapPair'] = fm1.path

                    intended_for = match_funcs_to_fm_pairs(matched_fms, 
                                                           fm_info, 
                                                           func_info)
                    for k, v in intended_for.items():
                        fm_info[k[0]]['IntendedFor'] = [x.path.replace(subject_dir, '') for x in v]
                        fm_info[k[1]]['IntendedFor'] = [x.path.replace(subject_dir, '') for x in v]

                for fm_img, fm_meta in fm_info.items():
                    fm_json = fm_img.path.replace('nii.gz', 'json')

                    print('Writing file {}'.format(fm_json))
                    with open(fm_json, 'w') as f:
                        json.dump(fm_meta, f, indent=2)

if __name__ == '__main__':
    main()
    
    

 

```