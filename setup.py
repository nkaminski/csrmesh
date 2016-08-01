from setuptools import setup

setup(name='csrmesh',
        version='0.5.1',
        description='Reverse engineered implementation of the CSRMesh bridge protocol',
        long_description='Reverse engineered implementation of the CSRMesh bridge protocol. Currently only capable of interfacing with Feit HomeBrite smart bulbs but support for additional devices can easily be added. Requires bluez gatttool to transmit packets.',
        url='https://github.com/nkaminski/csrmesh',
        classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Home Automation',
        ],
        keywords='bluetooth csrmesh qualcomm csr BTLE',
        author='Nash Kaminski',
        author_email='nashkaminski@kaminski.io',
        license='GPLv3',
        packages=['csrmesh'],
        install_requires=[
        'pycrypto',
        ],
        scripts=['bin/csrmesh-cli'],
        zip_safe=False)
