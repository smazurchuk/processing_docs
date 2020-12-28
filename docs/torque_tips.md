# My philosophy

Submitting jobs should be easy. I do not want to create a job script every time I run a job; this is a hassle. I want to perform as few keystrokes a possible. I do not want to put a bunch of pieces together; everything should be in an expected place. We should spend as little time submitting jobs to the cluster, so we can focus on more important problems. Do not reinvent the wheel and use well established tools.

My solution so far has been to embrace python to submit jobs to the cluster. Python has several useful built-in features for writing command line progams. The `argparse` package is great, because it simultaneously generates command line options and help.

## Directory structure

Organize files and use the same organization scheme across experiments. Here is my proposed directory strucutre:

```pre
experiment_name
|-- bids
|-- derivatives
|   `-- fmriprep-v20.1.0
|       |-- deconvolve
|       `-- fmriprep
|-- scripts
|   |-- commands
|   |-- configurations
|   |-- custom
|   |   |-- study
|   |   `-- pipelines
|-- singularity_images
|-- sourcedata
|   |-- sub-15369s01
|   |   `-- eprime
|   |-- sub-15452s01
|   |   `-- eprime
|   `-- sub-test1s01
|       `-- eprime
|-- templateflow
`-- tmp
```

* **experiment_name** is the top level directory and should describe the experiment.
* **bids** is a bids compliant folder containing the raw data in nifti format.
* **derivatives** contains all files derived from the bids directory. I like to create a sub-directory (fmriprep-v20.1.0 in this case) to inidicate the fmriprep version.
* **scripts** contains our scripts.
    * **commands** is a general-purpose repository containing python command-line scripts. All necessary operations should be performed in these scripts; do not leave any work for bash scripts. This folder is a git repository and can be cloned into any epxeriment directory. 
    * **custom** contains scripts written specifically for this experiment. I recommend creating this as a git repository so it can be cloned into scratch sapce.
    * **custom/study** contains study specific scripts.
    * **custom/pipelines** contains study specific HPC cluster scripts.
    * **custom/configurations** contains configuration files (heursiticy.py, task.json, etc.).
* **singularity_images** contains singularity images. I try to run all my scripts through singularity images, so we have the software we need in one place.
* **sourcedata** contains all participant dicom files in tar.gz format.
* **templateflow** contains standard space templates used in normalization. This is need for fmriprep.

## Job submission

I keep the job submissions scripts in **scripts/custom/torque**. A single pipeline consists of 2 files:

    * **constants.py** - This file contains default paths to files and directories. If we use the same directory structure across studies, it should not change much. All pipelines use this file.
    * **pipeline1.py** - This file writes out the pipeline bash script and submits it to the HPC. I number the pipelines in the order they should be run.

I am going to use the SOE experiment as an example. Here is its current **constants.py**:

```python
from pathlib import Path

SCRIPT_FILE = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_FILE.parent
QSUB_SCRIPT = SCRIPT_DIR.joinpath('singularity_template.bash')

# change variables below to fit experiment
EXPERIMENT_DIR = SCRIPT_DIR.joinpath('..', '..', '..').resolve()
BIDS_DIR = EXPERIMENT_DIR.joinpath('bids')
SOURCEDATA_DIR = EXPERIMENT_DIR.joinpath('sourcedata')

DERIVATIVES_DIR = EXPERIMENT_DIR.joinpath('derivatives', 'fmriprep-v20.1.0')
FMRIPREP_DIR = DERIVATIVES_DIR.joinpath('fmriprep')
OUT_DIR = DERIVATIVES_DIR.joinpath('deconvolve')
WORK_DIR = EXPERIMENT_DIR.joinpath('tmp')
CONFIGURATIONS_DIR = EXPERIMENT_DIR.joinpath('scripts', 'configurations')
FREESURFER_DIR = Path('/cm/shared/apps/freesurfer/6.0.0/')
TEMPLATEFLOW_DIR = EXPERIMENT_DIR.joinpath('templateflow')

HEURISTIC = CONFIGURATIONS_DIR.joinpath('heuristic.py')

HEUDICONV_CONTAINER = EXPERIMENT_DIR.joinpath('singularity_images', 'heudiconv-v0.6.0.simg')
PREPROCESS_CONTAINER = EXPERIMENT_DIR.joinpath('singularity_images', 'fmriprep-v20.1.0.simg')
POSTPROCESS_CONTAINER = EXPERIMENT_DIR.joinpath('singularity_images', 'fmriprep-v20.0.5.simg')

SPACES = ['T1w', 'MNI152NLin2009cAsym']

COMMANDS_DIR = EXPERIMENT_DIR.joinpath('scripts', 'commands')
LOCAL_DIR = COMMANDS_DIR.joinpath('local')
STUDY_DIR = EXPERIMENT_DIR.joinpath('scripts', 'custom', 'study')

HEUDICONV = LOCAL_DIR.joinpath('heudiconv.py')
ADD_PHASE_ENCODING_DIRECTION = COMMANDS_DIR.joinpath('cli_add_phase_encoding_direction.py')
ADJUST_JSONS = COMMANDS_DIR.joinpath('cli_adjust_jsons.py')
POST_HEUDICONV = STUDY_DIR.joinpath('post_heudiconv.py')
FMRIPREP = LOCAL_DIR.joinpath('fmriprep.py')
GENERATE_DESIGN_MATRIX = COMMANDS_DIR.joinpath('cli_generate_design_matrix.py')
DECONVOLVE_PREP = COMMANDS_DIR.joinpath('cli_deconvolve_prep.py')
POSTPROC_AND_MODEL_ESTIMATION = COMMANDS_DIR.joinpath('cli_postproc_and_model_estimation.py')
SMOOTH_AND_DECONVOLVE = COMMANDS_DIR.joinpath('cli_smooth_and_deconvolve.py')
CALCULATE_TASK_TSNR = COMMANDS_DIR.joinpath('cli_calculate_task_tsnr.py')

PREAMBLE = [
    '#!/bin/bash',
    'module load singularity/2.6.1',
    'module load afni/19.3.18',
    '',
    'set -e',
]
```

For the pipelines I created, pipeline1 converts the dicom files to nifti images, handles some permissions issues, adjusts json files, and creates the events.tsv files for each run from the psychopy csv files. Here are patterns I use in pipeline1.py that is consistent in other pipeline scripts:

* The pipeline scripts call the commands from the `commands` repository or from the `study` folder. These scripts are well tested outside the HPC.
* `cmds` is a list in which each item is a command to be run in the job. The commands are run sequentially starting from the first item in the list.
* I try to run python commmands using any fMRI tools (afni, FSL SPM) through a singularity image. If I do not use a singularity image, the python command runs through my anaconda environment installed in my home directory. My environment has all required python packages installed.
* `--run-local` option will run the pipeline on the local machine and not submit it to the HPC cluster. This is useful for testing pipelines on a local machine.
* `--run-local --testing` options will print the commands to be run at the command line in order. They will not be run.
* `--testing` will write the bash pipeline script to the working directory. I always use `experiment/tmp/pipelines` as the working directory. The qsub command will be printed at the command line, but will not be run, so the pipeline bash script is not submitted to the HPC.
* I use `make_readable_command` function to make commands look readable when they are printed anywhere.

Here is pipeline1.py script using the above patterns:

```python
import os
import json
import random
import string
import textwrap
import subprocess

import pandas as pd

from shlex import split
from pathlib import Path
from datetime import datetime
from argparse import (ArgumentParser, 
                      ArgumentDefaultsHelpFormatter, 
                      RawDescriptionHelpFormatter)

from utils import user_name, make_readable_command

from constants import *

SCRIPT_FILE = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_FILE.parent

# minor heuristic check
linked_heuristic = SCRIPT_DIR.joinpath('heuristic.py')
try:
    os.link(HEURISTIC, linked_heuristic)
except:
    SCRIPT_DIR.joinpath('heuristic.py').unlink()
    os.link(HEURISTIC, linked_heuristic)
    
from heuristic import pm
for key, (record, sm) in pm.items():
    patient_id = key[0]
    acq_date = key[1]
    entries = len(sm)

    if entries != record:
        linked_heuristic.unlink()
        raise Exception(f'Image entries do not match record ({patient_id}, {acq_date}) - ({entries}, {record})')

class CustomFormatter(ArgumentDefaultsHelpFormatter, 
                      RawDescriptionHelpFormatter):
    pass

def get_parser():
    """Define parser object"""

    epilog = textwrap.dedent("""
        These commands are run in this order with hardcoded defaults:
            heudiconv
            adjust_jsons
            post_heudiconv
    """)

    parser = ArgumentParser(description='torque pipeline1', 
                            epilog=epilog, formatter_class=CustomFormatter)

    # REQRUIED
    parser.add_argument('participant', action='store', help='participant names')
    parser.add_argument('session', action='store', help='session name')

    # OPTIONAL TORQUE
    parser.add_argument('--binds', action='store', help='fmriprep path binds',
                        nargs='+')
    parser.add_argument('--run-local', action='store_true', 
                        help='do not submit job, but run it locally')

    parser.add_argument('--email', action='store', default=(user_name() + '@mcw.edu'),
                        help='email address')
    parser.add_argument('--mem', action='store', type=int, default=60,
                        help='qsub memory in gigabytes')
    parser.add_argument('--walltime', action='store', default='48:00:00',
                        help='qsub walltime')
    parser.add_argument('--testing', action='store_true',
                        help='do not run the command, only print command to be run')

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    participant = args.participant
    session = args.session
    binds = args.binds

    email = args.email
    mem = args.mem
    walltime = args.walltime
    testing = args.testing

    dicom_dir_template = SOURCEDATA_DIR.joinpath('sub-{subject}', 
                                                 'ses-{session}',
                                                 'sub-{subject}_ses-{session}.tar.gz')

    if args.run_local: 
        if binds is None:
            print(' * * * WARNING: No binds and running local * * *')

    # check if files exist in bids/.heudiconv/{subject}/ses-{session}
    check_dir = BIDS_DIR.joinpath('.heudiconv', f'{participant}', f'ses-{session}')
    if check_dir.is_dir() and not args.testing:
        raise Exception(f'Directory exists: {check_dir}')
    

    # check participant key in heuristic, this sucks when it is not
    dicominfo = SOURCEDATA_DIR.joinpath(f'sub-{participant}', f'ses-{session}', 'dicominfo.tsv')
    df = pd.read_csv(dicominfo.as_posix(), sep='\t', dtype={'AcquisitionDate': str})
    key = (df.PatientID[0], df.AcquisitionDate[0])

    if key not in pm:
        linked_heuristic.unlink()
        raise Exception(f'{key} not in heuristic')
    linked_heuristic.unlink()

    # do work now
    heudiconv_dir = (f'heudiconv_{participant}_{session}_' + 
                     ''.join(random.choices(string.ascii_letters, k=5)))
    
    work_dir = EXPERIMENT_DIR.joinpath('tmp', heudiconv_dir)
    out_dir = BIDS_DIR.joinpath(f'sub-{participant}', f'ses-{session}')
    cmds = []
    
    heudiconv_cmd = ['singularity run']
    if binds:
        for bind in binds:
            heudiconv_cmd.append(f'-B {bind}')
    
    heudiconv_cmd.extend([
        f'-B {work_dir}:/tmp',
        f'{HEUDICONV_CONTAINER}',
        f'-d {dicom_dir_template}',
        f'-s {participant}',
        f'-ss {session}',
        f'-o {BIDS_DIR}',
        f'-f {HEURISTIC}',
        f'-b notop',
        f'--overwrite',
    ])
    cmds.append(heudiconv_cmd)
    
    cmds.append(f'rm -rf {work_dir}')
    {% raw %}cmds.append(f'find {out_dir} -type d -exec chmod 775 \'{{}}\' \;') {% endraw %}
    {% raw %}cmds.append(f'find {out_dir} -type f -exec chmod 664 \'{{}}\' \;') {% endraw %}

    cmds.append([
        f'python {ADD_PHASE_ENCODING_DIRECTION}',
        f'{BIDS_DIR}',
        f'AP',
        f'PA',
        f'--participants {participant}',
        f'--session {session}',
    ])

    cmds.append([
        f'python {ADJUST_JSONS}',
        f'{BIDS_DIR}',
        f'--participants {participant}',
        f'--session {session}',
        f'--remove-slicetiming',
        f'--match-se-fieldmaps',
    ])
    
    cmds.append([
        f'python {POST_HEUDICONV}',
        f'{BIDS_DIR}',
        f'{SOURCEDATA_DIR}',
        f'{participant}',
        f'{session}',
    ])
    
    if args.run_local:
        for cmd in cmds:
            if args.testing:
                print(make_readable_command(cmd) + '\n')
            else:
                work_dir.mkdir(parents=True, exist_ok=True)
                subprocess.run(split(' '.join(cmd)), check=True)
    else:
        job_name = f'soe_p1_{participant}_{session}'
        pipeline_dir = WORK_DIR.joinpath('pipelines')
        pipeline_dir.mkdir(exist_ok=True)
        job_file = pipeline_dir.joinpath(f'p1_{participant}_{session}.bash')
        log_dir = SCRIPT_DIR.joinpath('qsub_jobs', user_name())
        cmds = [make_readable_command(cmd) + '\n' for cmd in cmds]
        cmds = '\n'.join(PREAMBLE) + '\n\n' + '\n'.join(cmds)
        job_file.write_text(cmds)
    
        torque_cmd = [
            f'qsub -M {email}',
            f'-m abe',
            f'-j oe',
            f'-N {job_name}',
            f'-o {log_dir}',
            f'-V',
            f'-l nodes=1:ppn=1,walltime={walltime},mem={mem}gb',
            f'-q bigmem',
            f'{job_file}'
        ]
    
        if args.testing:
            print('Here is your qsub command:')
            print(make_readable_command(torque_cmd))
        else:
            work_dir.mkdir(parents=True, exist_ok=True)
            log_dir.mkdir(mode=int(0o775), exist_ok=True, parents=True)
    
            results = subprocess.run(split(' '.join(torque_cmd)), 
                                     capture_output=True)
    
            print(results.stdout.decode().strip())
            if results.stderr:
                print(results.stderr.decode().strip())

if __name__ == '__main__':
    main()
```

All the soe pipeline scripts are found here: `/group/jbinder/work/jheffernan/soe/scripts/custom/pipelines`.

## Other tips

* The `-v` qsub option exports a list of variables to the batch job. My previous strategy was to have a pipeline1.py and pipeline1.bash files. The python file would set all the variables and submit them to the bash file as arguments for the pipeline. I prefer creating a script for each job with hard-coded paths so that we can easily rerun the script if need be.


