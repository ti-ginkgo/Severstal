import pandas as pd

from torch.utils.data.dataset import Dataset
from torch.utils.data.sampler import Sampler

from utils.mask_functions import *
from utils.augment_util import *
from utils.common_util import *
from datasets.tool import *
from config.config import *
import numpy as np

class SteelDataset(Dataset):
    def __init__(self, 
                 steel_df,
                 img_size=(256, 1600),
                 mask_size=(256, 1600),
                 transform=None,
                 return_label=True,
                 pseudo=None,
                 pseudo_ratio=0.,
                 crop_version=None,
                 dataset=None,
                 predict_pos=False):
        self.img_size = img_size
        self.mask_size = mask_size
        self.return_label = return_label
        self.crop_version = crop_version
        self.dataset = dataset
        self.suffix = 'jpg'
       
        base_dir = DATA_DIR
        if dataset in ['train', 'val']:
            img_dir = opj(base_dir, 'train', 'images', 'images_256x1600')
        elif dataset in ['test']:
            img_dir = opj(base_dir, 'test', 'images', 'images_256x1600')
        else:
            raise ValueError(dataset)

        if crop_version is None:
            self.img_ids = self.steel_df[ID].values
        else:
            self.img_ids = self.steel_df[CROP_ID].values

        self.img_dir = img_dir
        self.num = len(self.img_ids)

        self.basic_img_ids = self.img_ids
        self.transform = transform

        print('image_dir: %s' % self.img_dir)
        print('image size: %s' % str(self.img_size))

    def __getitem__(self, index):
        img_id = self.img_ids[index]
        img_fname = opj(self.img_dir, f'{img_id}')

        image = cv2.imread(img_fname)
        if image is None:
            print(img_fname)
            raise ValueError(img_fname)
  
        if self.return_label:
            mask = build_mask(self.steel_df.iloc[index], self.mask_size[0], self.mask_size[1])
            mask = mask.astype(np.int8)
            
            if self.transform is not None:
                image, mask = self.transform(image=image, mask=mask)

            image = image / 255.0
            # mask = mask / 255.0
            image = image_to_tensor(image)
            mask = label_to_tensor(mask)
            return image, mask, index
        else:
            if self.transform is not None:
                image = self.transform(image=image)[0]

            image = image / 255.0
            image = image_to_tensor(image)
            return image, index

    def __len__(self):
        return self.num