import setuptools

setuptools.setup(
    name="pydave4vm",
    version="1",
    url="https://github.com/Chicrala/pydave4vm",

    author="Andre Chicrala",
    author_email="andrechicrala@gmail.com",

    description="An attempt to make a working version in python of the dave4vm software that was originally written in IDL. ",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
