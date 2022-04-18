"""Install script."""
from setuptools import setup, find_packages


install_requires = [
    "appdirs",
    "colorama",
    "requests",
]

entry_points = {
    "console_scripts": ["kot = kot.__main__:main"],
}

setup(
    name="kot",
    version="0.3.0",
    description="A very simple C++ builder and runner",
    author="Andrey Zhukov",
    url="https://github.com/andreasxp/kot",
    install_requires=install_requires,
    packages=find_packages(include=[
        "kot",
        "kot.*"
    ]),
    package_data={
        "kot": ["data/*"]
    },
    entry_points=entry_points
)
