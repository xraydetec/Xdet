# --------------------------------------------------------
# Fast R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""Blob helper functions."""

import numpy as np
import cv2
import pdb

def mask_list_to_blob(masks):
    """Convert a list of images into a network input.

    Assumes images are already prepared (means subtracted, BGR order, ...).
    """
    #pdb.set_trace()
    max_shape = np.array([mask.shape for mask in masks]).max(axis=0)
    num_masks = len(masks)
    mask_blob = np.zeros((num_masks, max_shape[0], max_shape[1]),
                    dtype=np.float32)
    for i in xrange(num_masks):
        mask = masks[i]
        mask_blob[i, 0:mask.shape[0], 0:mask.shape[1]] = mask
    # Move channels (axis 3) to axis 1
    # Axis order will become: (batch elem, channel, height, width)

    return mask_blob




def im_list_to_blob(ims):
    """Convert a list of images into a network input.

    Assumes images are already prepared (means subtracted, BGR order, ...).
    """
    #pdb.set_trace()
    max_shape = np.array([im.shape for im in ims]).max(axis=0)
    num_images = len(ims)
    blob = np.zeros((num_images, max_shape[0], max_shape[1], 3),
                    dtype=np.float32)
    for i in xrange(num_images):
        im = ims[i]
        blob[i, 0:im.shape[0], 0:im.shape[1], :] = im
    # Move channels (axis 3) to axis 1
    # Axis order will become: (batch elem, channel, height, width)
    channel_swap = (0, 3, 1, 2)
    blob = blob.transpose(channel_swap)
    return blob

def prep_im_for_blob(im, mask, pixel_means, target_size, max_size,stride):
    """Mean subtract and scale an image for use in a blob."""
    #pdb.set_trace()
    im = im.astype(np.float32, copy=False)
    im -= pixel_means
    im_shape = im.shape
    im_size_min = np.min(im_shape[0:2])
    im_size_max = np.max(im_shape[0:2])
    im_scale = float(target_size) / float(im_size_min)
    # Prevent the biggest axis from being more than MAX_SIZE
    if np.round(im_scale * im_size_max) > max_size:
        im_scale = float(max_size) / float(im_size_max)
    im = cv2.resize(im, None, None, fx=im_scale, fy=im_scale,
                    interpolation=cv2.INTER_LINEAR)
    mask = cv2.resize(mask, None, None, fx=im_scale, fy=im_scale,
                    interpolation=cv2.INTER_LINEAR)    
    if stride == 0:
        return im, mask, im_scale
    else:
        # pad to product of stride
        im_height = int(np.ceil(im.shape[0] / float(stride)) * stride)
        im_width = int(np.ceil(im.shape[1] / float(stride)) * stride)
        im_channel = im.shape[2]
        padded_im = np.zeros((im_height, im_width, im_channel))
        padded_im[:im.shape[0], :im.shape[1], :] = im
        padded_mask = np.zeros((im_height, im_width))
        padded_mask[:im.shape[0], :im.shape[1]] = mask
        return padded_im, padded_mask, im_scale

