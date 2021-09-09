# --------------------------------------------------------
# UAVLAB CA
# --------------------------------------------------------

import caffe
import yaml
import numpy as np
from fast_rcnn.config import cfg
import pdb
import scipy

DEBUG = False

class PhySizeLayer(caffe.Layer):
    """
    adjust the inputs send to the smoothl1losslayer
    """

    def setup(self, bottom, top):
        layer_params = yaml.load(self.param_str_)
        self._num_classes = layer_params['num_classes']

        #output
        # phy_area
        top[0].reshape(1, self._num_classes )
        # phy_mean
        top[1].reshape(1, self._num_classes )
        # phy_inside_weights
        top[2].reshape(1, self._num_classes )
        # phy_outside_weights
        top[3].reshape(1, self._num_classes )


  

    def forward(self, bottom, top):
     
        # Proposal ROIs (0, x1, y1, x2, y2) coming from RPN
        
        rois_p2 = bottom[0].data
        rois_p3 = bottom[1].data
        rois_p4 = bottom[2].data
        rois_p5 = bottom[3].data


        #bbox_preds(proposal shifts)
        bbox_preds = bottom[4].data
        
        #phy_scale 
        phy_scale = bottom[5].data[0]
        #label of proposals
        all_labels = bottom[6].data	

        #bbox_inside_weights
        bbox_inside_weights = bottom[7].data	
        #pdb.set_trace()
        #im_info
        im_infor = bottom[8].data
        #scale
        im_scale = im_infor[0,2]
        #mask
        mask = bottom[9].data

 
        #mean, take care that start from the bg ,i.e. from class 0
        pre_calu_mean = np.array( cfg.TRAIN.PHY_MEAN )
        #std , take care that start from the bg ,i.e. from class 0
        pre_calu_std = np.array( cfg.TRAIN.PHY_STD )		
        

        #1024 
        all_rois = np.vstack((rois_p2, rois_p3, rois_p4, rois_p5))	
        #scipy.io.savemat('/home/ca/rois.mat', mdict={'rois': all_rois}) 
        
        all_batch_size = cfg.TRAIN.BATCH_SIZE*4  #4 feature map layers
        bbox_preds = bbox_preds.reshape(self._num_classes*all_batch_size,4)        
        all_rois = np.tile(all_rois, self._num_classes)

        all_rois = all_rois.reshape(self._num_classes*all_batch_size,5)   #0,x1,y1,x2,y2
        
        sample = np.linspace(0,bbox_inside_weights.shape[1],num=self._num_classes,endpoint=False,dtype=int)
        #pdb.set_trace()
        phy_inside_weights = bbox_inside_weights[:,sample]          
        #scipy.io.savemat('/home/ca/phy_inside_weights.mat', mdict={'phy_inside_weights': phy_inside_weights})        
        flag = phy_inside_weights.reshape(self._num_classes*all_batch_size,1)
        #other is useless
        index = np.where(flag > 0)
        
        all_y_max = np.round(all_rois[:,4]).astype(np.int)
        all_y_min = np.round(all_rois[:,2]).astype(np.int)
        all_x_max = np.round(all_rois[:,3]).astype(np.int)
        all_x_min = np.round(all_rois[:,1]).astype(np.int)
        
        area = np.zeros([self._num_classes*all_batch_size,1])
        for i in index[0]:
            #only one image per iteration
            target_area = mask[0,all_x_min[i]:all_x_max[i]+1,all_y_min[i]:all_y_max[i]+1]
            #pdb.set_trace()
            area[i] = np.sum(target_area)
        '''
        for i in xrange(0,self._num_classes*all_batch_size):
            #only one image per iteration
            target_area = mask[0,all_x_min[i]:all_x_max[i]+1,all_y_min[i]:all_y_max[i]+1]
            #pdb.set_trace()
            area[i] = np.sum(target_area)
        '''
        area = area.astype(float)
        area = area * phy_scale**2 / im_scale**2
        
        img_l = area
        img_l = img_l.reshape(all_batch_size, self._num_classes)
        #scipy.io.savemat('/home/ca/area.mat', mdict={'area': area})  
        #remind to check the data type, should be float 32
        #phy_l = area*phy_scale*phy_scale / pre_calu_std
        #phy_mean = pre_calu_mean*phy_scale*phy_scale / pre_calu_std\
        #print("area.shape:    %d/n", area.shape)
        #print("phy_scale:    ", phy_scale)
        #print("pre_calu_std.shape:    %d/n", pre_calu_std.shape)
        phy_l = img_l*pre_calu_std		
        phy_mean = pre_calu_mean*pre_calu_std      
        phy_mean = phy_mean.reshape(1, self._num_classes)
        phy_mean = np.tile(phy_mean, all_batch_size)
        phy_mean = phy_mean.reshape(all_batch_size, self._num_classes)





        # phy_area
        top[0].reshape(*phy_l.shape)
        top[0].data[...] = phy_l

        # phy_mean
        top[1].reshape(*phy_mean.shape)
        top[1].data[...] = phy_mean
        
        # phy_inside_weights
        top[2].reshape(*phy_inside_weights.shape)
        top[2].data[...] = phy_inside_weights
        #pdb.set_trace()
        # phy_outside_weights
        top[3].reshape(*phy_inside_weights.shape)
        top[3].data[...] = phy_inside_weights


       
    def backward(self, top, propagate_down, bottom):
        """This layer does not propagate gradients."""
        pass

    def reshape(self, bottom, top):
        """Reshaping happens during the call to forward."""
        pass





