from setuptools import setup, find_packages

setup(
    name="tikzgrapher",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "networkx", "pygame"  # Add dependencies here
    ],
)
