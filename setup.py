import setuptools
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(base_dir, 'README.md')) as f:
    README = f.read()

setuptools.setup(
    author='NonupleBroken',
    author_email='nonuplebroken@gmail.com',
    name='extend_mt19937_predictor',
    version='19937.0.3',
    description='Extend Mt19937 Predictor',
    long_description=README,
    long_description_content_type='text/markdown',
    license='GPLv3',
    py_modules=['extend_mt19937_predictor'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Security :: Cryptography',
    ],
    url='https://github.com/NonupleBroken/ExtendMT19937Predictor',
    test_suite='tests',
)
