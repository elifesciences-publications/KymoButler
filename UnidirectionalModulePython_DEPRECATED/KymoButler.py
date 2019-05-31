import mxnet as mx
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import os
from skimage.morphology import remove_small_objects, thin
from skimage.measure import label, regionprops
from skimage.color import label2rgb
import accum
import sys
from sklearn import preprocessing
import csv

#######################################
###KYMOBUTLER with inception FCN
#######################################

#%% SETUP and helper functions
# get location of temporary folder for data added to the executable
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def ask_user_input(prompt):
    #set up window
    root = tk.Tk()
    root.withdraw()
    #get executeable directory to load data
    cwd=os.path.abspath(os.path.dirname(sys.argv[0]))
    #get Kymograph image path
    image_path = filedialog.askopenfilename(initialdir = cwd, title = prompt)
    dir_path=os.path.dirname(image_path)
    return (dir_path, image_path)

def run_the_net_on(image, path, name, flip):
    e = sym.bind(mx.cpu(), image, aux_states=aux);
    out = e.forward();
    result=out[0][0].asnumpy();
    if flip:
        result=result[:,::-1,:];
    Image.fromarray((result[:,:,1]*255).astype(np.uint8)).save(os.path.join(path,name))
    return result

def load_and_convert(prefix, image, image_dir):
    im = np.asarray(Image.open(os.path.join(image_dir,image)))
    min_max_scaler = preprocessing.MinMaxScaler()
    input_im = min_max_scaler.fit_transform(im);
    inputND = mx.nd.array(np.array([[input_im]]));
    nd["Input"] = inputND;
    #run the net on input anterograde
    ant = run_the_net_on(nd, image_dir, prefix+'_antprob.bmp', False)

    #reflect input image and load to mxnet
    im_ref=im[:,::-1];
    input_imref = min_max_scaler.fit_transform(im_ref);
    inputND = mx.nd.array(np.array([[input_imref]]));
    nd["Input"] = inputND;
    #run the net on input retrograde
    ret = run_the_net_on(nd, image_dir, prefix+'_retprob.bmp', True)

    return (input_im, ant, ret)

def segmentation(p_map):
    thr=p_map[:,:,1]>threshold_value
    rmv=remove_small_objects(thr,5,connectivity=2)
    thin_map=thin(rmv)
    trk=regionprops(label(thin_map,connectivity=2))
    return trk, thin_map

def write_coordinates(writer, p_map, name):
    for i in range(len(p_map)):
        foo=p_map[i].coords + 1 # corrected BUG
        tmp=accum.aggregate(foo[:,0], foo[:,1], func='mean')
        for j in range(len(np.unique(foo[:,0]))):
            writer.writerow([name, i, np.unique(foo[:,0])[j],
                         np.trim_zeros(tmp)[j]])

def process_image(path, img_path):
    # prefix is the name to append to each output image
    prefix = os.path.splitext(os.path.basename(img_path))[0]
    input_im, ant, ret = load_and_convert(prefix, img_path, path)
    #Segmentation and save as CSV
    with open(os.path.join(path, prefix+'_kymographs.csv'), 'w') as f:
        writer = csv.writer(f)
        trk_ant, thin_ant = segmentation(ant)
        trk_ret, thin_ret = segmentation(ret)
        write_coordinates(writer, trk_ant, 'anterograde')
        write_coordinates(writer, trk_ret, 'retrograde')
    #Save Colored overlay
    foo=label2rgb(np.maximum(label(thin_ant,connectivity=2),
                             label(thin_ret,connectivity=2)),
        image=input_im, bg_label=0)
    foo=Image.fromarray((foo*255).astype(np.uint8))
    foo.save(os.path.join(path,prefix+'_overlay.bmp'))


#%% Load incnet Net and get aux states from file
sym = mx.symbol.load(resource_path('net.json'))
nd=mx.nd.load(resource_path('net.params'))
foo=np.loadtxt(resource_path('auxparam.txt'),dtype='str')

batchaux=eval(foo.item())
aux = {}
naux=sym.list_auxiliary_states()
for i in range(len(naux)):
    aux[naux[i]] = mx.nd.array(np.array(batchaux[i]))

#%%
# Import threshold_value and start of the script: use of command line arguments 
#vs interactive window

from config import *

if len(sys.argv) == 1:
    path, img_path = ask_user_input("Select Kymograph to analyze!")
    process_image(path, img_path)
else:
    for i in range(1, len(sys.argv)):
        path = os.path.abspath(os.path.dirname(sys.argv[i]))
        img_path = os.path.basename(sys.argv[i])
        process_image(path, img_path)
