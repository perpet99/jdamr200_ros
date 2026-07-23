@echo off
rem jdamr200_teleop(jdamr_teleop) 키보드 조작 노드를 WSL(Ubuntu-24.04, ROS2 Jazzy)에서 실행하는 배치파일
rem 이 파일이 있는 위치를 워크스페이스 루트로 사용합니다.

setlocal

rem 이 배치파일의 Windows 경로를 WSL 경로로 변환 (예: D:\...\jdamr200_ros -> /mnt/d/.../jdamr200_ros)
for /f "delims=" %%i in ('wsl -d Ubuntu-24.04 wslpath -a "%~dp0"') do set "WSL_WS_PATH=%%i"

echo WSL workspace path: %WSL_WS_PATH%
echo 키보드로 cmd_vel 을 발행합니다. 종료하려면 이 창에서 Ctrl+C를 누르세요.
echo.

wsl -d Ubuntu-24.04 -e bash -c "source /opt/ros/jazzy/setup.bash && cd '%WSL_WS_PATH%' && source install/setup.bash && ros2 run jdamr200_teleop jdamr_teleop"

echo.
echo 종료되었습니다.
pause
