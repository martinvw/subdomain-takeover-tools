import os
import sys

from setuptools import setup, find_packages


def get_metadata():
    import re
    with open(os.path.join("subdomain_takeover_tools", "__init__.py")) as f:
        return dict(re.findall("__([a-z]+)__ = ['\"]([^'\"]+)['\"]", f.read()))


def update_version(target_version):
    with open(os.path.join("subdomain_takeover_tools", "__init__.py"), 'w') as f:
        for key, value in metadata.items():
            if key == 'version':
                value = target_version

            f.write("__%s__ = '%s'\n" % (key, value))


metadata = get_metadata()

if sys.argv[-1] == 'publish':
    # os.system('cd docs && make html')
    os.system('rm -rf dist')
    os.system('rm -rf build')
    os.system('python3 -m build')

    sys.stdout.write('Continue with publishing and committing? ')
    input()

    print("Uploading release to pypi:")
    os.system("python3 -m twine upload --repository pypi dist/subdomain_takeover_tools-%s* " % metadata['version'])

    print("Tagging:")
    os.system("git tag -a %s -m 'version %s'" % (metadata['version'], metadata['version']))
    os.system("git push --tags")

    print("Upgrading dev version:")
    from bump import SemVer

    version = SemVer.parse(metadata['version'])
    version.bump(minor=True, reset=True)
    update_version(str(version))
    os.system("git add subdomain_takeover_tools/__init__.py")
    os.system("git commit -m \"New development version\"")
    os.system("git push")

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
                                      'confirm_azure_app_service=subdomain_takeover_tools.confirm_azure_app_service'
                                      ':main',
                                      'confirm_azure_traffic_manager=subdomain_takeover_tools'
                                      '.confirm_azure_traffic_manager:main',
                                      'extract_domain_names=subdomain_takeover_tools.extract_domain_names:main',
                                      'authoritative_resolve=subdomain_takeover_tools.authoritative_resolve:main',
                                      'subtake_enrich_and_export=subdomain_takeover_tools.subtake_enrich_and_export'
                                      ':main',
                                      ]},
    include_package_data=True,
    install_requires=[
        'tldextract',
        'dnspython',
        'boto3',
        'azure-identity',
        'azure-mgmt-trafficmanager'
    ],
    extras_require={
        'dev': [
            'bump'
        ]
    },
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
