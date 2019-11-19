from setuptools import setup, find_packages

setup(
    name="sippy",
    version="1.1",
    packages=find_packages(),

    install_requires=[
        'twisted>=14.0',
        'requests-futures>=1.0'
    ],

    dependency_links=[
        'git+https://github.com/sobomax/libelperiodic'
    ],

    package_data={
        '': ['dictionary', '*.md']
    },
    test_suite='tests',

    entry_points={
        'console_scripts': [
            'b2bua = sippy.b2bua_num:main_func'
        ],
    },

    # meta-data for upload to PyPi
    author="Sippy Software, Inc.",
    author_email="sales@sippysoft.com",
    description="SIP RFC3261 Back-to-back User Agent (B2BUA)",
    license="BSD",
    keywords="sip b2bua voip rfc3261 sippy",
    url="http://www.b2bua.org/",
)
