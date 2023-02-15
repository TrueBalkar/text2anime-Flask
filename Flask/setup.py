from setuptools import find_packages, setup

setup(
    name='text2anime',
    version='1.0.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask', 'pandas', 'numpy', 'laserembeddings', 'nltk', 'Dataframe', 'Model'
    ],
)
