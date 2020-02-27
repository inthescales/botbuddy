from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='botbuddy',
    version='0.1.0',
    description='Facilitates posting text to social media accounts.',
    long_description=readme,
    author='Robin Hill',
    author_email='robin@inthescales.com',
    url='https://github.com/inthescales/botbuddy',
    license=license,
    packages=find_packages()
)
