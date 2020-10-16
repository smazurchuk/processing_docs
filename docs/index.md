---
extra: smazurchuk generated this on 9/24/20
date: 2020-09-24
---

# Welcome to LIL Processing Docs

This documents the labs fmri-prep pipeline (as developed by Joe Heffernan). As documented here, this is the pipeline that is **specific to the clinical epilepsy project**. As such many of the scripts here are study specific.

### Script Overview
This is a list of the relevant scripts. For a more detailed outline, see [Overview](overview.md)

Pre-processing

* `run_tarred_dicom_info.py` - creates a tsv file with dicom info
* `dicom_info.R` - gets info from tsv file
* `run_heudiconv.py` - convert dicoms to nifti
* `cli_adjust_jsons.py` - check field maps
* `cli_post_heudiconv.py` - update tsv file
* `run_fmriprep_epilepsy.py` - run fmriprep on subject

GLM

* `generate_eprime_config.py` - creates json file for each task
* `generate_events.py` - 
* `generate_design_matrix.py`
* `run_deconvolve_prep.py`
* `run_postproc_and_model_estimation.py`

Post GLM

* `post_analysis.py`
* `run_calculate_task_tsnr.py`
* `deconvolve_link.py`
* `PlotSingleParticipantMotion.R`



### General Notes

Within the language lab, there are 3 general pipelines used:
1. fmri-prep for clnical epilepsy data
   * The surfaces that are output here are *freesurfer* and hpc surfaces
2. HCP pipline for SOE data
3. AFNI-centric processing
   * Similar to using `afni_proc.py`, a lot of the SOE data is processed using afni-centric scripts



