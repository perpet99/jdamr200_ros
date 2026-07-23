
## jdAMR200 Gazebo 시뮬레이션용 Launch 파일 설명서

### 1. 개요

이 문서는 `jdAMR200` 로봇을 **Gazebo(gz-sim, Harmonic)** 시뮬레이터에 스폰하고, 키보드/토픽으로 구동하며 라이다·IMU 센서 데이터를 확인하기 위한 `jdamr200_gazebo.launch.py`의 사용법을 설명한다.

> ⚠️ 이 패키지는 **ROS2 Jazzy(Ubuntu 24.04) 기준 새 Gazebo(gz-sim/Harmonic)** 를 사용한다.
> Gazebo Classic(`gazebo_ros`, `gzserver`/`gzclient`)은 Jazzy부터 공식 지원이 종료되어 사용하지 않는다.
> ROS2 Humble(Ubuntu 22.04) 환경이라면 이 launch 파일은 그대로 동작하지 않으며, Gazebo Classic 기반의 별도 버전이 필요하다.

---

### 2. 사전 준비

#### 1) 필수 패키지 설치

```bash
sudo apt install ros-jazzy-ros-gz-sim ros-jazzy-ros-gz-bridge ros-jazzy-robot-state-publisher
```

#### 2) WSL(Windows) 사용 시 GUI(WSLg) 확인

Gazebo GUI 창이 떠야 하므로 WSLg가 정상 동작해야 한다. 아래 명령으로 확인할 수 있다.

```bash
ls /mnt/wslg/.X11-unix/    # X0 소켓이 보여야 정상
```

X0 소켓이 보이지 않으면 Windows 쪽에서 `wsl --shutdown` 후 WSL을 다시 시작한다.

#### 3) 빌드 및 환경 설정

```bash
cd ~/jdamr200_ws
colcon build --symlink-install
source install/setup.bash
```

---

### 3. 실행 방법

```bash
ros2 launch jdamr200_gazebo jdamr200_gazebo.launch.py
```

실행하면 다음이 순서대로 뜬다:

1. **gz-sim 서버 + GUI** — `jdamr200_gazebo/worlds/jdamr200.world` 월드 로드 (`hexa` 모델 포함), 물리 시뮬레이션 즉시 시작(`-r`)
2. **robot_state_publisher** — URDF 기반 TF 트리 퍼블리시
3. **ros_gz_sim create** — `/robot_description` 토픽을 읽어 로봇을 `jdamr200_robot`이라는 이름으로 월드에 스폰 (스폰 후 프로세스는 정상 종료됨)
4. **ros_gz_bridge parameter_bridge** — ROS2 ↔ Gazebo Transport 토픽 브릿지

---

### 4. Launch 파일 구성요소 설명

#### 1) URDF 로딩 및 `robot_description` 파라미터

```python
jdamr200_urdf = os.path.join(
    get_package_share_directory('jdamr200_description'),
    'urdf', 'jdamr200.urdf')
with open(jdamr200_urdf, 'r') as file:
    jdamr200_desc = file.read()
robot_description = {'robot_description': jdamr200_desc}
```

#### 2) 모델 리소스 경로 설정

```python
SetEnvironmentVariable(
    name='GZ_SIM_RESOURCE_PATH',
    value=[model_path, os.pathsep, os.environ.get('GZ_SIM_RESOURCE_PATH', '')]
)
```

* `jdamr200_gazebo/models` 아래의 커스텀 모델(`hexa` 등)을 gz-sim이 `model://` URI로 찾을 수 있도록 경로를 추가한다.
* Gazebo Classic의 `GAZEBO_MODEL_PATH`에 대응하는 gz-sim 전용 환경 변수다.

#### 3) gz-sim 실행

```python
IncludeLaunchDescription(
    PythonLaunchDescriptionSource([
        os.path.join(ros_gz_sim_share_dir, 'launch', 'gz_sim.launch.py')
    ]),
    launch_arguments={'gz_args': f'-r {world_file}'}.items(),
)
```

* `ros_gz_sim`의 표준 launch 파일을 통해 gz-sim 서버+GUI를 한 번에 실행한다.
* `-r`은 월드를 로드하자마자 일시정지 없이 바로 시뮬레이션을 시작하라는 옵션이다.

#### 4) 로봇 스폰

```python
Node(
    package='ros_gz_sim',
    executable='create',
    arguments=['-name', 'jdamr200_robot', '-topic', 'robot_description',
               '-x', '0.0', '-y', '0.5', '-z', '0.2'],
)
```

* Gazebo Classic의 `spawn_entity.py`에 대응하는 gz-sim 전용 스폰 노드다.

#### 5) ROS2 ↔ Gazebo 토픽 브릿지

```python
Node(
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
)
```

브릿지 문법: `TOPIC@ROS_TYPE@GZ_TYPE`(양방향), `]`는 ROS→Gazebo 단방향, `[`는 Gazebo→ROS 단방향을 의미한다.

| 토픽 | 방향 | 설명 |
| --- | --- | --- |
| `/cmd_vel` | ROS → Gazebo | 속도 명령 (DiffDrive 플러그인이 소비) |
| `/odom` | Gazebo → ROS | 휠 오도메트리 |
| `/tf` | Gazebo → ROS | odom → base_footprint 변환 |
| `/scan` | Gazebo → ROS | 라이다 스캔 (`laser_link` 프레임) |
| `/imu/data` | Gazebo → ROS | IMU 센서 데이터 |
| `/joint_states` | Gazebo → ROS | 바퀴 조인트 상태 |
| `/clock` | Gazebo → ROS | 시뮬레이션 시간 |

---

### 5. 동작 확인

#### 1) 토픽 확인

```bash
ros2 topic list
ros2 topic echo /scan --once
ros2 topic echo /odom --once
```

#### 2) 키보드로 구동

```bash
# 다른 터미널에서
ros2 run jdamr200_teleop jdamr_teleop
```

또는 토픽으로 직접 테스트:

```bash
ros2 topic pub -r 10 -t 3 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.3}}'
```

`/odom`의 `pose.pose.position.x`가 증가하면 정상 동작하는 것이다.

---

### 6. 디버깅 팁

* **로봇이 안 보이거나 안 움직이면**: `gz topic -i -t /odom`으로 publisher가 존재하는지 먼저 확인한다. Publisher가 없다면 로봇 엔티티 스폰이 실패했거나, 동시에 여러 개의 gz-sim 인스턴스가 떠서 같은 `/world/default/...` 네임스페이스를 충돌시키고 있을 가능성이 높다 — Gazebo Transport는 ROS2 도메인 ID 같은 프로세스 격리가 없어서, 같은 이름의 월드를 띄운 여러 `gz sim` 프로세스가 서로 토픽을 공유/충돌한다.
* **launch를 껐는데 GUI가 안 꺼지면**: `ros2 launch`를 `Ctrl+C`나 `timeout`으로 종료해도 하위 `gz sim server`/`gz sim gui` 프로세스가 간혹 살아남는다. `ps aux | grep 'gz sim'`으로 확인 후 필요하면 `kill -9`로 정리한다.
* **센서 프레임이 이상하면**: URDF에서 `laser_joint`처럼 센서가 달린 fixed joint에 `<disableFixedJointLumping>`이 빠지면, gz-sim이 fixed joint로 연결된 링크들을 하나로 합쳐버려 `/scan`의 `frame_id`가 `laser_link`가 아닌 엉뚱한 링크 이름으로 나온다.

---

### 7. 관련 패키지 및 파일 구조

| 파일/패키지 | 설명 |
| --- | --- |
| `jdamr200_description/urdf/jdamr200.urdf` | 로봇 모델 정의 (gz-sim용 `<gazebo>` 플러그인 포함) |
| `jdamr200_gazebo/worlds/jdamr200.world` | 시뮬레이션 월드 (gz-sim 시스템 플러그인, ground/sun, hexa 모델) |
| `jdamr200_gazebo/models/hexa` | 커스텀 정적 모델 |
| `jdamr200_gazebo/launch/jdamr200_gazebo.launch.py` | gz-sim 실행, 스폰, ROS-GZ 브릿지 |
| `ros_gz_sim`, `ros_gz_bridge` | 새 Gazebo(gz-sim)와 ROS2를 연결하는 표준 패키지 |
