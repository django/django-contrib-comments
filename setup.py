from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

long_description = readme + history

setup(
    name='django-contrib-comments',
    version='2.2.0',
    url="https://github.com/django/django-contrib-comments",
    description='The code formerly known as django.contrib.comments.',
    long_description=long_description,
    author='Django Software Foundation',
    author_email='jacob@jacobian.org',
    license='BSD',
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    test_suite='tests.runtests.main',
    install_requires=['Django>=2.2']
)
