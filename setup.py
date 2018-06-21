from setuptools import setup, find_packages

__version__='0.0.1'

setup(
        name='fpga-image-pack',
	version=__version__,
	packages=find_packages(),

	entry_points={
		'console_scripts': [
			'fpga-image-pack-ecp5 = lattice.ecp5:_pack'
		]
	},

	# metadata for upload to PyPI
	author='Aleksandr Gusarov',
	author_email='alexandergusarov@gmail.com',
	description='Tool for pack binary FPGA images into one image file',
	license='MIT'
)
