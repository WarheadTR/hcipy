import numpy as np
from .propagator import MonochromaticPropagator
from ..optics import Wavefront, make_polychromatic
from ..field import Field

class FraunhoferPropagatorMonochromatic(MonochromaticPropagator):
	'''A monochromatic perfect lens propagator.

		This implements the propagation of a wavefront through a perfect lens. The wavefront
		is assumed to be exactly in the front focal plane of the lens and is propagated to the
		back focal plane. The implementation follows [1]_.

		.. [1] Goodman, J.W., 2005 Introduction to Fourier optics. Roberts and Company Publishers.
	
		Parameters
		----------
		input_grid : Grid
			The grid on which the incoming wavefront is defined.
		output_grid : Grid
			The grid on which the outgoing wavefront is to be evaluated.
		wavelength : scalar
			The wavelength of the wavefront.
		focal_length : scalar
			The focal length of the lens system.
	'''
	def __init__(self, input_grid, output_grid, wavelength_0=1, focal_length=1, wavelength=1):
		from ..fourier import make_fourier_transform

		if focal_length is None:
			f_lambda_ref = 1
		else:
			f_lambda_ref = wavelength_0 * focal_length
		
		f_lambda = f_lambda_ref * (wavelength / wavelength_0)
		self.uv_grid = output_grid.scaled(2*np.pi / f_lambda)
		self.fourier_transform = make_fourier_transform(input_grid, self.uv_grid)
		self.output_grid = output_grid

		# Intrinsic to Fraunhofer propagation
		self.norm_factor = 1 / (1j * f_lambda)
		self.input_grid = input_grid

	def forward(self, wavefront):
		'''Propagate a wavefront forward through the lens.
	
		Parameters
		----------
		wavefront : Wavefront
			The incoming wavefront.
		
		Returns
		-------
		Wavefront
			The wavefront after the propagation.
		'''
		U_new = self.fourier_transform.forward(wavefront.electric_field) * self.norm_factor
		return Wavefront(Field(U_new, self.output_grid), wavefront.wavelength)
	
	def backward(self, wavefront):
		'''Propagate a wavefront backward through the lens.
	
		Parameters
		----------
		wavefront : Wavefront
			The incoming wavefront.
		
		Returns
		-------
		Wavefront
			The wavefront after the propagation.
		'''
		U_new = self.fourier_transform.backward(wavefront.electric_field) / self.norm_factor
		return Wavefront(Field(U_new, self.input_grid), wavefront.wavelength)
	
	def get_transformation_matrix_forward(self, input_grid, wavelength=1):
		'''Create the forward linear transformation between the internal input grid and output grid.
	
		Parameters
		----------
		input_grid : Grid
			The input grid on which the wavefront is defined.
			Currently this parameter is ignored and an internal grid is used.
		wavelength : scalar
			The wavelength of the wavefront.
		
		Returns
		-------
		ndarray
			The transformation matrix that describes the propagation.
		'''
		# Ignore input wavelength and just use the internal one.
		return self.fourier_transform.get_transformation_matrix_forward() * self.norm_factor
	
	def get_transformation_matrix_backward(self, input_grid, wavelength=1):
		'''Create the backward linear transformation between the internal input grid and output grid.
	
		Parameters
		----------
		input_grid : Grid
			The input grid on which the wavefront is defined.
			Currently this parameter is ignored and an internal grid is used.
		wavelength : scalar
			The wavelength of the wavefront. 

		Returns
		-------
		ndarray
			The transformation matrix that describes the propagation.
		'''
		# Ignore input wavelength and just use the internal one.
		return self.fourier_transform.get_transformation_matrix_backward() / self.norm_factor
	
FraunhoferPropagator = make_polychromatic()(FraunhoferPropagatorMonochromatic)