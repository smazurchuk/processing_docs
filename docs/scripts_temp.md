# Script References 

This gives some details of the scripts and prints the help if it exists 

!!! Note 
    This directory was generated on 2020-09-25 by smazurchuk 


## `run_tarred_dicom_info.py` 
 
[Source](/script_source/run_tarred_dicom_info.py) 	 
Help Output: 

```bash
usage: run_tarred_dicom_info.py [-h] --in_files IN_FILES [IN_FILES ...]
                                [--email EMAIL] [--mem MEM]
                                [--walltime WALLTIME] [--testing]

Get dicom information from tar.gz file.

optional arguments:
  -h, --help            show this help message and exit
  --in_files IN_FILES [IN_FILES ...]
                        the tar.gz files (default: None)
  --email EMAIL         email address (default: smazurchuk@mcw.edu)
  --mem MEM             qsub memory in gigabytes (default: 10)
  --walltime WALLTIME   qsub walltime (default: 00:30:00)
  --testing             do not run the command, only print information
                        (default: False)
``` 
---
## `dicom_info.R` 
 
[Source](/script_source/dicom_info.R) 	 
Help Output: 

## `run_heudiconv.py` 
 
[Source](/script_source/run_heudiconv.py) 	 
Help Output: 

```bash
usage: run_heudiconv.py [-h] --participants PARTICIPANTS [PARTICIPANTS ...]
                        [--sessions SESSIONS [SESSIONS ...]] [--email EMAIL]
                        [--mem MEM] [--walltime WALLTIME] [--testing]
                        experiment_dir heuristic

Run heudiconv to extract tar.gz to bids.

positional arguments:
  experiment_dir        the bids directory
  heuristic             heuristic file

optional arguments:
  -h, --help            show this help message and exit
  --participants PARTICIPANTS [PARTICIPANTS ...]
                        participant names (default: None)
  --sessions SESSIONS [SESSIONS ...]
                        sessions (default: None)
  --email EMAIL         email address (default: smazurchuk@mcw.edu)
  --mem MEM             qsub memory in gigabytes (default: 20)
  --walltime WALLTIME   qsub walltime (default: 7:00:00)
  --testing             do not run the command, only print information
                        (default: False)
``` 
---
## `cli_adjust_jsons.py` 
 
[Source](/script_source/cli_adjust_jsons.py) 	 
Help Output: 

```bash
usage: cli_adjust_jsons.py [-h]
                           [--participants PARTICIPANTS [PARTICIPANTS ...]]
                           [--hyperband HYPERBAND] [--tr TR]
                           [--slicetiming SLICETIMING [SLICETIMING ...] |
                           --remove-slicetiming] [--match-se-fieldmaps]
                           bids_dir

Corrects json files in bids format

positional arguments:
  bids_dir              the bids directory

optional arguments:
  -h, --help            show this help message and exit
  --participants PARTICIPANTS [PARTICIPANTS ...]
                        participants to correct. All sessions are corrected.
                        If not specified, all participants in bids_dir will be
                        corrected

func:
  func options

  --hyperband HYPERBAND
                        the hyperband factor
  --tr TR               repetition time
  --slicetiming SLICETIMING [SLICETIMING ...]
                        the time at which slices are acquired in a single fMRI
                        brain scan. These value must be less than the TR.
  --remove-slicetiming  remove SliceTiming field

fmap:
  fmap options

  --match-se-fieldmaps  Match field maps together and fill IntendedFor field
                        for spin-echo field map json files

func+fmap:
  func+fmap options
``` 
---
## `cli_post_heudiconv.py` 
 
[Source](/script_source/cli_post_heudiconv.py) 	 
Help Output: 

```bash
usage: cli_post_heudiconv.py [-h] --participants PARTICIPANTS
                             [PARTICIPANTS ...]
                             bids_dir

Adjusts scans.tsv after heudiconv completeion

positional arguments:
  bids_dir              the bids directory

optional arguments:
  -h, --help            show this help message and exit
  --participants PARTICIPANTS [PARTICIPANTS ...]
                        participants to correct. All sessions are corrected.
                        If not specified, all participants in bids_dir will be
                        corrected
``` 
---
## `run_fmriprep_epilepsy.py` 
 
[Source](/script_source/run_fmriprep_epilepsy.py) 	 
Help Output: 

```bash
usage: run_fmriprep_epilepsy.py [-h] [--nthreads NTHREADS]
                                [--omp-nthreads OMP_NTHREADS] [--email EMAIL]
                                [--mem MEM] [--walltime WALLTIME] [--testing]
                                participants [participants ...]

Run fmriprep for epilepsy dataset.

positional arguments:
  participants          bids participant names

optional arguments:
  -h, --help            show this help message and exit
  --nthreads NTHREADS   maximum number of threads across all processes
                        (default: 16)
  --omp-nthreads OMP_NTHREADS
                        maximum number of threads per-process (default: 8)
  --email EMAIL         email address (default: smazurchuk@mcw.edu)
  --mem MEM             qsub memory in gigabytes (default: 200)
  --walltime WALLTIME   qsub walltime (default: 48:00:00)
  --testing             do not run the command, only print information
                        (default: False)
``` 
---
## `soe_dimon.py` 
 
[Source](/script_source/soe_dimon.py) 	 
Help Output: 

