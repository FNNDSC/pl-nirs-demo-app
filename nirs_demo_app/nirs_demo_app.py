#                                                            _
# nirs_demo_app ds app
#
# (c) 2016 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import os
import json
import numpy as np
import nibabel as nib
from pymcx import MCX
from chrisapp.base import ChrisApp

default_mcx = {
    'autopilot': True,
    'gpuid': 1,
    'nphoton': 1e8,
    'tstart': 0,
    'tend': 5e-9,
    'tstep': 1e-10,
    'issrcfrom0': True
}


class Nirs_demo_app(ChrisApp):
    """
    An app to demo nirs mcx simulations..
    """
    AUTHORS         = 'FNNDSC (jacob.tatz@childrens.harvard.edu)'
    SELFPATH        = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC        = os.path.basename(__file__)
    EXECSHELL       = 'python3'
    TITLE           = 'Nirs Demo App'
    CATEGORY        = ''
    TYPE            = 'ds'
    DESCRIPTION     = 'An app to demo nirs mcx simulations.'
    DOCUMENTATION   = 'http://wiki'
    VERSION         = '0.1'
    LICENSE         = 'Opensource (MIT)'
    MAX_NUMBER_OF_WORKERS = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS = 1  # Override with integer value
    MAX_CPU_LIMIT         = '' # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT         = '' # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT      = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT      = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT         = 1  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT         = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

    # Fill out this with key-value output descriptive info (such as an output file path
    # relative to the output dir) that you want to save to the output meta file when
    # called with the --saveoutputmeta flag
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        """
        self.add_argument(
            '--head',
            dest        = 'head',
            type        = str,
            optional    = False,
            help        = 'Path to NIFTI file containg the head'
        )

        self.add_argument(
            '--mcx-config',
            dest        = 'mcx_config',
            type        = str,
            optional    = False,
            help        = 'Path to json file for mcx coniguration'
        )

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        # Load params
        with open(os.path.join(options.inputdir, options.mcx_config)) as jf:
            config = json.load(jf)
        nifti = nib.load(os.path.join(options.inputdir, options.head))
        unitinmm, uy, uz = nifti.header.get_zooms()[:3]
        # assert unitinmm == uy == uz, "voxels must be cubes"
        # Prepare simulations
        cfg = MCX(**{**default_mcx, **config["mcx"]})
        cfg.vol = nifti.get_data()
        cfg.unitinmm = unitinmm
        # Run simulations
        cfg.srcpos = config['srcpos']
        cfg.srcdir = config['srcdir']
        src_fluence = cfg.run(1)["fluence"].sum(axis=3)
        cfg.srcpos = config['detpos']
        cfg.srcdir = config['detdir']
        det_fluence = cfg.run(1)["fluence"].sum(axis=3)
        banana_fluence = src_fluence*det_fluence
        # Save Results
        nib.save(nib.Nifti1Image(src_fluence, None, nifti.header),
                 os.path.join(options.outputdir, "src.nii.gz"))
        nib.save(nib.Nifti1Image(np.log(src_fluence), None, nifti.header),
                 os.path.join(options.outputdir, "logsrc.nii.gz"))

        nib.save(nib.Nifti1Image(det_fluence, None, nifti.header),
                 os.path.join(options.outputdir, "det.nii.gz"))
        nib.save(nib.Nifti1Image(np.log(det_fluence), None, nifti.header),
                 os.path.join(options.outputdir, "logdet.nii.gz"))

        nib.save(nib.Nifti1Image(banana_fluence, None, nifti.header),
                 os.path.join(options.outputdir, "banana.nii.gz"))
        nib.save(nib.Nifti1Image(np.log(banana_fluence), None, nifti.header),
                 os.path.join(options.outputdir, "logbanana.nii.gz"))

        nib.save(nifti, os.path.join(options.outputdir, "anatomical.nii.gz"))


# ENTRYPOINT
if __name__ == "__main__":
    app = Nirs_demo_app()
    app.launch()
