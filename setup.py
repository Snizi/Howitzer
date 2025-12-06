from setuptools import setup, find_packages

setup(
    name="howitzer",
    version="1.0.0",
    description="A security tool to detect authorization bypass vulnerabilities by replaying Burp Suite requests.",
    author="Howitzer Team",
    packages=find_packages(),
    py_modules=['howitzer'],
    entry_points={
        'console_scripts': [
            'howitzer=howitzer:main',
        ],
    },
    install_requires=[
        'requests>=2.25.0',
        'PyYAML>=5.4.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
    ],
)
