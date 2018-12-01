import numpy as np


def gaussian_blur3d(input_3d: np.ndarray, meta_data: dict,
                    config: dict) -> np.array:
    '''Performs 3D Gaussian blur on the input volume

    :param input_3d: input volume in 3D numpy array
    :param meta_data: a dict object with the following key(s):
        'spacing': 3-tuple of floats, the pixel spacing in 3D
    :param config: a dict object with the following key(s):
        'sigma': a float indicating size of the Gaussian kernel

    :return: the blurred volume in 3D numpy array, same size as input_3d
    '''
    weights = np.asarray(gaussian_blur1d_weights(config['sigma']))
    spacing = meta_data['spacing']
    result = np.array(input_3d.shape,dtype(input_3d.dtype))
    for x in range(input_3d.shape[0]):
    	for y in range(input_3d.shape[1]):
    		convy = input_3d[x][y][y,y+weights.shape[0]-1] * weights
    		input_3d[x][y][y,y+weights.shape[0]-1] += convy
    		y += spacing[0]
    	for z in range(input_3d.shape[2]):
    		convz = input_3d[x][:,z][z,z+weights.shape[0]-1] * weights
    		input_3d[x][:,z][z,z+weights.shape[0]-1] += convz
    		z += spacing[0]
    	x+=spacing[2]

    result = input_3d;


def gaussian_blur1d_weights(sigma):
	f = np.polynomial.Polynomial([0,0,-0.5/(sigma*sigma)])
	radius = 2*sigma
	x = np.arange(-radius,radius+1)
	fx = np.exp(f(x),dtype=np.double)
	fx = fx/fx.sum()	
	fd = f.deriv()
	fx *= fd(x)
	return fx
	
