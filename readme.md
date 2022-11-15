# Choroid plexus segmentation using Gaussian Mixture Models (GMM)

Studies of choroid plexus have recently gained attention. Given its role in CSF production, choroid plexus plays a crucial role in CSF-based clearance systems. Moreover, choroid plexus epithelium is lined with numerous transporters that transport various CSF proteins including Aβ to the blood. T1-weighted MRIs provide a non-invasive imaging technique to study the morphological characteristics of choroid plexus and also enable more advanced functional and perfusion imaging studies. Previous studies have used Freesurfer for automatic choroid plexus segmentation. Here, we present a lightweight algorithm that aims to improve choroid plexus segmentation using Gaussian Mixture Models (GMM). We tested the accuracy of the algorithm against manual segmentations as well as Freesurfer. 

<h4>Citation</h4>
Our paper describing this lightweight algorithm with potential implications for multi-modal neuroimaging studies of choroid plexus in dementia is published. If you use ChP-GMM segmentation, please cite our paper: 

<em> Tadayon, E., Moret, B., Sprugnoli, G., Monti, L., Pascual-Leone, A., Santarnecchi, E. and Alzheimer’s Disease Neuroimaging Initiative, 2020. <b>Improving Choroid Plexus Segmentation in the Healthy and Diseased Brain: Relevance for Tau-PET Imaging in Dementia. Journal of Alzheimer's Disease</b></em>
</b></i>. 
 
<h3>Pipeline</h3>

<img src="./docs/pipeline.png" style="display: block; margin-left: auto; margin-right: auto;width: 50%">

<h3>Comparing GMM and Freesurfer against Manual Segmentation (MS) in 20 subjects of Human Connectome Project (HCP) dataset</h3>
<img src="./docs/performance.png" style="display: block; margin-left: auto; margin-right: auto;width: 50%">
<b>MS<sub>NC</sub>:</b> Manual Segmentation using T1-weighted MRIs with No Contrast<br>
<b>MS<sub>NC1/2</sub>:</b> MS performed by researcher 1 or 2<br>
<b>Dice Coefficient (DC):</b> A metric that calculates spatial similarity between two segmentations

<h3>Choroid plexus segmentation for three representative subjects of HCP dataset using Freesurfer and GMM</h3> 
 <img src="./docs/samples.png" style="display: block; margin-left: auto; margin-right: auto;width: 50%">

<h3> Required packages</h3>

* FSL
* Freesurfer
* Python: nibabel, sklearn, numpy 

<h3> How to run the code</h3>
The current version of the script requires Freesurfer processed files (recon-all) for ventricular segmentation. In future, we aim to add the possibility to use other ventricular segmetnation algorithms to speed up the process. After running recon-all, you can get the choroid plexus segmentation as follows: 

In the terminal:
```bash
python run_gmm_chp_segmentation.py <freesurfer_subjects_dir> <subject_id>
```
The resulting choroid plexus segmentation can be found under `<freesurfer_subjects_dir><subject_id>mri/choroid_susan_segmentation.nii.gz`

<h3>Contact</h3>
For further questions, please email me at <a href="mailto:ehsan.tadayon84@gmail.com">sunny.tadayon@gmail.com</a>. 




