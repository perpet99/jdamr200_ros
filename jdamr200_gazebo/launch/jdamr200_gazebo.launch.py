import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_name = 'jdamr200_gazebo'
    pkg_share_dir = get_package_share_directory(pkg_name)
    ros_gz_sim_share_dir = get_package_share_directory('ros_gz_sim')

    # ====================================================================
    # 1. URDF 파일 경로 정의 및 로봇 설명 매개변수 설정
    # ====================================================================
    try:
        jdamr200_urdf = os.path.join(
            get_package_share_directory('jdamr200_description'),
            'urdf',
            'jdamr200.urdf')
        with open(jdamr200_urdf, 'r') as file:
            jdamr200_desc = file.read()
    except EnvironmentError:
        print(f"ERROR: Cannot find URDF file at {jdamr200_urdf}")
        exit(1)

    robot_description = {'robot_description': jdamr200_desc}

    # ====================================================================
    # 2. 필수 환경 변수 및 기타 설정
    # ====================================================================

    # gz-sim(Harmonic)의 모델/리소스 검색 경로 설정
    model_path = os.path.join(pkg_share_dir, 'models')
    set_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[model_path, os.path.pathsep, os.environ.get('GZ_SIM_RESOURCE_PATH', '')]
    )

    # 월드 파일 경로 설정
    world_file = os.path.join(pkg_share_dir, 'worlds', 'jdamr200.world')

    # ====================================================================
    # 3. 노드 실행 (Gazebo(gz-sim), Robot State Publisher, Spawner, ROS-GZ 브릿지)
    # ====================================================================

    # gz-sim 서버+GUI 실행 (월드 로드, '-r'로 즉시 시작)
    start_gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(ros_gz_sim_share_dir, 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={
            'gz_args': f'-r {world_file}',
        }.items(),
    )

    # 로봇의 기구학적 관계(TF)를 발행하는 노드
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description],
    )

    # 모델 스폰 노드 실행 (URDF를 gz-sim으로 로드)
    spawn_robot_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'jdamr200_robot',      # gz-sim 내에서 로봇의 이름
            '-topic', 'robot_description',  # 로봇 모델 설명이 포함된 ROS 토픽 이름
            '-x', '0.0',
            '-y', '0.5',
            '-z', '0.2',
        ],
        output='screen',
    )

    # ROS 2 <-> Gazebo Transport 토픽 브릿지
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        output='screen',
    )

    return LaunchDescription([
        set_model_path,
        start_gz_sim,
        robot_state_publisher_node,
        spawn_robot_node,
        bridge_node,
    ])
