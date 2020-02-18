# Choroid plexus segmentation using Gaussian Mixture Models (GMM)

 Studies of choroid plexus have recently gained momentum, given its role in CSF production as well as CSF clearance. T1-weighted MRIs provide a non-invasive imaging technique to study the morphological characteristics of choroid plexus and also enable more advanced functional and perfusion imaging given their abilitiy to segment choroid plexus accurately. Previous studies have used Freesurfer for automatic choroid plexus segmentation. Here, we present a lightweight algorithm that aims to improve choroid plexus segmentation using Gaussian Mixture Models (GMM). We tested the accuracy of the algorithm against manual segmentations as well as Freesurfer. Our paper describing this lightweight algorithm with potential implications for multi-modal neuroimaging studies in Dementia has been accepted for publication in Journal of Alzheimer's Disease (JAD). 
 
<h2>Pipeline</h2>

<img src="./docs/pipeline.png" style="display: block; margin-left: auto; margin-right: auto;width: 50%">

<h2>Comparing GMM, Freesurfer against Manual Segmentation in 20 subjects of Human Connectome Project (HCP) dataset</h2>

MS<sub>NC</sub>: Manual Segmentation usign T1-weighted MRIs with No Contrast
MS<sub>NC1/2</sub>: MS performed by researcher 1 or 2 
Dice Coefficient (DC): A metric that calculates spatial similarity between two segmentations

<img src="./docs/performance.png" style="display: block; margin-left: auto; margin-right: auto;width: 50%">

<h2>Choroid plexus segmentation for three representative subjects of HCP dataset using Freesurfer and GMM</h2> 
 
<img src="./docs/samples.png" style="display: block; margin-left: auto; margin-right: auto;width: 50%">





