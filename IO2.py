import pydicom
import os
import h5py
import json
import argparse
from json import dumps,encoder
import numpy as np
from os import listdir
from argparse import ArgumentParser



''' 
	Read the DICOM files in a directory.
    	Build a 3D volume by sorting against each file’s Slice Location DICOM tag in ascending order
'''
def read_dicom_files(mypath):
	dcmlist = [pydicom.read_file(mypath+f) for f in os.listdir(mypath)]
	dcmlist.sort(key=lambda d:d.SliceLocation,reverse=True)
	return dcmlist

'''
	Read the image pixel data from the hdf5 file
'''
def read_h5pyfile(filename):
	hf = h5py.File(filename,'r')
	hslices = hf[list(hf.keys())[0]].value
	return hslices
'''
	Replace the pixel data inside the DICOM datasets read in Step 1 with those read at Step 2
	Re-scale the pixel values from between 0 to 1 to the dynamic range of the data type used by the template DICOM files
	Assign a shared new Series Instance UID to all the files
	Assign a new SOP Instance UID to each of the files.
	Save the resulting datasets to the output DICOM folder
'''

def process_h5pyfile_data(hslices,dcmlist,path):
	newlist = np.zeros(hslices.shape,dtype=dcmlist[0].pixel_array.dtype)
	for x in range(len(hslices)): 
		hslices[x]=hslices[x]*(dcmlist[x].pixel_array.max()-dcmlist[x].pixel_array.min())
		newlist[x]=hslices[x].round().astype(dcmlist[x].pixel_array.dtype)
		dcmlist[x].PixelData = newlist[x].tobytes()
		dcmlist[x].SeriesInstanceUID = dcmlist[x].SeriesInstanceUID+'0'
		dcmlist[x].SOPInstanceUID = dcmlist[x].SOPInstanceUID+str(x)
		dcmlist[x].save_as(path+'/NIM-0001-000'+str(x)+'.dcm')

if __name__=='__main__':

	parser = ArgumentParser()

	parser.add_argument("--input-hdf5", "-i", dest="inputh5file",
                    	help="path to input hdf5 file")

	parser.add_argument("--input-dicom2", "-d", dest="inputdicompath",
                    	help="path to the template DICOM directory")

	parser.add_argument("--output-dicom", "-o", dest="outputdicomfile",
                    	help="path to output DICOM directory")

	args = parser.parse_args()
	dcmpath = args.outputdicomfile
	mypath = args.inputdicompath
	dcmlist = read_dicom_files(mypath)
	import pdb;pdb.set_trace()
	hfilename = args.inputh5file
	hslices = read_h5pyfile(hfilename)
	process_h5pyfile_data(hslices,dcmlist,dcmpath)


