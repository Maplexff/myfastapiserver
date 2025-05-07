from argparse import ArgumentParser
import os
import sys
import io
sys.path.insert(0,os.getcwd())
import torch

from utils.inference import inference_model, init_model, show_result_pyplot
from utils.train_utils import get_info, file2dict
from models.build import BuildNet

from PIL import Image
import json



def server_load_model():

    config = 'pth/model_1/efficientnetv2_m.py'
    classesmap = 'datas/annotations.txt'
    devicetype = 'cuda' if torch.cuda.is_available() else 'cpu'
    devicetype = 'cpu'


    classes_names, label_names = get_info(classesmap)
    # build the model from a config file and a checkpoint file
    model_cfg, train_pipeline, val_pipeline,data_cfg, lr_config, optimizer_cfg = file2dict(config)
    # if device is not None:
    #     device = torch.device(device)
    # else:
    #     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    device = torch.device(devicetype)
    global model
    model= BuildNet(model_cfg)
    model = init_model(model, data_cfg, device=device, mode='eval')
    


def server_image(filepath: str):

    config = 'pth/model_1/efficientnetv2_m.py'
    classesmap = 'datas/annotations.txt'
    classes_names, label_names = get_info(classesmap)
    model_cfg, train_pipeline, val_pipeline,data_cfg, lr_config, optimizer_cfg = file2dict(config)
    result = inference_model(model, filepath, val_pipeline, classes_names,label_names)
    print(result)
    return result



