#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
    DESTDIR_ARG="--root=$DESTDIR"
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/src/vision_opencv/cv_bridge"

# snsure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/install/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/install/lib/python2.7/dist-packages:/home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/build/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/build" \
    "/usr/bin/python" \
    "/home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/src/vision_opencv/cv_bridge/setup.py" \
    build --build-base "/home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/build/vision_opencv/cv_bridge" \
    install \
    $DESTDIR_ARG \
    --install-layout=deb --prefix="/home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/install" --install-scripts="/home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/install/bin"
