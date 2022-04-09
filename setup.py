"""Install script."""
from setuptools import setup, find_packages


install_requires = [
    "colorama"
]

extras_require = {
    "freeze":  [
        "pyinstaller",
    ]
}

entry_points = {
    "console_scripts": ["kot = kot.__main__:main"],
}

setup(
    name="kot",
    version="0.2.0",
    description="A very simple C++ builder and runner",
    author="Andrey Zhukov",
    url="https://github.com/andreasxp/kot",
    install_requires=install_requires,
    extras_require=extras_require,
    packages=find_packages(include=[
        "kot",
        "kot.*"
    ]),
    package_data={
        "kot": ["data/*"]
    },
    entry_points=entry_points
)
