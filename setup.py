from setuptools import setup, find_packages

requires = [
    'flask',
    'spotipy',
    'html5lib',
    'requests',
    'requests_html',
    'pathlib',
]

setup(name="Spotify KeepUp",
    version='1.0',
    description='An application that creates user-tailored playlists on Spotify',
    keywords='web flask',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires
)