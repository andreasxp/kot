"""Install script."""
from setuptools import setup, find_packages
from setuptools.command.egg_info import egg_info


# See https://stackoverflow.com/a/66443941/9118363 for explanation
class egg_info_ex(egg_info):
    """Includes license file into `.egg-info` folder."""

    def run(self):
        # don't duplicate license into `.egg-info` when building a distribution
        if not self.distribution.have_run.get('install', True):
            # `install` command is in progress, copy license
            self.mkpath(self.egg_info)
            self.copy_file('LICENSE.txt', self.egg_info)

        egg_info.run(self)


install_requires = [
    "appdirs",
    "colorama",
    "requests",
    "click"
]

extras_require = {
    "test": "pytest"
}

entry_points = {
    "console_scripts": ["kot = kot.__main__:main"],
}

setup(
    name="kot",
    version="0.3.1",
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
    entry_points=entry_points,
    license_files=["LICENSE.txt"],
    cmdclass={"egg_info": egg_info_ex},
)
