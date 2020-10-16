```python 
import os
import pwd
import sys
import json
import subprocess

from shlex import split
from datetime import datetime
from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

SCRIPT_FILE = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_FILE.parent
QSUB_SCRIPT = SCRIPT_DIR.joinpath('singularity_template.bash')
PYTHON_SCRIPT = str(SCRIPT_DIR
                    .joinpath('..', 'cli_tarred_dicom_info.py')
                    .resolve())

CONFIGURATION = SCRIPT_DIR.joinpath('configuration.json')
with CONFIGURATION.open() as f:
    configuration = json.load(f)
    CONTAINER = Path(configuration['containers']['miniconda'])

if not CONTAINER.is_file():
    raise Exception(f'Container file does not exist: {CONTAINER}')

def user_name():
    return pwd.getpwuid(os.getuid()).pw_name

def make_readable_command(cmd):
    results = [cmd[0]] + ['    ' + x for x in cmd[1:]]
    return ' \\\n'.join(results)

def get_parser():
    """Define parser object"""

    parser = ArgumentParser(description='Get dicom information from tar.gz file.',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    # REQUIRED
    parser.add_argument('--in_files', action='store', nargs='+',
                        help='the tar.gz files', required=True)

    # OPTIONAL TORQUE
    parser.add_argument('--email', action='store', default=(user_name() + '@mcw.edu'),
                        help='email address')
    parser.add_argument('--mem', action='store', type=int, default=10,
                        help='qsub memory in gigabytes')
    parser.add_argument('--walltime', action='store', default='00:30:00',
                        help='qsub walltime')
    parser.add_argument('--testing', action='store_true',
                        help='do not run the command, only print information')

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    in_files = [Path(x).resolve() for x in args.in_files]

    email = args.email
    mem = args.mem
    walltime = args.walltime

    # check files here
    for one_file in in_files:
        if not one_file.is_file():
            raise Exception(f'in_file is not a file: {one_file}')
    in_files = ' '.join(str(x) for x in in_files)

    log_dir = SCRIPT_DIR.joinpath('qsub_jobs', user_name())
    log_dir.mkdir(mode=int(0o775), exist_ok=True)

    singularity_cmd = [
        f'singularity exec',
        f'{CONTAINER} python {PYTHON_SCRIPT}',
        f'--in_files {in_files}']

    singularity_cmd = ' '.join(singularity_cmd)
    job_name = 'tarred_dicom_info_{}'.format(
        datetime.today().strftime('%Y%m%d%H%M%S'))
    batch_file = log_dir.joinpath(job_name)
    variable_list = f'cmd="{singularity_cmd}",batch_file="{batch_file}"'

    cmd = [
        f'qsub -M {email}',
        f'-m abe',
        f'-j oe',
        f'-q medmem',
        f'-N {job_name}',
        f'-o {log_dir}',
        f'-V',
        f'-v {variable_list}',
        f'-l nodes=1:ppn=1,walltime={walltime},mem={mem}gb',
        f'{QSUB_SCRIPT}'
    ]

    if not args.testing:
        results = subprocess.run(split(' '.join(cmd)), capture_output=True)
        print(results.stdout.decode().strip())
    else:
        print('Here is your qsub command:')
        print(make_readable_command(cmd))

if __name__ == '__main__':
    main()        


 

```