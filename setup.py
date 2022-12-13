from setuptools import setup

setup(name='pca9685_psd',
      version='0.1',
      description='PCA9685 Precision Servo Driver',
      author='Chris Albertson', url = '#',
      license='GNU LGPL',
      author_email='albertson.chris@gmail.com',
      packages=['pca9685_psd'],
      package_data={'': ['*.yaml']},
      install_requires=['smbus2'],
      zip_safe=False)
