from setuptools import _install_setup_requires, find_packages, setup 

setup(
    name='strava_app',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[ 
        'flask',
    ],
)