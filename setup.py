from setuptools import setup

setup(
    name="mediasync",
    version="0.1",
    description="Synchronizes user watch list between Emby servers and Jellyfin servers",
    author="broddo",
    python_requires=">=3.7",
    packages=["mediasync"],
    include_package_data=True,
    install_requires=["requests>=2.28.1", "responses>=0.22.0"],
    entry_points={
        "console_scripts": [
            "mediasync = mediasync.mediasyncmain:main",
        ],
    },
    test_suite="unittest.defaultTestLoader.discover",
    test_runner="unittest",
)
