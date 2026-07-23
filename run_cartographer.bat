@echo off
rem jdamr200_cartographer(All-in-One SLAM: lidar + cartographer_node + rviz2)를
rem WSL(Ubuntu-24.04, ROS2 Jazzy)에서 실행하는 배치파일
rem 이 파일이 있는 위치를 워크스페이스 루트로 사용합니다.
rem
rem 주의: 실제 라이다 하드웨어(/dev/ttyUSB0)가 필요합니다.
rem       WSL에서 쓰려면 usbipd-win 등으로 USB 장치를 WSL에 연결해야 합니다.

setlocal

rem 이 배치파일의 Windows 경로를 WSL 경로로 변환 (예: D:\...\jdamr200_ros -> /mnt/d/.../jdamr200_ros)
for /f "delims=" %%i in ('wsl -d Ubuntu-24.04 wslpath -a "%~dp0"') do set "WSL_WS_PATH=%%i"

echo WSL workspace path: %WSL_WS_PATH%
echo jdamr200_cartographer SLAM(All-in-One)을 시작합니다. 종료하려면 이 창에서 Ctrl+C를 누르세요.
echo.

wsl -d Ubuntu-24.04 -e bash -c "source /opt/ros/jazzy/setup.bash && cd '%WSL_WS_PATH%' && source install/setup.bash && ros2 launch jdamr200_cartographer cartographer.launch.py"

echo.
echo 종료되었습니다.
pause
