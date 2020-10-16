#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 14:49:14 2020
hello 
This is just to autogenerate documentation for Joe's scripts

Notes:
    * I dont deal with the fact that there is one R script. It is colored as python
    
    
@author: smazurchuk
"""
import os
import subprocess as sp
from datetime import datetime

base_dir = '/rcc/stor1/depts/neurology/projects/Epilepsy/clinical'
script_dir = [f'{base_dir}/scripts/commands/torque/run_tarred_dicom_info.py',
              f'{base_dir}/sourcedata/dicom_info.R',
              f'{base_dir}/scripts/commands/torque/run_heudiconv.py',
              f'{base_dir}/scripts/commands/cli_adjust_jsons.py',
              f'{base_dir}/scripts/commands/cli_post_heudiconv.py',
              f'{base_dir}/scripts/torque_study_specific/run_fmriprep_epilepsy.py',
              '/rcc/stor1/depts/neurology/projects/SOE320/Scripts/soe_dimon.py']

funcs = [k.split('/')[-1] for k in script_dir]
func_helps = [sp.run(f'python {script} -h', capture_output=True, shell=True).stdout.decode('utf-8') for script in script_dir]
func_source = [sp.run(f'cat {script}', capture_output=True, shell=True).stdout.decode('utf-8') for script in script_dir]


outf=[]; outf.append(f'# Script References \n\nThis gives some details of the scripts and prints the help if it exists \n\n!!! Note \n    This directory was generated on {datetime.today().strftime("%Y-%m-%d")} by smazurchuk \n\n\n')
if not os.path.isdir('docs/script_source'):
    os.mkdir('docs/script_source')
for i, func in enumerate(funcs):
    outf.append(f'## `{func}` \n \n[Source](/script_source/{func}) \t \nHelp Output: \n\n')
    if func_helps[i]:
        outf.append(f'```bash\n{func_helps[i]}``` \n---\n')
    with open(f'docs/script_source/{func}.md', 'w') as f:
        f.write(f'```python \n{func_source[i]} \n\n```')

with open('docs/scripts_temp.md', 'w') as f:
    f.writelines(outf)


