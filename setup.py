from setuptools import setup

setup(name='testbench',
      version='0.1',
      description='Integration Testing with Python and VirtualBox ',
      url='https://github.com/aheck/testbench',
      author='Andreas Heck',
      author_email='aheck@gmx.de',
      license='MIT',
      packages=['testbench'],
      install_requires = ['pyvbox', 'paramiko'],
      zip_safe=False)
