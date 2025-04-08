#!/usr/bin/env python3
"""
ChP-Seg: A lightweight python script for accurate segmentation of choroid plexus
Author: Ehsan Tadayon, MD
Date: 2019
"""

import sys
import subprocess
import numpy as np
import nibabel as nib
from sklearn.mixture import GaussianMixture, BayesianGaussianMixture


def run_cmd(cmd):
    """Run a shell command and print its output and errors."""
    print(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    show_error(result.stderr)
    return result.stdout, result.stderr


def show_error(err):
    """Print error messages if any."""
    if err:
        print(err)


def susan(input_img):
    """
    Run the 'susan' command on the given image.
    The command assumes the image file has a '.nii.gz' extension.
    """
    base_img = input_img.split('.nii')[0]
    cmd = f'susan {base_img}.nii.gz 1 1 3 1 0 {base_img}_susan.nii.gz'
    run_cmd(cmd)


def save_segmentation(clf, out_name, mask_t1_vals, X, mask_indices, mask_obj, subjects_dir, subj):
    """
    Save segmentation result from a clustering model.

    Parameters:
        clf : clustering model (e.g. GaussianMixture or BayesianGaussianMixture)
        out_name : output filename (e.g. 'lh_choroid_gmmb_mask.nii.gz')
        mask_t1_vals : intensity values from the T1 image within the mask
        X : feature array (e.g. intensity values reshaped to (-1, 1))
        mask_indices : tuple of indices (i, j, k) where the mask is 1
        mask_obj : nibabel image object (used to access the affine)
        subjects_dir : base directory of the subjects
        subj : subject identifier
    """
    # Initialize an empty image volume
    new_img = np.zeros((256, 256, 256))

    # Predict labels and decide which cluster corresponds to the choroid plexus
    predictions = clf.predict(X)
    if np.mean(mask_t1_vals[predictions == 1]) > np.mean(mask_t1_vals[predictions == 0]):
        choroid_ind = np.where(predictions == 1)[0]
    else:
        choroid_ind = np.where(predictions == 0)[0]

    choroid_coords = (mask_indices[0][choroid_ind],
                      mask_indices[1][choroid_ind],
                      mask_indices[2][choroid_ind])
    new_img[choroid_coords] = 1
    img_obj = nib.Nifti1Image(new_img, mask_obj.affine)
    out_path = f'{subjects_dir}/{subj}/mri/{out_name}'
    nib.save(img_obj, out_path)


def write_stats(input_img, fname):
    """
    Write volume statistics (from fslstats) for the given image to a file.

    Parameters:
        input_img : path to the image file
        fname : path to the output text file
    """
    cmd = f'fslstats {input_img} -V'
    out, _ = run_cmd(cmd)
    stat = out.split('\n')[0].split(' ')[0]
    with open(fname, 'w') as f:
        f.write(stat)


def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <subjects_dir> <subj>")
        sys.exit(1)

    subjects_dir = sys.argv[1]
    subj = sys.argv[2]

    # Load the T1 volume using nibabel's get_fdata (preferred in Python 3)
    t1_path = f'{subjects_dir}/{subj}/mri/T1.mgz'
    T1 = nib.load(t1_path).get_fdata()

    # Create masks for choroid and ventricle segmentation
    print('Creating masks: choroid+ventricle_mask.nii.gz and aseg_choroid_mask.nii.gz')
    cmd = (
        f'mri_binarize --i {subjects_dir}/{subj}/mri/aseg.mgz '
        f'--match 31 63 --o {subjects_dir}/{subj}/mri/aseg_choroid_mask.nii.gz'
    )
    run_cmd(cmd)

    cmd = (
        f'mri_binarize --i {subjects_dir}/{subj}/mri/aseg.mgz '
        f'--match 4 5 31 --o {subjects_dir}/{subj}/mri/lh_choroid+ventricle_mask.nii.gz'
    )
    run_cmd(cmd)

    cmd = (
        f'mri_binarize --i {subjects_dir}/{subj}/mri/aseg.mgz '
        f'--match 43 44 63 --o {subjects_dir}/{subj}/mri/rh_choroid+ventricle_mask.nii.gz'
    )
    run_cmd(cmd)

    # --- Left Hemisphere Processing ---
    print('Processing left hemisphere...')
    lh_mask_path = f'{subjects_dir}/{subj}/mri/lh_choroid+ventricle_mask.nii.gz'
    lh_mask_obj = nib.load(lh_mask_path)
    lh_mask = lh_mask_obj.get_fdata()
    lh_mask_indices = np.where(lh_mask == 1)
    mask_t1_vals = T1[lh_mask_indices]
    X = mask_t1_vals.reshape(-1, 1)

    bgmm_lh = BayesianGaussianMixture(n_components=2, covariance_type='full').fit(X)
    save_segmentation(bgmm_lh, 'lh_choroid_gmmb_mask.nii.gz', mask_t1_vals, X,
                      lh_mask_indices, lh_mask_obj, subjects_dir, subj)

    # Apply Susan filtering on left hemisphere
    lh_gmmb_mask_path = f'{subjects_dir}/{subj}/mri/lh_choroid_gmmb_mask.nii.gz'
    susan(lh_gmmb_mask_path)

    # Read the Susan-filtered mask and further segment
    lh_choroid_gmmb_mask = nib.load(lh_gmmb_mask_path).get_fdata()
    lh_choroid_gmmb_mask_indices = np.where(lh_choroid_gmmb_mask == 1)
    lh_choroid_gmmb_susan = nib.load(
        f'{subjects_dir}/{subj}/mri/lh_choroid_gmmb_mask_susan.nii.gz'
    ).get_fdata()
    susan_vals = lh_choroid_gmmb_susan[lh_choroid_gmmb_mask_indices]

    bgmm_susan_lh = BayesianGaussianMixture(n_components=3).fit(susan_vals.reshape(-1, 1))
    susan_predictions = bgmm_susan_lh.predict(susan_vals.reshape(-1, 1))
    means = bgmm_susan_lh.means_.flatten()
    choroid_cluster = int(np.argmax(means))

    lh_choroid_seg = np.zeros(lh_choroid_gmmb_mask.shape)
    indices = np.where(susan_predictions == choroid_cluster)
    lh_choroid_seg[(lh_choroid_gmmb_mask_indices[0][indices],
                    lh_choroid_gmmb_mask_indices[1][indices],
                    lh_choroid_gmmb_mask_indices[2][indices])] = 1

    lh_choroid_seg_obj = nib.Nifti1Image(lh_choroid_seg,
                                         nib.load(lh_gmmb_mask_path).affine)
    nib.save(lh_choroid_seg_obj,
             f'{subjects_dir}/{subj}/mri/lh_choroid_susan_segmentation.nii.gz')

    # --- Right Hemisphere Processing ---
    print('Processing right hemisphere...')
    rh_mask_path = f'{subjects_dir}/{subj}/mri/rh_choroid+ventricle_mask.nii.gz'
    rh_mask_obj = nib.load(rh_mask_path)
    rh_mask = rh_mask_obj.get_fdata()
    rh_mask_indices = np.where(rh_mask == 1)
    mask_t1_vals_rh = T1[rh_mask_indices]
    X_rh = mask_t1_vals_rh.reshape(-1, 1)

    # Fit both GMM and BayesianGMM (only Bayesian is used for segmentation)
    _ = GaussianMixture(n_components=2, covariance_type='full').fit(X_rh)
    bgmm_rh = BayesianGaussianMixture(n_components=2, covariance_type='full').fit(X_rh)
    save_segmentation(bgmm_rh, 'rh_choroid_gmmb_mask.nii.gz', mask_t1_vals_rh, X_rh,
                      rh_mask_indices, rh_mask_obj, subjects_dir, subj)

    # Apply Susan filtering on right hemisphere
    rh_gmmb_mask_path = f'{subjects_dir}/{subj}/mri/rh_choroid_gmmb_mask.nii.gz'
    susan(rh_gmmb_mask_path)

    rh_choroid_gmmb_mask = nib.load(rh_gmmb_mask_path).get_fdata()
    rh_choroid_gmmb_susan = nib.load(
        f'{subjects_dir}/{subj}/mri/rh_choroid_gmmb_mask_susan.nii.gz'
    ).get_fdata()
    rh_choroid_gmmb_mask_indices = np.where(rh_choroid_gmmb_mask == 1)
    susan_vals_rh = rh_choroid_gmmb_susan[rh_choroid_gmmb_mask_indices]

    bgmm_susan_rh = BayesianGaussianMixture(n_components=3).fit(susan_vals_rh.reshape(-1, 1))
    susan_predictions_rh = bgmm_susan_rh.predict(susan_vals_rh.reshape(-1, 1))
    means_rh = bgmm_susan_rh.means_.flatten()
    choroid_cluster_rh = int(np.argmax(means_rh))

    rh_choroid_seg = np.zeros(rh_choroid_gmmb_mask.shape)
    indices_rh = np.where(susan_predictions_rh == choroid_cluster_rh)
    rh_choroid_seg[(rh_choroid_gmmb_mask_indices[0][indices_rh],
                    rh_choroid_gmmb_mask_indices[1][indices_rh],
                    rh_choroid_gmmb_mask_indices[2][indices_rh])] = 1

    rh_choroid_seg_obj = nib.Nifti1Image(rh_choroid_seg,
                                         nib.load(rh_gmmb_mask_path).affine)
    nib.save(rh_choroid_seg_obj,
             f'{subjects_dir}/{subj}/mri/rh_choroid_susan_segmentation.nii.gz')

    # --- Combine Final Masks ---
    cmd = (
        f'fslmaths {subjects_dir}/{subj}/mri/lh_choroid_susan_segmentation.nii.gz '
        f'-add {subjects_dir}/{subj}/mri/rh_choroid_susan_segmentation.nii.gz '
        f'{subjects_dir}/{subj}/mri/choroid_susan_segmentation.nii.gz'
    )
    run_cmd(cmd)

    cmd = (
        f'fslmaths {subjects_dir}/{subj}/mri/lh_choroid_gmmb_mask.nii.gz '
        f'-add {subjects_dir}/{subj}/mri/rh_choroid_gmmb_mask.nii.gz '
        f'{subjects_dir}/{subj}/mri/choroid_gmmb_mask.nii.gz'
    )
    run_cmd(cmd)

    # --- Save Stats ---
    img_names = [
        'lh_choroid_gmmb_mask',
        'lh_choroid_susan_segmentation',
        'rh_choroid_gmmb_mask',
        'rh_choroid_susan_segmentation',
        'choroid_susan_segmentation'
    ]

    for img in img_names:
        input_img = f'{subjects_dir}/{subj}/mri/{img}.nii.gz'
        fname = f'{subjects_dir}/{subj}/mri/{img}_stat.txt'
        write_stats(input_img, fname)


if __name__ == '__main__':
    main()
