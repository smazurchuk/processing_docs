# Raw data storage model

We need a lab standard for storing raw dicom and nifti files, because it unifies lab imaging analysis procedures. Finding raw files and working with raw data across studies will be easier. The methods section for fMRI preprocessing in published papers will be a copy/paste plus some minor editing. The standard should minimize hard drive usage, because storage costs money. Lab standards just make sense.

## Directory structure overview

Below is an example directory tree for an experiment/study/project named `example`. The top level directory is the experiment name. It has 3 subject data sets: `001` with 2 sessions, `002` with 1 session, and `003` with 1 session. Each session has the following scans: `T1w`, `T2w`, `dwi`, `1 pair of spin echo images`, `2 rest`, and `1 storymath`.

```pre
experiment
|-- bids
|   |-- sub-001
|   |   |-- ses-1
|   |   |   |-- anat
|   |   |   |-- dwi
|   |   |   |-- fmap
|   |   |   `-- func
|   |   `-- ses-2
|   |       |-- anat
|   |       |-- dwi
|   |       |-- fmap
|   |       `-- func
|   |-- sub-002
|   |   `-- ses-1
|   |       |-- anat
|   |       |-- dwi
|   |       |-- fmap
|   |       `-- func
|   `-- sub-003
|       `-- ses-1
|           |-- anat
|           |-- dwi
|           |-- fmap
|           `-- func
|-- hcp
|   |-- 001
|   |   |-- DWI_dir97_RL_01
|   |   |-- DWI_dir97_RL_02
|   |   |-- rfMRI_REST1_RL_01
|   |   |-- rfMRI_REST1_RL_02
|   |   |-- rfMRI_REST2_RL_01
|   |   |-- rfMRI_REST2_RL_02
|   |   |-- SpinEchoFieldMap_LR_01
|   |   |-- SpinEchoFieldMap_LR_02
|   |   |-- SpinEchoFieldMap_RL_01
|   |   |-- SpinEchoFieldMap_RL_02
|   |   |-- T1w_MPR1_01
|   |   |-- T1w_MPR1_02
|   |   |-- T2w_CUBE1_01
|   |   |-- T2w_CUBE1_02
|   |   |-- tfMRI_STORYMATH_RL_01
|   |   `-- tfMRI_STORYMATH_RL_02
|   |-- 002
|   |   |-- DWI_dir97_RL_01
|   |   |-- rfMRI_REST1_RL_01
|   |   |-- rfMRI_REST2_RL_01
|   |   |-- SpinEchoFieldMap_LR_01
|   |   |-- SpinEchoFieldMap_RL_01
|   |   |-- T1w_MPR1_01
|   |   |-- T2w_CUBE1_01
|   |   `-- tfMRI_STORYMATH_RL_01
|   `-- 003
|       |-- DWI_dir97_RL_01
|       |-- rfMRI_REST1_RL_01
|       |-- rfMRI_REST2_RL_01
|       |-- SpinEchoFieldMap_LR_01
|       |-- SpinEchoFieldMap_RL_01
|       |-- T1w_MPR1_01
|       |-- T2w_CUBE1_01
|       `-- tfMRI_STORYMATH_RL_01
`-- sourcedata
    |-- sub-001
    |   |-- ses-1
    |   |   `-- 001s01.tar.gz
    |   `-- ses-2
    |       `-- 001s02.tar.gz
    |-- sub-002
    |   `-- ses-1
    |       `-- 002s01.tar.gz
    `-- sub-003
        `-- ses-1
            `-- 003s01.tar.gz
```

`sourcedata` stores the dicom files for all subjects in `tar.gz` format. `bids` stores the images in nifti format according to the [bids specification](https://bids-specification.readthedocs.io/en/stable/). `hcp` stores the images in nifti format that is compatible with the HCP minimal-preprocessing pipeline. All experiments should have the `sourcedata` and `bids` directories. `hcp` is optional and is likely unneeded. If the `hcp` directory is needed, create the nifti files by hard linking to the nifti files in `bids` directory so we save hard drive space. Many powerful tools are built requiring data in bids format, and we want to be able to use these tools.

## sourcedata

`sourcedata` stores the dicom files for all subjects in `tar.gz` format. There are 2 MRI scanners: the 3T pavilion scanner (located in the Froedtert pavilion) and the premier 3T scanner (located in the CIR). Research scans are nearly always uploaded to the [research XNAT server](https://gwxnat.rcc.mcw.edu/app/template/Login.vm). In the rare case of using clinical imagining data, the files are uploaded to the [clinical XNAT server](https://xnat.mcw.edu/xnat/app/template/Login.vm#!). Both permit downloading full sessions as `tar.gz` files, so do this according to the above tree format. Dicoms should be saved and stored in `tar.gz` format because it reduces the number of files from very many (there is a dicom file for each slice in a MRI scan) and it compresses the storage used by 5-6 times.

If dicoms are saved as `tar.gz` files, how can we identify the scans for the dicom files? The XNAT servers identify each scan under the details for an MR session. A better alternative is the python script `commands/cli_tarred_dicom_info.py`. This script pulls information from the dicom files in the `tar.gz` file and saves it into a tsv file. Here are the tsv file columns and their meanings:

1. **Path**
    * the path to the dicom folder.
2. **TotalFiles**
    * number of dicom files in dicom folder.
3. **AcquisitionDate**
    * the dicom acquisistion date.
4. **Modality**
    * image modality.
5. **StudyDescription**
    * the study description
6. **SeriesDescription**
    * the series description. This field is useful for identifying the dicom scans.
7. **SeriesNumber**
    * the series number. This number is must be unique for a session, which is the `tar.gz` file.
8. **PatientID**
    * the patient ID. This field is usefuld for identifying dicom scans.
9. **MagneticFieldStrength**
    * the magngetic field strength (typically 3).
10. **ReceiveCoilName**
    * the receive coil name (typically 32Ch Head).

## dicom to bids

There are multpile strategies to convert dicom files into bids format. Here are some online resources for dicom to bids conversion: [Andy's Brain Book: BIDS Overview](https://andysbrainbook.readthedocs.io/en/latest/OpenScience/OS/BIDS_Overview.html) and [The Stanford Center for REproducible Neuroscience](http://reproducibility.stanford.edu/bids-tutorial-series-part-1a/).

For my dicom-to-bids conversion, I use [heudiconv](https://github.com/nipy/heudiconv). Heudiconv requires creating a `heuristic.py` file which is a python file coding how to convert and organize the data. Below is a snippet of the `heuristic.py` file I created for the SOE data:

```python
# * * * LEADING COMMENTS * * *

# default values
# : (t1w, {"acq": "mprage"}, "MPRAGE BW=31.2kHz"),
# : (unprocessed_t1w, {"acq": "mprage"}, "ORIG MPRAGE BW=31.2kHz"),
# : (processed_t1w, {"acq": "mprage"}, "Filtered MPRAGE BW=31.2kHz"),
# : (t2w, {"acq": "cube"}, "Cube T2"),
# : (processed_t2w, {"acq": "filtered"}, "Filtered Cube T2"),
# : (fmap, {"dir": "AP"}, "SE Map 1 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 1 PA"),
# : (fmap, {"dir": "AP"}, "SE Map 2 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 2 PA"),
# : (fmap, {"dir": "AP"}, "SE Map 3 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 3 PA"),
# : (soe, {"run": 1, "dir": "AP"}, "MB4-EPI AP run1"),
# : (soe, {"run": 2, "dir": "AP"}, "MB4-EPI AP run2"),
# : (soe, {"run": 3, "dir": "AP"}, "MB4-EPI AP run3"),
# : (soe, {"run": 4, "dir": "AP"}, "MB4-EPI AP run4"),
# : (soe, {"run": 5, "dir": "AP"}, "MB4-EPI AP run5"),
# : (soe, {"run": 6, "dir": "AP"}, "MB4-EPI AP run6"),
# : (soe, {"run": 7, "dir": "AP"}, "MB4-EPI AP run7"),
# : (soe, {"run": 8, "dir": "AP"}, "MB4-EPI AP run8"),},

# ses-2's
# : (t1w, {"acq": "mprage"}, "MPRAGE BW=31.2kHz"),
# : (unprocessed_t1w, {"acq": "mprage"}, "ORIG MPRAGE BW=31.2kHz"),
# : (processed_t1w, {"acq": "mprage"}, "Filtered MPRAGE BW=31.2kHz"),
# : (t2w, {"acq": "cube"}, "Cube T2"),
# : (processed_t2w, {"acq": "filtered"}, "Filtered Cube T2"),
# : (fmap, {"dir": "AP"}, "SE Map 1 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 1 PA"),
# : (fmap, {"dir": "AP"}, "SE Map 2 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 2 PA"),
# : (fmap, {"dir": "AP"}, "SE Map 3 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 3 PA"),
# : (soe, {"run": 9, "dir": "AP"}, "MB4-EPI AP run9"),
# : (soe, {"run": 10, "dir": "AP"}, "MB4-EPI AP run10"),
# : (soe, {"run": 11, "dir": "AP"}, "MB4-EPI AP run11"),
# : (soe, {"run": 12, "dir": "AP"}, "MB4-EPI AP run12"),
# : (soe, {"run": 13, "dir": "AP"}, "MB4-EPI AP run13"),
# : (soe, {"run": 14, "dir": "AP"}, "MB4-EPI AP run14"),
# : (soe, {"run": 15, "dir": "AP"}, "MB4-EPI AP run15"),
# : (soe, {"run": 16, "dir": "AP"}, "MB4-EPI AP run16"),},

# : (t1w, {"acq": "mprage"}, "MPRAGE BW=31.2kHz"),
# : (unprocessed_t1w, {"acq": "mprage"}, "ORIG MPRAGE BW=31.2kHz"),
# : (processed_t1w, {"acq": "mprage"}, "Filtered MPRAGE BW=31.2kHz"),
# : (t2w, {"acq": "cube"}, "Cube T2"),
# : (processed_t2w, {"acq": "filtered"}, "Filtered Cube T2"),
# : (fmap, {"dir": "AP"}, "SE Map 1 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 1 PA"),
# : (fmap, {"dir": "AP"}, "SE Map 2 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 2 PA"),
# : (fmap, {"dir": "AP"}, "SE Map 3 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 3 PA"),
# : (soe, {"run": 9, "dir": "AP"}, "MB4-EPI AP run1"),
# : (soe, {"run": 10, "dir": "AP"}, "MB4-EPI AP run2"),
# : (soe, {"run": 11, "dir": "AP"}, "MB4-EPI AP run3"),
# : (soe, {"run": 12, "dir": "AP"}, "MB4-EPI AP run4"),
# : (soe, {"run": 13, "dir": "AP"}, "MB4-EPI AP run5"),
# : (soe, {"run": 14, "dir": "AP"}, "MB4-EPI AP run6"),
# : (soe, {"run": 15, "dir": "AP"}, "MB4-EPI AP run7"),
# : (soe, {"run": 16, "dir": "AP"}, "MB4-EPI AP run8"),},

# ses-3's
# : (t1w, {"acq": "mprage"}, "MPRAGE BW=31.2kHz"),
# : (unprocessed_t1w, {"acq": "mprage"}, "ORIG MPRAGE BW=31.2kHz"),
# : (processed_t1w, {"acq": "mprage"}, "Filtered MPRAGE BW=31.2kHz"),
# : (t2w, {"acq": "cube"}, "Cube T2"),
# : (processed_t2w, {"acq": "filtered"}, "Filtered Cube T2"),
# : (fmap, {"dir": "AP"}, "SE Map 1 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 1 PA"),
# : (fmap, {"dir": "AP"}, "SE Map 2 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 2 PA"),
# : (fmap, {"dir": "AP"}, "SE Map 3 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 3 PA"),
# : (soe, {"run": 17, "dir": "AP"}, "MB4-EPI AP run17"),
# : (soe, {"run": 18, "dir": "AP"}, "MB4-EPI AP run18"),
# : (soe, {"run": 19, "dir": "AP"}, "MB4-EPI AP run19"),
# : (soe, {"run": 20, "dir": "AP"}, "MB4-EPI AP run20"),
# : (soe, {"run": 21, "dir": "AP"}, "MB4-EPI AP run21"),
# : (soe, {"run": 22, "dir": "AP"}, "MB4-EPI AP run22"),
# : (soe, {"run": 23, "dir": "AP"}, "MB4-EPI AP run23"),
# : (soe, {"run": 24, "dir": "AP"}, "MB4-EPI AP run24"),},

# : (t1w, {"acq": "mprage"}, "MPRAGE BW=31.2kHz"),
# : (unprocessed_t1w, {"acq": "mprage"}, "ORIG MPRAGE BW=31.2kHz"),
# : (processed_t1w, {"acq": "mprage"}, "Filtered MPRAGE BW=31.2kHz"),
# : (t2w, {"acq": "cube"}, "Cube T2"),
# : (processed_t2w, {"acq": "filtered"}, "Filtered Cube T2"),
# : (fmap, {"dir": "AP"}, "SE Map 1 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 1 PA"),
# : (fmap, {"dir": "AP"}, "SE Map 2 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 2 PA"),
# : (fmap, {"dir": "AP"}, "SE Map 3 AP"),
# : (fmap, {"dir": "PA"}, "SE Map 3 PA"),
# : (soe, {"run": 17, "dir": "AP"}, "MB4-EPI AP run1"),
# : (soe, {"run": 18, "dir": "AP"}, "MB4-EPI AP run2"),
# : (soe, {"run": 19, "dir": "AP"}, "MB4-EPI AP run3"),
# : (soe, {"run": 20, "dir": "AP"}, "MB4-EPI AP run4"),
# : (soe, {"run": 21, "dir": "AP"}, "MB4-EPI AP run5"),
# : (soe, {"run": 22, "dir": "AP"}, "MB4-EPI AP run6"),
# : (soe, {"run": 23, "dir": "AP"}, "MB4-EPI AP run7"),
# : (soe, {"run": 24, "dir": "AP"}, "MB4-EPI AP run8"),},

# * * * KEY CREATION * * *

def create_key(template, outtype=("nii.gz",), annotation_classes=None):
    if template is None or not template:
        raise ValueError("Template must be a valid formatg string")
    return template, outtype, annotation_classes

### keyword info ###
# "item" must always be specified if we are using custom keywords; even if it is not used
# session = "ses-{}" (ses is already prefixed and not needed)
# bids_subject_session_prefix = 'sub-%s' % subject + (('_ses-%s' % ses) if ses else '')
# bids_subject_session_dir = 'sub-%s' % subject + (('/ses-%s' % ses) if ses else '')
# order matters with descriptors in task names (acq, run, etc.) 
# I recommend removing .heudiconv in subject folders, because it can cause errors if heudiconv is run again on the same dicom set


def infotodict(seqinfo):
    t1w = create_key("{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_acq-{acq}_T1w")
    t2w = create_key("{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_acq-{acq}_T2w")
    processed_t1w = create_key("{bids_subject_session_dir}/processed_anat/{bids_subject_session_prefix}_acq-{acq}_T1w")
    processed_t2w = create_key("{bids_subject_session_dir}/processed_anat/{bids_subject_session_prefix}_acq-{acq}_T2w")
    unprocessed_t1w = create_key("{bids_subject_session_dir}/unprocessed_anat/{bids_subject_session_prefix}_acq-{acq}_T1w")
    unprocessed_t2w = create_key("{bids_subject_session_dir}/unprocessed_anat/{bids_subject_session_prefix}_acq-{acq}_T2w")

    soe = create_key("{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-soe_dir-{dir}_run-{run}_bold")

    fmap = create_key("{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_dir-{dir}_run-{item}_epi")

    info = {t1w: [], t2w: [],
            processed_t1w: [], processed_t2w: [],
            unprocessed_t1w: [], unprocessed_t2w: [],
            soe: [],
            fmap: [],}

# * * * DICT CREATION * * *

    pm = {
        # ses-1
        ('SOE_101_1_032919', '20190329'): {
            3 : (t1w, {"acq": "mprage"}, "MPRAGE BW=31.2kHz"),
            40003 : (unprocessed_t1w, {"acq": "mprage"}, "ORIG MPRAGE BW=31.2kHz"),
            4 : (t2w, {"acq": "cube"}, "Cube T2"),
            1004 : (processed_t2w, {"acq": "filtered"}, "Filtered Cube T2"),
            5 : (fmap, {"dir": "AP"}, "SE Map 1 AP"),
            6 : (fmap, {"dir": "PA"}, "SE Map 1 PA"),
            11 : (fmap, {"dir": "AP"}, "SE Map 2 AP"),
            12 : (fmap, {"dir": "PA"}, "SE Map 2 PA"),
            17 : (fmap, {"dir": "AP"}, "SE Map 3 AP"),
            18 : (fmap, {"dir": "PA"}, "SE Map 3 PA"),
            7 : (soe, {"run": 1, "dir": "AP"}, "MB4-EPI AP run1"),
            8 : (soe, {"run": 2, "dir": "AP"}, "MB4-EPI AP run2"),
            9 : (soe, {"run": 3, "dir": "AP"}, "MB4-EPI AP run3"),
            10 : (soe, {"run": 4, "dir": "AP"}, "MB4-EPI AP run4"),
            13 : (soe, {"run": 5, "dir": "AP"}, "MB4-EPI AP run5"),
            14 : (soe, {"run": 6, "dir": "AP"}, "MB4-EPI AP run6"),
            15 : (soe, {"run": 7, "dir": "AP"}, "MB4-EPI AP run7"),
            16 : (soe, {"run": 8, "dir": "AP"}, "MB4-EPI AP run8"),},
        # ses-2
        ('SOE_101_2_051619', '20190516'): { # soe101  2      
            2 : (t1w, {"acq": "mprage"}, "MPRAGE BW=31.2kHz"),
            40002 : (unprocessed_t1w, {"acq": "mprage"}, "ORIG MPRAGE BW=31.2kHz"),
            1002 : (processed_t1w, {"acq": "mprage"}, "Filtered MPRAGE BW=31.2kHz"),
            3 : (t2w, {"acq": "cube"}, "Cube T2"),
            1003 : (processed_t2w, {"acq": "filtered"}, "Filtered Cube T2"),
            4 : (fmap, {"dir": "AP"}, "SE Map 1 AP"),
            5 : (fmap, {"dir": "PA"}, "SE Map 1 PA"),
            10 : (fmap, {"dir": "AP"}, "SE Map 2 AP"),
            11 : (fmap, {"dir": "PA"}, "SE Map 2 PA"),
            16 : (fmap, {"dir": "AP"}, "SE Map 3 AP"),
            17 : (fmap, {"dir": "PA"}, "SE Map 3 PA"),
            6 : (soe, {"run": 9, "dir": "AP"}, "MB4-EPI AP run9"),
            7 : (soe, {"run": 10, "dir": "AP"}, "MB4-EPI AP run10"),
            8 : (soe, {"run": 11, "dir": "AP"}, "MB4-EPI AP run11"),
            9 : (soe, {"run": 12, "dir": "AP"}, "MB4-EPI AP run12"),
            12 : (soe, {"run": 13, "dir": "AP"}, "MB4-EPI AP run13"),
            13 : (soe, {"run": 14, "dir": "AP"}, "MB4-EPI AP run14"),
            14 : (soe, {"run": 15, "dir": "AP"}, "MB4-EPI AP run15"),
            15: (soe, {"run": 16, "dir": "AP"}, "MB4-EPI AP run16"),},
        #ses-3
        ('SOE_101_3_061119', '20190611'): { # soe101  3      
            2 : (t1w, {"acq": "mprage"}, "MPRAGE BW=31.2kHz"),
            40002 : (unprocessed_t1w, {"acq": "mprage"}, "ORIG MPRAGE BW=31.2kHz"),
            1002 : (processed_t1w, {"acq": "mprage"}, "Filtered MPRAGE BW=31.2kHz"),
            3 : (t2w, {"acq": "cube"}, "Cube T2"),
            1003 : (processed_t2w, {"acq": "filtered"}, "Filtered Cube T2"),
            4 : (fmap, {"dir": "AP"}, "SE Map 1 AP"),
            5 : (fmap, {"dir": "PA"}, "SE Map 1 PA"),
            10 : (fmap, {"dir": "AP"}, "SE Map 2 AP"),
            11 : (fmap, {"dir": "PA"}, "SE Map 2 PA"),
            16 : (fmap, {"dir": "AP"}, "SE Map 3 AP"),
            17 : (fmap, {"dir": "PA"}, "SE Map 3 PA"),
            6 : (soe, {"run": 17, "dir": "AP"}, "MB4-EPI AP run1"),
            7 : (soe, {"run": 18, "dir": "AP"}, "MB4-EPI AP run2"),
            8 : (soe, {"run": 19, "dir": "AP"}, "MB4-EPI AP run3"),
            9 : (soe, {"run": 20, "dir": "AP"}, "MB4-EPI AP run4"),
            12 : (soe, {"run": 21, "dir": "AP"}, "MB4-EPI AP run5"),
            13 : (soe, {"run": 22, "dir": "AP"}, "MB4-EPI AP run6"),
            14 : (soe, {"run": 23, "dir": "AP"}, "MB4-EPI AP run7"),
            15 : (soe, {"run": 24, "dir": "AP"}, "MB4-EPI AP run8"),},
    }

# * * * FOR LOOP * * *

    for s in seqinfo:
        series_num = int(s.series_id.split('-')[0])
        sm = pm[(s.patient_id, s.date)]

        if series_num in sm:
            sm[series_num][1]["item"] = s.series_id
            info[sm[series_num][0]].append(sm[series_num][1])

    return info
```

The strategy behind my `heuristic.py` file is to explicitly declare all dicom scans and how to name them according to the bids specification for a single experiment. I prefer this strategy, becuase it can handle all edge cases and it fully documents the dicom to nifti file conversions.

My `heursitic.py` file contains 4 sections labeled within the snippet: leading comments, key creation, dict creation, and for loop. Leading comments are comments containing common values for dict creation. In the above example heuristic file, the comments contain comman scans for a single participant in the SOE experiment for all 3 sessions. When a new session for a participant has been completed, the session scans are copied from the comments, pasted into the dict creation section, and the missing values are filled. Key creations creates keys for the info dict. The keys are templates file names for the type of scan and are used as dict keys for info. Dict creation section will likely be the only section edited when a new session is acquired for a participant. The dict `pm` specifies scans for each participant session. In the above example, the keys in pm uniquely identify a participant scanning session. The keys are a 2-tuple with the dicom `PatientID` as first value and `AcquisitionDate` as secon value. The value for the 2-tuple is a dict specifying each dicom scan. The keys are the dicom `SeriesNumber`s. The values are a 3-tuple: (info key, entities and their values for the scan, the dicom `SeriesDescription`). The series description is used only for documentation purporses. The last section is the for loop. It cycles through the scans for a patient session and appends them to the lists in info. Heudiconv converts the dicoms to nifti files and names them according to the information contained in the info dict.

If you do not like how I write my `heuristic.py` file, this [tutorial](http://reproducibility.stanford.edu/bids-tutorial-series-part-2a/) offers a different strategy. Other strategies can be found through a search engine.

# bids to hcp

If you need to use the HCP pipeline, write a script converting the bids folder to the hcp directory structure. When creating the HCP files, hard link (`ln`) to the bids files. Hard linknig saves hard drive space.
