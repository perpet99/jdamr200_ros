# jdAMR200 ROS2 패키지 

## 📁 Repository Structure

```
jdamr200_ros/
├── jdamr200_description/      # URDF 기반 로봇 모델 패키지 (RViz 시각화 용도)
├── jdamr200_node/             # 임베디드 보드(Arduino/ESP32)와의 통신 노드
├── jdamr200_teleop/           # 키보드 입력을 받아 cmd_vel 발행 (teleop 노드)
├── jdamr200_bringup/          # 여러 노드를 실행하기 위한 launch 파일들
├── jdamr200_cartographer/     # Cartographer 기반 SLAM 패키지
└── lidar_sl_ros2/             # LP14 LDlidar ROS2 드라이버 (외부 제공)
```

### 🔧 패키지 설명

* **`jdamr200_description`**
  URDF 파일을 통해 jdAMR200 로봇의 시각적 모델을 정의합니다. RViz에서 사용됩니다.

* **`jdamr200_node`**
  Arduino 또는 ESP32와 직렬 통신을 통해 실제 하드웨어를 제어합니다.

  * **기능**:

    * `/cmd_vel` 토픽 수신 → 모터 제어
    * IMU, 엔코더 데이터 수신 및 ROS 토픽으로 발행

* **`jdamr200_teleop`**
  키보드 입력을 받아 `/cmd_vel` 메시지를 발행하는 노드입니다.

  * 키보드로 로봇을 원격 조종할 수 있습니다.

* **`jdamr200_bringup`**
  실행 편의를 위한 launch 파일을 포함합니다.

  * URDF 모델을 RViz에 로딩
  * Lidar 및 통신 노드 실행 등 자동화

* **`jdamr200_cartographer`**
  2D SLAM을 위한 Cartographer 구성을 포함합니다.

  * Lidar 데이터를 이용해 자율주행 맵 생성 가능

* **`lidar_sl_ros2`**
  LP14 LDlidar용 ROS2 드라이버 패키지입니다.

  * 외부에서 제공된 드라이버를 포함

---

## 🚀 Installation

```bash
# 1. 워크스페이스 생성
mkdir -p ~/jdamr200_ws/src
cd ~/jdamr200_ws/src

# 2. 본 레포지토리 복제
git clone https://github.com/JD-edu/jdamr200_ros.git .

# 3. 의존성 설치 (선택 사항)
rosdep install --from-paths . --ignore-src -r -y

# 4. 빌드
cd ~/jdamr200_ws
colcon build

# 5. 환경 설정
source install/setup.bash
```

---

## ⚙️ 사용 방법

### 1. 모터 제어 및 키보드 텔레옵 실행

```bash
# 터미널 1: 하드웨어 통신 노드 실행
ros2 run jdamr200_node jdamr200_node

# 터미널 2: 키보드 조작으로 cmd_vel 발행
ros2 run jdamr200_teleop jdamr_teleop
```

* `jdamr200_node`는 `/cmd_vel`을 수신하여 로봇의 바퀴를 제어합니다.
* `jdamr200_teleop`은 키보드 입력을 받아 `/cmd_vel`을 발행합니다.

### 2. RViz에서 로봇 모델 시각화

```bash
ros2 launch jdamr200_bringup jdamr200_urdf_launch.py
```

### 3. Gazebo 시뮬레이션 (ROS2 Jazzy / gz-sim)

```bash
ros2 launch jdamr200_gazebo jdamr200_gazebo.launch.py
```

* gz-sim(Harmonic) 시뮬레이터에 로봇을 스폰하고, `/cmd_vel`로 구동하며 `/scan`, `/imu/data`, `/odom` 등의 센서 토픽을 확인할 수 있습니다.
* 자세한 사전 준비 및 트러블슈팅은 [jdamr200_gazebo/how_to_use_jdamr200_gazebo_launch.md](jdamr200_gazebo/how_to_use_jdamr200_gazebo_launch.md)를 참고하세요.

### 4. Cartographer로 지도 생성 및 저장

Gazebo 시뮬레이션(또는 실제 로봇 + 라이다)을 주행시키면서 Cartographer SLAM으로 지도를 만들고 저장합니다.

```bash
# 터미널 1: Gazebo 시뮬레이션 실행 (실제 로봇이라면 이 단계 대신 라이다/모터 노드를 실행)
ros2 launch jdamr200_gazebo jdamr200_gazebo.launch.py

# 터미널 2: Cartographer SLAM + RViz 실행
ros2 launch jdamr200_cartographer cartographer_gazebo.launch.py

# 터미널 3: 키보드로 로봇을 돌아다니게 하며 지도를 채운다
ros2 run jdamr200_teleop jdamr_teleop
```

지도가 충분히 만들어졌으면(RViz에서 `/map`을 확인하며) 아래 명령으로 저장합니다.

```bash
# 워크스페이스 루트에서 실행 (maps 디렉터리에 저장하는 예시)
mkdir -p maps
ros2 run nav2_map_server map_saver_cli -f maps/jdamr200_map
```

* `maps/jdamr200_map.pgm`(지도 이미지), `maps/jdamr200_map.yaml`(해상도/원점 등 메타데이터) 두 파일이 생성됩니다.
* Windows 배치파일: [run_gazebo.bat](run_gazebo.bat)로 시뮬레이션을, 별도 터미널에서 `wsl -d Ubuntu-24.04`로 접속해 위 명령들을 실행해도 됩니다.
* 실제 로봇(하드웨어)에서 지도를 만들 때는 `jdamr200_cartographer/launch/cartographer.launch.py`(라이다 노드 포함, All-in-One 방식)를 사용하세요. `cartographer_gazebo.launch.py`는 Gazebo 전용입니다 — Gazebo는 `/scan`, `/odom`, `/tf`를 이미 제공하므로 라이다 노드나 별도 TF 발행 없이 `cartographer_node`, `occupancy_grid_node`, `rviz2`만 실행합니다.

### 5. 저장한 지도로 자율주행 (Nav2)

저장된 지도를 이용해 Nav2 스택으로 목표 지점까지 자율주행할 수 있습니다.

```bash
# 터미널 1: Gazebo 시뮬레이션 실행 (Cartographer는 필요 없음 — 지도가 이미 있으므로)
ros2 launch jdamr200_gazebo jdamr200_gazebo.launch.py

# 터미널 2: Nav2 bringup (저장한 지도로 로컬라이제이션 + 경로계획/추종)
ros2 launch nav2_bringup bringup_launch.py \
    map:=/절대/경로/maps/jdamr200_map.yaml \
    use_sim_time:=true
```

RViz(별도로 `rviz2 -d $(ros2 pkg prefix nav2_bringup)/share/nav2_bringup/rviz/nav2_default_view.rviz`로 실행하거나, 기존 RViz 창에 `Navigation2` 관련 디스플레이를 추가)에서:

1. **2D Pose Estimate** 툴로 로봇의 현재 위치/방향을 지도 위에 대략 클릭해 알려줍니다. (AMCL이 초기 위치를 받아야 `map` 프레임을 발행하기 시작합니다.)
2. **2D Goal Pose** 툴로 목표 지점을 클릭하면 로봇이 자율주행으로 이동합니다.

CLI로 직접 테스트하려면:

```bash
# 초기 위치 지정 (로봇의 대략적인 현재 위치)
ros2 topic pub -t 1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
  '{header: {frame_id: map}, pose: {pose: {position: {x: 0.0, y: 0.5, z: 0.0}, orientation: {w: 1.0}}}}'

# 목표 지점으로 이동 지시
ros2 topic pub -t 1 /goal_pose geometry_msgs/msg/PoseStamped \
  '{header: {frame_id: map}, pose: {position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}'
```

* `nav2_bringup`의 기본 파라미터 파일(`/opt/ros/jazzy/share/nav2_bringup/params/nav2_params.yaml`)을 그대로 사용합니다. 로봇 반경/최대 속도 등을 이 로봇에 맞게 튜닝하려면 `params_file:=<커스텀 yaml 경로>` 인자로 별도 파라미터 파일을 지정하세요.
* 필요한 패키지: `ros-jazzy-navigation2`, `ros-jazzy-nav2-bringup`, `ros-jazzy-nav2-map-server` (`sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup`)
* 실제 로봇에서 실행할 때는 `use_sim_time:=false`로 바꾸고, Gazebo 실행 단계 대신 실제 라이다/모터 노드를 띄우세요.
