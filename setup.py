#!/usr/bin/python

from setuptools import setup
import distutils.command.install_scripts
import shutil

f = open('README')
long_description = f.read().strip()
f.close()

# idea from http://stackoverflow.com/a/11400431/2139420
class strip_py_ext(distutils.command.install_scripts.install_scripts):
    def run(self):
        distutils.command.install_scripts.install_scripts.run(self)
        for script in self.get_outputs():
            if script.endswith(".py"):
                shutil.move(script, script[:-3])


setup(
    name="igwtop",
    version="0.1a",
    description="'top' like performance tool for ceph iscsi gateway nodes",
    long_description=long_description,
    author="Paul Cuzner",
    author_email="pcuzner@redhat.com",
    url="http://github.com/pcuzner/igwtop",
    license="GPLv3",
    packages=[
        "collectors",
        "config",
        "igwtopUI",
        "utils"
        ],
    scripts=[
        'igwtop.py'
    ],
    cmdclass = {
        "install_scripts" : strip_py_ext
    }
)
