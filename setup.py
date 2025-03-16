from setuptools import setup, find_packages

setup(
    name="shcs",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Cors',
        'Flask-SocketIO',
        'PyJWT',
        'redis',
        'bcrypt',
        'python-dotenv',
        'PyMySQL',
        'Werkzeug',
        'ultralytics',
        'opencv-python',
        'numpy',
        'eventlet',
        'cryptography',
        'Flask-Limiter',
        'requests'
    ],
    python_requires='>=3.8',
) 