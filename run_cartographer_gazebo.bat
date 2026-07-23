@echo off
rem Gazebo(gz-sim) 시뮬레이션 + Cartographer SLAM 연동 실행 배치파일
rem 1) 새 콘솔 창에서 jdamr200_gazebo 시뮬레이션을 띄우고
rem 2) 이 창에서 cartographer_gazebo.launch.py(SLAM + rviz2)를 실행합니다.
rem
rem 실제 라이다 하드웨어가 필요 없습니다 (Gazebo가 /scan, /odom, /tf를 제공).

setlocal

for /f "delims=" %%i in ('wsl -d Ubuntu-24.04 wslpath -a "%~dp0"') do set "WSL_WS_PATH=%%i"

echo WSL workspace path: %WSL_WS_PATH%

rem 이전에 남아있을 수 있는 gz-sim / cartographer / rviz2 프로세스 정리
echo 기존에 남아있는 프로세스를 정리합니다...
wsl -d Ubuntu-24.04 -e bash -c "pkill -9 -f 'ros2 launch jdamr200_gazebo' 2>/dev/null; pkill -9 -f 'ros2 launch jdamr200_cartographer' 2>/dev/null; pkill -9 -f 'gz sim' 2>/dev/null; pkill -9 -f 'ros_gz_bridge/parameter_bridge' 2>/dev/null; pkill -9 -f cartographer_node 2>/dev/null; pkill -9 -f cartographer_occupancy_grid_node 2>/dev/null; pkill -9 -f rviz2 2>/dev/null; exit 0"

echo.
echo [1/2] Gazebo(gz-sim) 시뮬레이션을 새 창에서 시작합니다...
start "jdamr200 Gazebo Simulation" wsl -d Ubuntu-24.04 -e bash -c "source /opt/ros/jazzy/setup.bash && cd '%WSL_WS_PATH%' && source install/setup.bash && ros2 launch jdamr200_gazebo jdamr200_gazebo.launch.py"

echo Gazebo 및 로봇 스폰이 끝날 때까지 잠시 대기합니다...
timeout /t 10 /nobreak >nul

echo.
echo [2/2] Cartographer SLAM + RViz 를 이 창에서 시작합니다. 종료하려면 Ctrl+C를 누르세요.
echo       (Gazebo 창은 따로 닫아야 합니다)
echo.

wsl -d Ubuntu-24.04 -e bash -c "source /opt/ros/jazzy/setup.bash && cd '%WSL_WS_PATH%' && source install/setup.bash && ros2 launch jdamr200_cartographer cartographer_gazebo.launch.py"

echo.
echo Cartographer가 종료되었습니다. (Gazebo 창은 별도로 닫아주세요)
pause
