import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # jdamr200_gazebo.launch.py가 /clock을 브릿지하므로 기본값을 true로 둔다.
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    jdamr200_cartographer_prefix = get_package_share_directory('jdamr200_cartographer')
    jdamr200_config_dir = LaunchConfiguration(
        'jdamr200_config_dir',
        default=os.path.join(jdamr200_cartographer_prefix, 'config'))

    # body_link가 아닌 base_footprint(URDF 실제 루트 프레임)를 tracking/published frame으로 쓰는 설정
    configuration_basename = LaunchConfiguration(
        'configuration_basename', default='jdamr200_gazebo.lua')

    resolution = LaunchConfiguration('resolution', default='0.05')
    publish_period_sec = LaunchConfiguration('publish_period_sec', default='1.0')

    cartographer_launch_file_dir = os.path.join(
        jdamr200_cartographer_prefix, 'launch')

    rviz2_config = os.path.join(
        jdamr200_cartographer_prefix, 'rviz2', 'cartographer.rviz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument(
            'cartographer_config_dir',
            default_value=jdamr200_config_dir,
            description='Full path to config file to load'),
        DeclareLaunchArgument(
            'configuration_basename',
            default_value=configuration_basename,
            description='Name of lua file for cartographer'),
        DeclareLaunchArgument(
            'resolution',
            default_value=resolution,
            description='Resolution of a grid cell in the published occupancy grid map'),
        DeclareLaunchArgument(
            'publish_period_sec',
            default_value=publish_period_sec,
            description='OccupancyGrid publishing period'),

        # 주의: 라이다 노드, robot_state_publisher, odom/TF 관련 정적 변환은 여기서 만들지 않는다.
        # jdamr200_gazebo.launch.py를 먼저 실행하면 /scan, /odom, /tf(odom->base_footprint),
        # robot_state_publisher(base_footprint->base_link->laser_link)가 이미 모두 제공된다.

        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=['-configuration_directory', jdamr200_config_dir,
                       '-configuration_basename', configuration_basename]
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [cartographer_launch_file_dir, '/occupancy_grid.launch.py']),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'resolution': resolution,
                'publish_period_sec': publish_period_sec,
            }.items(),
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2_cartographer',
            output='screen',
            arguments=['-d', rviz2_config],
            parameters=[{'use_sim_time': use_sim_time}],
        ),
    ])
