from setuptools import setup, find_packages

requires = [
    'flask',
    'spotipy',
    'html5lib',
    'requests',
    'requests_html',
    'beautifulsoup4',
    'youtube-dl',
    'pathlib',
    'pandas'
]

setup(name="SpotifyPlaylistConverter",
    version='1.0',
    description='An application that converts Spotify playlist to YouTube version',
    keywords='web flask',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires
)