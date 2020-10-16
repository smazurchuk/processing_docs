```python 
import os
import pwd
import sys
import time
import subprocess

from shlex import split
from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

SCRIPT_FILE = Path(sys.argv[0]).resolve()
SCRIPT_DIR = SCRIPT_FILE.parent
QSUB_SCRIPT = SCRIPT_DIR.joinpath('singularity_fmriprep_epilepsy.bash')

# change variables below to fit experiment
CONTAINER = Path('/rcc/stor1/depts/neurology/users/jheffernan/singularity_images/fmriprep-v20.1.0.simg')
EXPERIMENT_DIR = SCRIPT_DIR.joinpath('..', '..').resolve()
BIDS_DIR = EXPERIMENT_DIR.joinpath('bids')
DERIVATIVES_DIR = EXPERIMENT_DIR.joinpath('derivatives', 'fmriprep-v20.1.0')

if not CONTAINER.is_file():
    raise Exception(f'Container file does not exist: {CONTAINER}')

def user_name():
    return pwd.getpwuid(os.getuid()).pw_name

def make_readable_command(cmd):
    results = [cmd[0]] + ['    ' + x for x in cmd[1:]]
    return ' \\\n'.join(results)

def get_parser():
    """Define parser object"""

    parser = ArgumentParser(description='Run fmriprep for epilepsy dataset.',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    # REQUIRED
    parser.add_argument('participants', action='store', nargs='+',
                        help='bids participant names')

    # OPTIONAL
    parser.add_argument('--nthreads', action='store', type=int, default=16,
                        help='maximum number of threads across all processes')

    # OPTIONAL TORQUE
    parser.add_argument('--omp-nthreads', action='store', type=int, default=8,
                        help='maximum number of threads per-process')
    parser.add_argument('--email', action='store', default=(user_name() + '@mcw.edu'),
                        help='email address')
    parser.add_argument('--mem', action='store', type=int, default=200,
                        help='qsub memory in gigabytes')
    parser.add_argument('--walltime', action='store', default='48:00:00',
                        help='qsub walltime')
    parser.add_argument('--testing', action='store_true',
                        help='do not run the command, only print information')

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    participants = args.participants
    nthreads = args.nthreads

    omp_nthreads = args.omp_nthreads
    email = args.email
    mem = args.mem
    walltime = args.walltime

    if omp_nthreads > nthreads:
        raise Exception('omp_nthreads ({omp_nthreads}) > nthreads ({nthreads})')

    bids_participants = {x.stem.split('-')[1] for x in BIDS_DIR.glob('sub-*')}
    invalid_participants = set(participants).difference(bids_participants)
    if invalid_participants:
        raise Exception(f'Invalid participants: {invalid_participants}')

    log_dir = SCRIPT_DIR.joinpath('qsub_jobs', user_name())
    log_dir.mkdir(mode=int(0o775), exist_ok=True)

    for participant in participants:
        job_name = f'fmriprep_{participant}'
        batch_file = log_dir.joinpath(job_name)

        variable_list = [
            'participant="{}"'.format(participant),
            'batch_file="{}"'.format(batch_file),
            'container="{}"'.format(CONTAINER),
            'experiment_dir="{}"'.format(str(EXPERIMENT_DIR)),
            'bids_dir="{}"'.format(str(BIDS_DIR)),
            'derivatives_dir="{}"'.format(str(DERIVATIVES_DIR)),
            'nthreads="{}"'.format(nthreads),
            'omp_nthreads="{}"'.format(omp_nthreads),
        ]
        variable_list = ','.join(variable_list)

        cmd = [
            f'qsub -M {email}',
            f'-m abe',
            f'-j oe',
            f'-N {job_name}',
            f'-o {log_dir}',
            f'-V',
            f'-v {variable_list}',
            f'-l nodes=1:ppn={nthreads},walltime={walltime},mem={mem}gb',
            f'-q bigmem',
            f'{QSUB_SCRIPT}'
        ]

        if not args.testing:
            results = subprocess.run(split(' '.join(cmd)), capture_output=True)
            print(results.stdout.decode().strip())
            if results.stderr:
                print(results.stderr.decode().strip())
        else:
            print('Here is your qsub command:')
            print(make_readable_command(cmd))

if __name__ == '__main__':
    main()        

 

```