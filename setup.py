# coding: utf8

from setuptools import setup, find_packages


setup(
    name="Gonsole",
    version="0.1",
    description="console for Golang",
    author="yeyuexia",
    author_email="yyxworld@gmail.com",
    url="https://github.com/yeyuexia/gonsole",
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': ['gonsole = gonsole.gonsole:execute']
    },
    install_requires=[
        "requests>=2.8.1"
    ]
)
