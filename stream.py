import chainer, math
from chainer import functions, cuda
from chainer.links import *

# Standar functions

class ClippedReLU():
	def __init__(self, z=20):
		self.z = z

	def __call__(self, x):
		return functions.clipped_relu(x, self.z)

class CReLU():
	def __init__(self, axis=1):
		self.axis = axis

	def __call__(self, x):
		return functions.crelu(x, self.axis)

class ELU():
	def __init__(self, alpha=1):
		self.alpha = alpha

	def __call__(self, x):
		return functions.elu(x, self.alpha)
	
def HardSigmoid():
	return functions.hard_sigmoid

class LeakyReLU():
	def __init__(self, slope=1):
		self.slope = slope

	def __call__(self, x):
		return functions.leaky_relu(x, self.slope)
	
def LogSoftmax():
	return functions.log_softmax

class Maxout():
	def __init__(self, pool_size=0.5):
		self.pool_size = pool_size

	def __call__(self, x):
		return functions.maxout(x, self.pool_size)
	
def ReLU():
	return functions.relu

def Sigmoid():
	return functions.sigmoid

class Softmax():
	def __init__(self, axis=1):
		self.axis = axis

	def __call__(self, x):
		return functions.softmax(x, self.axis)

class Softplus():
	def __init__(self, beta=1):
		self.beta = beta

	def __call__(self, x):
		return functions.softplus(x, self.beta)

def Tanh():
	return functions.tanh

# Pooling

class AveragePooling2D():
	def __init__(self, ksize, stride=None, pad=0):
		self.ksize = ksize
		self.stride = stride
		self.pad = pad

	def __call__(self, x):
		return functions.average_pooling_2d(x, self.ksize, self.stride, self.pad)

class AveragePoolingND():
	def __init__(self, ksize, stride=None, pad=0):
		self.ksize = ksize
		self.stride = stride
		self.pad = pad

	def __call__(self, x):
		return functions.average_pooling_nd(x, self.ksize, self.stride, self.pad)

class MaxPooling2D():
	def __init__(self, ksize, stride=None, pad=0, cover_all=True):
		self.ksize = ksize
		self.stride = stride
		self.pad = pad
		self.cover_all = cover_all

	def __call__(self, x):
		return functions.max_pooling_2d(x, self.ksize, self.stride, self.pad)

class MaxPoolingND():
	def __init__(self, ksize, stride=None, pad=0, cover_all=True):
		self.ksize = ksize
		self.stride = stride
		self.pad = pad
		self.cover_all = cover_all

	def __call__(self, x):
		return functions.max_pooling_nd(x, self.ksize, self.stride, self.pad)

class SpatialPyramidPooling2D():
	def __init__(self, pyramid_height, pooling_class):
		self.pyramid_height = pyramid_height
		self.pooling_class = pooling_class

	def __call__(self, x):
		return functions.spatial_pyramid_pooling_2d(x, self.pyramid_height, self.pooling_class)

class Unpooling2D():
	def __init__(self, ksize, stride=None, pad=0, outsize=None, cover_all=True):
		self.ksize = ksize
		self.stride = stride
		self.pad = pad
		self.outsize = outsize
		self.cover_all = cover_all

	def __call__(self, x):
		return functions.unpooling_2d(x, self.ksize, self.stride, self.pad, self.outsize, self.cover_all)

class UpSampling2D():
	def __init__(self, indexes, ksize, stride=None, pad=0, outsize=None, cover_all=True):
		self.indexes = indexes
		self.ksize = ksize
		self.stride = stride
		self.pad = pad
		self.outsize = outsize
		self.cover_all = cover_all

	def __call__(self, x):
		return functions.upsampling_2d(x, self.indexes, self.ksize, self.stride, self.pad, self.outsize, self.cover_all)

# Array manipulations

class BroadcastTo():
	def __init__(self, shape):
		self.shape = shape

	def __call__(self, x):
		return functions.broadcast_to(x, self.shape)

class ExpandDims():
	def __init__(self, axis):
		self.axis = axis

	def __call__(self, x):
		return functions.expand_dims(x, self.axis)

def Flatten():
	return functions.flatten

class Reshape():
	def __init__(self, shape):
		self.shape = shape

	def __call__(self, x):
		return functions.reshape(x, self.shape)

class RollAxis():
	def __init__(self, axis, start=0):
		self.axis = axis
		self.start = start

	def __call__(self, x):
		return functions.rollaxis(x, self.axis, self.start)

class Squeeze():
	def __init__(self, axis):
		self.axis = axis

	def __call__(self, x):
		return functions.squeeze(x, self.axis)

class SwapAxes():
	def __init__(self, axis1, axis2):
		self.axis1 = axis1
		self.axis2 = axis2

	def __call__(self, x):
		return functions.swapaxes(x, self.axis1, self.axis2)

class Tile():
	def __init__(self, reps):
		self.reps = reps

	def __call__(self, x):
		return functions.tile(x, self.reps)

class Transpose():
	def __init__(self, axes):
		self.axes = axes

	def __call__(self, x):
		return functions.transpose(x, self.axes)

# Noise injections

class Dropout():
	def __init__(self, ratio=0.5):
		self.ratio = ratio

	def __call__(self, x):
		return functions.dropout(x, self.ratio)

class GaussianNoise():
	def __init__(self, mean, std):
		self.mean = mean
		self.std = std

	def __call__(self, x):
		if chainer.config.train == False:
			return x
		xp = cuda.get_array_module(x.data)
		std = math.log(self.std ** 2)
		noise = functions.gaussian(chainer.Variable(xp.zeros_like(x.data)), chainer.Variable(xp.full_like(x.data, std)))
		return x + noise

# Connections

class Residual(object):
	def __init__(self, *layers):
		self.layers = layers

	def __call__(self, x):
		for layer in self.layers:
			x = layer(x)
		return x

# Chain

class Stream(chainer.Chain):
	def __init__(self, *layers):
		super(Stream, self).__init__()
		assert not hasattr(self, "layers")
		self.layers = []
		if len(layers) > 0:
			self.layer(*layers)

	def layer(self, *layers):
		with self.init_scope():
			for i, layer in enumerate(layers):
				index = i + len(self.layers)

				if isinstance(layer, chainer.Link):
					setattr(self, "layer_%d" % index, layer)

				if isinstance(layer, Residual):
					for _index, _layer in enumerate(layer.layers):
						if isinstance(_layer, chainer.Link):
							setattr(self, "layer_{}_{}".format(index, _index), _layer)
		self.layers += layers

	def __call__(self, x):
		for layer in self.layers:
			y = layer(x)
			if isinstance(layer, Residual):
				y += x
			x = y
		return x