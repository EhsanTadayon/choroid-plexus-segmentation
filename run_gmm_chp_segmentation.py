import numpy as np
import nibabel as nib
from sklearn.mixture import GaussianMixture,BayesianGaussianMixture
import sys
import subprocess

### parameters

subjects_dir= sys.argv[1]

subj = sys.argv[2]




### functions

def run_cmd(cmd):
    print cmd
    out,err = unix_cmd(cmd)
    print out
    show_error(err)
    return out,err
    
def save_segmentation(clf,out_name):
    new_img = np.zeros((256,256,256))

    #choroid_ind = np.where(np.mean(clf.means_)==np.max(clf.means_))

    if np.mean(mask_T1_vals[clf.predict(X)==1]) > np.mean(mask_T1_vals[clf.predict(X)==0]): 
    
        choroid_ind = np.where(clf.predict(X)==1)[0]
    else: 

        choroid_ind = np.where(clf.predict(X)==0)[0]

    choroid_coords = (mask_indices[0][choroid_ind], mask_indices[1][choroid_ind], mask_indices[2][choroid_ind])
    new_img[choroid_coords] = 1
    imgObj = nib.Nifti1Image(new_img,maskObj.affine)
    nib.save(imgObj,'{subjects_dir}/{subj}/mri/{out_name}'.format(subjects_dir=subjects_dir,
                                                                                subj=subj,
                                                                                out_name=out_name))


def susan(input_img): 
    input_img = input_img.split('.nii')[0]
    cmd='susan {input_img}.nii.gz 1 1 3 1 0 {input_img}_susan.nii.gz'.format(input_img = input_img)
    out,err = run_cmd(cmd)
    
## functions for running unix cmd
# unix command
def unix_cmd(cmd):
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    out,err=p.communicate()
    return out,err

def show_error(err):
    if len(err) > 0: 
        print(err)
        
   


# reading the T1 volume under freesurfer

T1 = nib.load('{subjects_dir}/{subj}/mri/T1.mgz'.format(subjects_dir=subjects_dir,subj=subj)).get_data()



# creating a mask for both ventricles and choroid plexus: 
print 'Creating masks: choroid+ventricle.mgz and aseg_choroid.mgz'

cmd = 'mri_binarize --i {subjects_dir}/{subj}/mri/aseg.mgz --match 31 63  --o {subjects_dir}/{subj}/mri/aseg_choroid_mask.nii.gz'
cmd = cmd.format(subjects_dir=subjects_dir, subj=subj)
run_cmd(cmd)


cmd = 'mri_binarize --i {subjects_dir}/{subj}/mri/aseg.mgz --match 4 5 31  --o {subjects_dir}/{subj}/mri/lh_choroid+ventricle_mask.nii.gz'
cmd = cmd.format(subjects_dir=subjects_dir, subj=subj)
run_cmd(cmd)

cmd = 'mri_binarize --i {subjects_dir}/{subj}/mri/aseg.mgz --match 43 44 63  --o {subjects_dir}/{subj}/mri/rh_choroid+ventricle_mask.nii.gz'
cmd = cmd.format(subjects_dir=subjects_dir, subj=subj)
run_cmd(cmd)


### left hemisphere (lh)
# get the intensity values for the mask:

print 'getting intensity values for the mask ....'

maskObj = nib.load('{subjects_dir}/{subj}/mri/lh_choroid+ventricle_mask.nii.gz'.format(subjects_dir=subjects_dir,
                                                                        subj=subj))
mask = maskObj.get_data()
mask_indices = np.where(mask==1)
mask_indices_array = np.array(mask_indices)
mask_T1_vals = T1[mask_indices]


X = np.reshape(mask_T1_vals,(-1,1))
gmmb = BayesianGaussianMixture(n_components=2, covariance_type='full').fit(X)

save_segmentation(gmmb,'lh_choroid_gmmb_mask.nii.gz')


## susan 
input_img = '{subjects_dir}/{subj}/mri/lh_choroid_gmmb_mask.nii.gz'.format(subjects_dir=subjects_dir,subj=subj)
susan(input_img)

## read choroid_gmmb_mask_susan.nii.gz
choroid_gmmb_mask = nib.load('{subjects_dir}/{subj}/mri/lh_choroid_gmmb_mask.nii.gz'.format(subjects_dir=subjects_dir, subj=subj))
choroid_gmmb_mask_ = choroid_gmmb_mask.get_data()
choroid_gmmb_susan = nib.load('{subjects_dir}/{subj}/mri/lh_choroid_gmmb_mask_susan.nii.gz'.format(subjects_dir=subjects_dir, subj=subj)).get_data()
choroid_gmmb_mask_ind = np.where(choroid_gmmb_mask_==1)
susan_vals = choroid_gmmb_susan[choroid_gmmb_mask_ind]

susan_gmmb = BayesianGaussianMixture(n_components=3).fit(np.reshape(susan_vals,(-1,1)))
susan_gmmb_predict = susan_gmmb.predict(np.reshape(susan_vals,(-1,1)))

m = susan_gmmb.means_.flatten()
choroid_ind = np.where(m==np.max(m))[0][0]
choroid_susan_seg = np.zeros(choroid_gmmb_mask_.shape)
choroid_susan_seg[(choroid_gmmb_mask_ind[0][susan_gmmb_predict==choroid_ind],choroid_gmmb_mask_ind[1][susan_gmmb_predict==choroid_ind], choroid_gmmb_mask_ind[2][susan_gmmb_predict==choroid_ind])]= 1

choroid_susan_segObj = nib.Nifti1Image(choroid_susan_seg,choroid_gmmb_mask.affine)
nib.save(choroid_susan_segObj,'{subjects_dir}/{subj}/mri/lh_choroid_susan_segmentation.nii.gz'.format(subjects_dir=subjects_dir,subj=subj))



#### rh 

print 'getting intensity values for the mask ....'

maskObj = nib.load('{subjects_dir}/{subj}/mri/rh_choroid+ventricle_mask.nii.gz'.format(subjects_dir=subjects_dir,
                                                                        subj=subj))
mask = maskObj.get_data()
mask_indices = np.where(mask)
mask_indices_array = np.array(mask_indices)
mask_T1_vals = T1[mask_indices]


## GMM
X = np.reshape(mask_T1_vals,(-1,1))
gmm = GaussianMixture(n_components=2, covariance_type='full').fit(X)
gmmb = BayesianGaussianMixture(n_components=2, covariance_type='full').fit(X)
save_segmentation(gmmb,'rh_choroid_gmmb_mask.nii.gz')


## susan 
input_img = '{subjects_dir}/{subj}/mri/rh_choroid_gmmb_mask.nii.gz'.format(subjects_dir=subjects_dir,subj=subj)
susan(input_img)

## read choroid_gmmb_mask_susan.nii.gz
choroid_gmmb_mask = nib.load('{subjects_dir}/{subj}/mri/rh_choroid_gmmb_mask.nii.gz'.format(subjects_dir=subjects_dir, subj=subj))
choroid_gmmb_mask_ = choroid_gmmb_mask.get_data()

choroid_gmmb_susan = nib.load('{subjects_dir}/{subj}/mri/rh_choroid_gmmb_mask_susan.nii.gz'.format(subjects_dir=subjects_dir, subj=subj)).get_data()

choroid_gmmb_mask_ind = np.where(choroid_gmmb_mask_==1)
susan_vals = choroid_gmmb_susan[choroid_gmmb_mask_ind]

susan_gmmb = BayesianGaussianMixture(n_components=3).fit(np.reshape(susan_vals,(-1,1)))
susan_gmmb_predict = susan_gmmb.predict(np.reshape(susan_vals,(-1,1)))

m = susan_gmmb.means_.flatten()

choroid_ind = np.where(m==np.max(m))[0][0]

choroid_susan_seg = np.zeros(choroid_gmmb_mask_.shape)
choroid_susan_seg[(choroid_gmmb_mask_ind[0][susan_gmmb_predict==choroid_ind],choroid_gmmb_mask_ind[1][susan_gmmb_predict==choroid_ind], choroid_gmmb_mask_ind[2][susan_gmmb_predict==choroid_ind])]= 1

choroid_susan_segObj = nib.Nifti1Image(choroid_susan_seg,choroid_gmmb_mask.affine)
nib.save(choroid_susan_segObj,'{subjects_dir}/{subj}/mri/rh_choroid_susan_segmentation.nii.gz'.format(subjects_dir=subjects_dir,subj=subj))


## saving final masks

cmd = 'fslmaths {subjects_dir}/{subj}/mri/lh_choroid_susan_segmentation.nii.gz -add {subjects_dir}/{subj}/mri/rh_choroid_susan_segmentation.nii.gz {subjects_dir}/{subj}/mri/choroid_susan_segmentation.nii.gz'.format(subjects_dir=subjects_dir,subj=subj)
run_cmd(cmd)

cmd = 'fslmaths {subjects_dir}/{subj}/mri/lh_choroid_gmmb_mask.nii.gz -add {subjects_dir}/{subj}/mri/rh_choroid_gmmb_mask.nii.gz {subjects_dir}/{subj}/mri/choroid_gmmb_mask.nii.gz'.format(subjects_dir=subjects_dir,subj=subj)
run_cmd(cmd)


###### stats ######

def write_stats(input_img,fname):
    cmd = 'fslstats {input_img} -V'.format(input_img=input_img)
    out,err = run_cmd(cmd)
    stat = out.split('\n')[0].split(' ')[0]
    f = open(fname,'w')
    f.write(stat)



for img in ['lh_choroid_gmmb_mask','lh_choroid_susan_segmentation','rh_choroid_gmmb_mask','rh_choroid_susan_segmentation','aseg_choroid']:
    input_img = '{subjects_dir}/{subj}/mri/{img}.nii.gz'.format(subjects_dir=subjects_dir, subj=subj, img = img)
    fname='{subjects_dir}/{subj}/mri/{img}_stat.txt'.format(subjects_dir=subjects_dir, subj=subj, img=img)
    write_stats(input_img,fname=fname)
















