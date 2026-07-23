from setuptools import find_packages, setup
import os 
from glob import glob

package_name = 'jdamr200_gazebo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.py'))),
        # URDF 파일 설치
        (os.path.join('share', package_name, 'urdf'), glob(os.path.join('urdf', '*'))),
        # 월드 파일 설치
        (os.path.join('share', package_name, 'worlds'), glob(os.path.join('worlds', '*.world'))),
        # 컨트롤러 설정 파일 설치
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
        # meshes 폴더 
        (os.path.join('share', package_name, 'models', 'hexa', 'meshes'), 
        glob('models/hexa/meshes/*')), 
        (os.path.join('share', package_name, 'models', 'hexa'), glob(os.path.join('models', 'hexa', 'model.*'))),
        (os.path.join('share', package_name, 'models', 'hexa'), glob(os.path.join('models', 'hexa', '*.sdf'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jdedu',
    maintainer_email='jdedu.kr@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
