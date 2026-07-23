@echo off
rem jdamr200_gazebo.launch.py 를 WSL(Ubuntu-24.04, ROS2 Jazzy)에서 실행하는 배치파일
rem 이 파일이 있는 위치를 워크스페이스 루트로 사용합니다.

setlocal

rem 이 배치파일의 Windows 경로를 WSL 경로로 변환 (예: D:\...\jdamr200_ros -> /mnt/d/.../jdamr200_ros)
for /f "delims=" %%i in ('wsl -d Ubuntu-24.04 wslpath -a "%~dp0"') do set "WSL_WS_PATH=%%i"

echo WSL workspace path: %WSL_WS_PATH%

rem 이전 실행에서 남아있을 수 있는 gz-sim / 브릿지 / launch 프로세스 정리
rem (Ctrl+C나 타임아웃으로 종료해도 gz sim 하위 프로세스가 간혹 orphan으로 남는 문제 대응)
echo 기존에 남아있는 시뮬레이션 프로세스를 정리합니다...
wsl -d Ubuntu-24.04 -e bash -c "pkill -9 -f 'ros2 launch jdamr200_gazebo' 2>/dev/null; pkill -9 -f 'gz sim' 2>/dev/null; pkill -9 -f 'ros_gz_bridge/parameter_bridge' 2>/dev/null; pkill -9 -f 'ros_gz_sim/create' 2>/dev/null; exit 0"

echo Gazebo(gz-sim) 시뮬레이션을 시작합니다. 종료하려면 이 창에서 Ctrl+C를 누르세요.
echo.

wsl -d Ubuntu-24.04 -e bash -c "source /opt/ros/jazzy/setup.bash && cd '%WSL_WS_PATH%' && source install/setup.bash && ros2 launch jdamr200_gazebo jdamr200_gazebo.launch.py"

rem 종료 후에도 gz sim 하위 프로세스가 남는 경우가 있어 한 번 더 정리
wsl -d Ubuntu-24.04 -e bash -c "pkill -9 -f 'ros2 launch jdamr200_gazebo' 2>/dev/null; pkill -9 -f 'gz sim' 2>/dev/null; pkill -9 -f 'ros_gz_bridge/parameter_bridge' 2>/dev/null; exit 0"

echo.
echo 종료되었습니다.
pause
