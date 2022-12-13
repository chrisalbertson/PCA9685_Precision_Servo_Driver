from setuptools import setup

setup(name='pca9685_psd',
      version='0.1',
      description='PCA9685 Precision Servo Driver',
      author='Chris Albertson',
      url='https://github.com/chrisalbertson/PCA9685_Precision_Servo_Driver',
      license='GNU LGPL',
      author_email='albertson.chris@gmail.com',
      packages=['pca9685_psd'],
      py_modules=['pca9685', 'servo'],
      package_data={'': ['*.yaml']},
      install_requires=[
          'smbus2',
          'pyyaml',
          'numpy',
          'matplotlib',
          'scipy',
          'PySimpleGUI'
      ],
      zip_safe=False)
