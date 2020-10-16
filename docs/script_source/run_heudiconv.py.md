```python 
import os
import pwd
import sys
import json
import time
import subprocess

from shlex import split
from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

SCRIPT_FILE = Path(sys.argv[0]).resolve()
SCRIPT_DIR = SCRIPT_FILE.parent
QSUB_SCRIPT = SCRIPT_DIR.joinpath('singularity_heudiconv.bash')

CONFIGURATION = SCRIPT_DIR.joinpath('configuration.json')
with CONFIGURATION.open() as f:
    configuration = json.load(f)
    CONTAINER = Path(configuration['containers']['heudiconv'])

if not CONTAINER.is_file():
    raise Exception(f'Container file does not exist: {CONTAINER}')

def user_name():
    return pwd.getpwuid(os.getuid()).pw_name

def make_readable_command(cmd):
    results = [cmd[0]] + ['    ' + x for x in cmd[1:]]
    return ' \\\n'.join(results)

def get_parser():
    """Define parser object"""

    parser = ArgumentParser(description='Run heudiconv to extract tar.gz to bids.',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    # REQUIRED
    parser.add_argument('experiment_dir', action='store', help='the bids directory')
    parser.add_argument('heuristic', action='store', help='heuristic file')
    parser.add_argument('--participants', action='store', required=True, 
                        nargs='+', help='participant names')

    # OPTIONAL
    parser.add_argument('--sessions', action='store', nargs='+', 
                        help='sessions')

    # OPTIONAL TORQUE
    parser.add_argument('--email', action='store', default=(user_name() + '@mcw.edu'),
                        help='email address')
    parser.add_argument('--mem', action='store', type=int, default=20,
                        help='qsub memory in gigabytes')
    parser.add_argument('--walltime', action='store', default='7:00:00',
                        help='qsub walltime')
    parser.add_argument('--testing', action='store_true',
                        help='do not run the command, only print information')

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    experiment_dir = Path(args.experiment_dir).resolve()
    bids_dir = experiment_dir.joinpath('bids')
    sourcedata = experiment_dir.joinpath('sourcedata')
    heuristic = Path(args.heuristic).resolve()
    participants = args.participants
    sessions = args.sessions

    email = args.email
    mem = args.mem
    walltime = args.walltime

    # check files here
    if not experiment_dir.is_dir():
        raise Exception(f'experiment_dir is not a directory: {experiment_dir}')

    if not sourcedata.is_dir():
        raise Exception(f'sourcedata is not a directory: {sourcedata}')

    if not heuristic.is_file():
        raise Exception(f'heuristic is not a file: {heuristic}')

    info = []
    for participant in participants:

        if sessions is None:
            tar_file = sourcedata.joinpath(f'sub-{participant}', 
                                           f'{participant}.tar.gz')
            if not tar_file.is_file():
                raise Exception(f'tar_file is not a file: {tar_file}')

            dicom_dir_template = "{subject}.tar.gz"
            info.append(([f'{participant}'], 
                         tar_file, 
                         dicom_dir_template)) 
        else:
            for session in sessions:
                tar_file = sourcedata.joinpath(f'sub-{participant}', 
                                               f'ses-{session}',
                                               f'{participant}_{session}.tar.gz')
                if not tar_file.is_file():
                    raise Exception(f'tar_file is not a file: {tar_file}')

                dicom_dir_template = "{subject}_{session}.tar.gz"
                info.append(([f'{participant}', f'{session}'],
                             tar_file, 
                             dicom_dir_template)) 

    log_dir = SCRIPT_DIR.joinpath('qsub_jobs', user_name())
    log_dir.mkdir(mode=int(0o775), exist_ok=True)

    for i, (descriptor, tar_file, dicom_dir_template) in enumerate(info):
        job_name = 'heudiconv_' + '_'.join(descriptor)
        batch_file = log_dir.joinpath(job_name)

        out_dir = bids_dir.joinpath('sub-{}'.format(descriptor[0]))
        if len(descriptor) == 2:
            out_dir = bids_dir.joinpath('ses-{}'.format(descriptor[1]))
                
        variable_list = [
            'participant="{}"'.format(descriptor[0]),
            'tar_file="{}"'.format(tar_file),
            'dicom_dir_template="{}"'.format(dicom_dir_template),
            'batch_file="{}"'.format(batch_file),
            'out_dir="{}"'.format(out_dir),
            'container="{}"'.format(CONTAINER),
            'bids_dir="{}"'.format(bids_dir),
            'heuristic="{}"'.format(heuristic),
        ]
        if len(descriptor) == 2:
            variable_list.append('session="{}"'.format(descriptor[1]))
        variable_list = ','.join(variable_list)
            
        cmd = [
            f'qsub -M {email}',
            f'-m abe',
            f'-j oe',
            f'-N {job_name}',
            f'-o {log_dir}',
            f'-V',
            f'-v {variable_list}',
            f'-l nodes=1:ppn=1,walltime={walltime},mem={mem}gb',
            f'-q bigmem',
            f'{QSUB_SCRIPT}'
        ]

        if not args.testing:
            results = subprocess.run(split(' '.join(cmd)), capture_output=True)
            print(results.stdout.decode().strip())

            error_codes = results.stderr.decode().strip()
            if error_codes:
                print('ERRORS:')
                print(error_codes)

            if len(info) > 1 and i != (len(info) - 1):
                print('Waiting 60 seconds to avoid heudiconv collisions...')
                time.sleep(60)
        else:
            print('Here is your qsub command:')
            print(make_readable_command(cmd))

if __name__ == '__main__':
    main()        



 

```