import os
import sys

from setuptools import setup, find_packages


def get_metadata():
    import re
    with open(os.path.join("subdomain_takeover_tools", "__init__.py")) as f:
        return dict(re.findall("__([a-z]+)__ = ['\"]([^'\"]+)['\"]", f.read()))


metadata = get_metadata()

if sys.argv[-1] == 'publish':
    # os.system('cd docs && make html')
    os.system('python setup.py sdist')

    print("You probably want to upload it to pypi:")
    print("  twine upload dist/* -p")

    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (metadata['version'], metadata['version']))
    print("  git push --tags")
    sys.exit()

try:
    long_description = open("README.md", "r").read()
except Exception:
    long_description = None

setup(
    name='subdomain_takeover_tools',
    version=metadata['version'],
    packages=find_packages(),
    url='https://github.com/martinvw/subdomain-takeover-tools',
    license='MIT',
    author='Martin van Wingerden',
    author_email='info@martinvw.nl',
    description='Some helper subdomain_takeover_tools to validate subdomain takeovers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={'console_scripts': ['confirm_elb=subdomain_takeover_tools.confirm_elb:main',
                                      'confirm_s3=subdomain_takeover_tools.confirm_s3:main',
                                      'confirm_shopify=subdomain_takeover_tools.confirm_shopify:main',
                                      'extract_domain_names=subdomain_takeover_tools.extract_domain_names:main',
                                      ]},
    include_package_data=True,
    install_requires=[
        'tldextract',
        'dnspython',
        'boto3'
    ],
    keywords=['subdomain-takeover', 'subtake', 'elb', 's3', 'shopify'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Development Status :: 4 - Beta',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
)
