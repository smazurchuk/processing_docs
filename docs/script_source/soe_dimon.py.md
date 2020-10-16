```python 
#!/cm/shared/apps/python/2.7.11/bin/python

'''
SOE320 fMRI project
Calls AFNI's Dimon to convert dicom images into nifti files and organizes
the files into folders for preprocessing.
Runs in RCC's Carley cluster or in local machine, see setting below.
NOTE: the directory tree structure of the session varies depending on how it was
downloaded from XNAT.

Written for Python 2.7 and AFNI 18.0 or higher
Usage: python soe_dimon.py [subjID] [session]
ex.: python soe_dimon.py 103 1
 Leo Fernandino
05/07/19
'''
#-----------------------------------------
# Running locally or on an RCC machine/cluster?
# Locally:
#afnipath = '/home/lfernandino/abin/'
#afnipath = '/Users/jedidiahmathis/abin'
# RCC:
afnipath = 'module load "afni/18.0.00";'
#-----------------------------------------

import os
import sys
import glob
import shutil

## Read in the command line input for subject ID and session number
subj = sys.argv[1]
#subj = '105'
session = sys.argv[2]
#session = '1'

# Set paths
studypath = '/rcc/stor1/depts/neurology/projects/SOE320/Raw_MRI_data/'
# fill in the date digits in the folder name
sessionpath = glob.glob(studypath + 'SOE_' + subj + '_' + session + '_*')[0]
dicompath = os.path.join(sessionpath, 'dicom')
outpath = os.path.join(sessionpath, 'nifti')
anatHCPpath = os.path.join('/rcc/stor1/depts/neurology/projects/SOE320/Anat_surfaces', 'SOE'+subj, 'unprocessed')

print ''
print 'Running soe_dimon.py for subject ' + subj + ' session ' + session + '...'
print ''

# directory tree structure depends on how the session was downloaded from XNAT
if os.path.isdir(os.path.join(sessionpath, 'scans')):
    datapath = os.path.join(sessionpath, 'scans')
else:
    datapath = sessionpath

# Create destination folders if they don't already exist
if not os.path.isdir(dicompath):
    os.mkdir(dicompath)
if not os.path.isdir(outpath):
    os.mkdir(outpath)
if not os.path.exists(anatHCPpath):
    os.makedirs(anatHCPpath)

# Change into the directory containing the scans
os.chdir(datapath)

# Replace any spaces in the run directory names with underscores
rm_spaces = 'find '+ datapath + ' -depth -maxdepth 1 -name \'* *\' -execdir bash -c \'mv -- "$1" "${1// /_}"\' bash {} \;'
os.system(rm_spaces)
# Replace any dashes in the run directory names with underscores
rm_dashes = 'find '+ datapath + ' -depth -maxdepth 1 -name \'*-*\' -execdir bash -c \'mv -- "$1" "${1//-/_}"\' bash {} \;'
os.system(rm_dashes)

# Move dicom folders into dicompath
for file in glob.glob(datapath + '/*'):
    if file != dicompath and file != outpath:
        shutil.move(file, dicompath)

# List dicom directories containing anatomical scans for this subject
mpragelist = filter(os.path.isdir, glob.glob(os.path.join(dicompath, '*_MPRAGE_BW*')))
print str(len(mpragelist)) + ' dicom MPRAGE found'
cubet2list = filter(os.path.isdir, glob.glob(os.path.join(dicompath, '*_CubeT2')))
print str(len(cubet2list)) + ' dicom CubeT2 found'

# For each MPRAGE in this session
for mpragepath in mpragelist:
    if mpragepath.split('/')[-1].split('_')[1] == 'MPRAGE':
        anatname = 'T1w_MPR' + session
    #elif mpragepath.split('/')[-1].split('_')[1] == 'FL':
        #anatname = 'T1w_MPR' + session
    elif mpragepath.split('/')[-1].split('_')[1] == 'ORIG':
        anatname = 'ORIG_MPRAGE'
    else:
        print ('')
        print('***WARNING: MPRAGE folder name does not match any expected pattern! Using output "mprage"')
        anatname = 'mprage'
    if os.path.isfile(os.path.join(outpath, 'SOE'+ subj + '_' + anatname + '.nii.gz')):
        print ''
        print '***WARNING: A nifti file for ' + anatname + ' already exists for SOE'+ subj
        print 'Skipping ' + anatname
        print ''
    else:
        # Convert dicom images into a nifti file and move it to the nifti folder
        print ''
        print 'Calling AFNI "dimon" to generate nifti file:'
        filename = 'SOE'+ subj + '_' + anatname + '.nii.gz'
        # directory tree depends on how the data was downloaded from XNAT...
        if os.path.isdir(os.path.join(mpragepath, 'resources')) :
            dimon_call = afnipath + 'Dimon -infile_pattern ' + mpragepath + '/resources/DICOM/files/"*.dcm" -gert_create_dataset -dicom_org -gert_to3d_prefix ' + filename
        else:
            dimon_call = afnipath + 'Dimon -infile_pattern ' + mpragepath + '/DICOM/"*.dcm" -gert_create_dataset -dicom_org -gert_to3d_prefix ' + filename
        print dimon_call
        os.system(dimon_call)
        # Copy the T1w_MPR file to the source folder for the HCP anat pipeline
        if anatname == 'T1w_MPR' + session:
            shutil.copy(filename, anatHCPpath)
        shutil.move(filename, outpath)

# For each CubeT2 in this session
for CubeT2path in cubet2list:
    if CubeT2path.split('/')[-1].split('_')[1] == 'CubeT2':
        anatname = 'CubeT2_unfiltered'
    elif CubeT2path.split('/')[-1].split('_')[1] == 'Filtered':
        anatname = 'T2w_CUBE' + session
    else:
        print ('')
        print('***WARNING: CubeT2 folder name does not match any expected pattern! Using "cubeT2"')
        print ('')
        anatname = 'cubeT2'
    if os.path.isfile(os.path.join(outpath, 'SOE'+ subj + '_' + anatname + '.nii.gz')):
        print ''
        print '***WARNING: A nifti file for ' + anatname + ' already exists for SOE' + subj
        print 'Skipping ' + anatname
        print ''
    else:
        # Convert dicom images into a nifti file and move it to the nifti folder
        print ''
        print 'Calling AFNI "dimon" to generate nifti file:'
        filename = 'SOE'+ subj + '_' + anatname + '.nii.gz'
        # directory tree depends on how the data was downloaded from XNAT...
        if os.path.isdir(os.path.join(CubeT2path, 'resources')) :
            dimon_call = afnipath + 'Dimon -infile_pattern ' + CubeT2path + '/resources/DICOM/files/"*.dcm" -gert_create_dataset -dicom_org -gert_to3d_prefix ' + filename
        else:
            dimon_call = afnipath + 'Dimon -infile_pattern ' + CubeT2path + '/DICOM/"*.dcm" -gert_create_dataset -dicom_org -gert_to3d_prefix ' + filename
        print dimon_call
        os.system(dimon_call)
        # Copy the T2w_CUBE file to the source folder for the HCP anat pipeline
        if anatname == 'T2w_CUBE' + session:
            shutil.copy(filename, anatHCPpath)
        shutil.move(filename, outpath)

# List dicom directories containing spin echo maps for this subject
semapslist = filter(os.path.isdir, glob.glob(os.path.join(dicompath, '*_SE_Map_*')))
print str(len(semapslist)) + ' dicom SE maps found'

# For each SE map in this session, grab the map name and use it in the outfile name
for mappath in semapslist:
    mapname = mappath.split('/')[-1].split('_')[-2] + '_' + mappath.split('/')[-1].split('_')[-1]
    if os.path.isfile(os.path.join(outpath, 'SOE'+ subj + '_SEmap' + mapname + '.nii.gz')):
        print ''
        print '***WARNING: A nifti file for SEmap' + mapname + ' already exists for SOE' + subj
        print 'Skipping SEmap' + mapname
        print ''
    else:
        # Convert dicom images into a nifti file and move it to the nifti folder
        print ''
        print 'Calling AFNI "dimon" to generate nifti file:'
        filename = 'SOE'+ subj + '_SEmap' + mapname + '.nii.gz'
        # directory tree depends on how the data was downloaded from XNAT...
        if os.path.isdir(os.path.join(mappath, 'resources')) :
            dimon_call = afnipath + 'Dimon -infile_pattern ' + mappath + '/resources/DICOM/files/"*.dcm" -gert_create_dataset -dicom_org -gert_to3d_prefix ' + filename
        else:
            dimon_call = afnipath + 'Dimon -infile_pattern ' + mappath + '/DICOM/"*.dcm" -gert_create_dataset -dicom_org -gert_to3d_prefix ' + filename
        print dimon_call
        os.system(dimon_call)
        shutil.move(filename, outpath)

print ''
print '**************************************************'
print 'Converting dicom to nifti for functional runs'
print '**************************************************'
print ''

# List dicom directories containing functional runs for this subject
runlist = filter(os.path.isdir, glob.glob(os.path.join(dicompath, '*_MB4*EPI_*')))
print str(len(runlist)) + ' dicom functional runs found'

# For each run in this session, grab the run number and include it (as double digits) in the outfile name
for runpath in runlist:
    run = runpath.split('/')[-1].split('_')[-1].split('run')[-1]
    runnumber = run.zfill(2)
    if os.path.isfile(os.path.join(outpath, 'SOE'+ subj + '_run' + runnumber + '.nii.gz')):
        print ''
        print '***WARNING: A nifti file for run' + runnumber + ' already exists for SOE' + subj
        print 'Skipping run' + runnumber
        print ''
    else:
        # Convert dicom images into a nifti file and move it to the nifti folder
        # Using 'dimon'
        print ''
        print 'Calling AFNI "dimon" to generate nifti file:'
        filename = 'SOE'+ subj + '_run' + runnumber + '.nii.gz'
        # directory tree depends on how the data was downloaded from XNAT...
        if os.path.isdir(os.path.join(runpath, 'resources')) :
            dimon_call = afnipath + 'Dimon -infile_pattern ' + runpath + '/resources/DICOM/files/"*.dcm" -gert_create_dataset -dicom_org -gert_to3d_prefix ' + filename
        else:
            dimon_call = afnipath + 'Dimon -infile_pattern ' + runpath + '/DICOM/"*.dcm" -gert_create_dataset -dicom_org -gert_to3d_prefix ' + filename
        print dimon_call
        os.system(dimon_call)
        shutil.move(filename, outpath)

os.system('rm -f dimon.files.run.* GERT_Reco_dicom_*')

# If 'scans' folder exists but is now empty (as it should), delete it
if os.path.isdir(os.path.join(sessionpath, 'scans')):
    if not os.listdir(os.path.join(sessionpath, 'scans')) :
        print 'Removing empty folder "scans"'
        os.rmdir(os.path.join(sessionpath, 'scans'))
    else:
        print ''
        print '**WARNING: Folder "scans" is not empty!'

print ''
print 'Script "soe_dimon.py" finished for SOE' + subj + ' session ' + session
print ''
 

```