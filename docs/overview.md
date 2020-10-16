# Overview of Pipelines

## Epilepsy

This description largely follows from `bids_pipeline_v2.doc` ([here](https://mcw0-my.sharepoint.com/:w:/g/personal/jheffernan_mcw_edu/EUQ6onemS01MjpNDi_THa5kBTwgdJd9kHdIN6G4ZXet9uA?e=4%3amb3UHK&at=9)). This analysis pipeline assumes the data starts as tarred and gzipped (`tar.gz`) dicom files. Note, most referenced scripts can be found under the scripts heading in the side-bar. Preprocessing this data involves:

1. Generating a `.tsv` file describing the different scans in the dicom file. This is done by the function
`run_tarred_dicom_info.py`.
    * This script ends up calling `cli_tarred_dicom_info.py` which processes the input files. This script uses pydicom to load dicom files and then extracts information from the header.  <p>&nbsp;</p>

2. Generating all the dicom information needed for the conversion from dicom to `.nii` files and the other info that will be fed into `heudiconv.py`
    * This is done by `dicom_Info.R` <p>&nbsp;</p>

3. Running `run_heudiconv.py`. I don't really know what this script does ...
    * It requires being run on the bigmem queue on the RCC
    * Goes on to call `singularity_heudiconv.bash` which runs the actual analysis <p>&nbsp;</p>

4. Running `cli_adjust_jsons.py`. I think this is the step that removes slice timing. Not sure why? 
    * This removes slice timings and matches se-fieldmaps <p>&nbsp;</p>
  
5. Running `cli_post_heudiconc.py`. This updates the `scans.tsv` file associated with each participant/session
    * This is needed for deconvolve <p>&nbsp;</p>

6. Running `run_fmriprep_epilepsy.py` which runs fmriprep on the subject

### Understanding the Output

## SOE AFNI

This analysis is specific to the processing of the SOE data. It begins with the script `soe_dimon.py` written by Leo.

```shell
Written for Python 2.7 and AFNI 18.0 or higher
Usage: python soe_dimon.py [subjID] [session]
ex.: python soe_dimon.py 103 1
 Leo Fernandino
05/07/19
```
Following this, there is a script by that copies the files after which the following proc.py command is used to pre-process the data[^1]

```bash
afni_proc.py -subj_id SOE_${subj}_${sesh}_SEmap${SEn}                   \
        -dsets $dsets                                                   \
        -copy_anat SOE_${subj}_T1w_acpc_dc_restore_brain_1mm+orig       \
        -blip_forward_dset SOE${subj}_SEmap${SEn}_AP.nii.gz             \
        -blip_reverse_dset SOE${subj}_SEmap${SEn}_PA.nii.gz             \
        -blocks despike tshift align tlrc volreg blur mask scale        \
	    -tlrc_base MNI152_T1_2009c+tlrc				                	\
        -volreg_align_e2a   						                    \
	    -volreg_tlrc_warp						                        \
	    -blur_size 4.0							                        \
        -anat_has_skull no                                              \
        -align_opts_aea -giant_move -resample off                       \
	    -align_epi_strip_method 3dSkullStrip
```

Following this, the findal outputs have a name like `blip`. These can then be copied into a directory. The next step is to create the 3d deconvolve file. This is done by creating the necessary 1d files. Proc py produces the nuissance regressors. The ones we are interested in are 3d


This analysis stream assumes that we start from nifti files organized like the RCC. Further, we will use a script that does not use MNI space


#### Proc.py Options
```shell
subj_id: file prefix
dsets: functional run files
copy_anat: makes copy of anat file
blip_forward_dset: AP SEmap
blip_reverse_dset: PA Semap
tcat_remove_first_trs: remove first x time points

blocks: indicate which default and optional blocks to run
despike: lowers all extreme values
tshift: align voxels w/in volumes
volreg: motion correction, registration to 3rd volume by default
align: alignment to {space}
mask: create a subject anatomy mask
scale: scale each voxel to mean of 100, clip values at 200

blip_opts_qw: set options for qwarp
volreg_align_e2a: align EPI to anatomy
align_epi_strip_method: default is 3dAutomask, set to 3dSkullstrip
```

