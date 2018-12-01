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
	Normalize the 3D volume to the range between 0 and 1, converting the data from the input data type to 32-bit float data type
'''
def build_3D_Volume(dcmlist):
	slices = np.zeros((len(dcmlist),dcmlist[0].Rows,dcmlist[0].Columns))
	for d in range(len(dcmlist)):	
		vol = np.asarray(dcmlist[d].pixel_array)
		vol = (vol-vol.min())/(vol.max()-vol.min())
		vol = vol.astype('float32')
		slices[d] = vol
	return slices

'''
	Build a dictionary to store the following meta data:
	Pixel spacing in all three dimensions
	Series description 
	The imaging modality name
'''
def build_metadata_dct(dcmlist):
	metadatadct = dict()
	for d in range(len(dcmlist)):
		SpacingList = dcmlist[d].PixelSpacing._list
		SpacingList.append(dcmlist[d].SpacingBetweenSlices)
		metadata = {d:{'Modality':dcmlist[d].Modality,
				'SeriesDescription':dcmlist[d].SeriesDescription,
				'PixelSpacing':SpacingList}}
		metadatadct.update(metadata)
	return metadatadct



if __name__=='__main__':

	parser = ArgumentParser()
	parser.add_argument("--input-dicom", "-i", dest="inputdicompath",
                    	help="path to input DICOM directory")
	parser.add_argument("--output-json", "-j", dest="outputjsonfile",
                    	help="path to output JSON file")

	parser.add_argument("--output-hdf5", "-f", dest="outputhdf5file",
                    	help="path to output hdf5 file")


	args = parser.parse_args()
	
	mypath = args.inputdicompath
	dcmlist = read_dicom_files(mypath)
	slices = build_3D_Volume(dcmlist)
	metadatadct = build_metadata_dct(dcmlist)
	jsonfilename = args.outputjsonfile
	json.dump(metadatadct,open(jsonfilename,'w'))
	houtputfilename = args.outputhdf5file
	hf = h5py.File(houtputfilename,'w')
	hf.create_dataset('Pixel_Data',data=slices)


