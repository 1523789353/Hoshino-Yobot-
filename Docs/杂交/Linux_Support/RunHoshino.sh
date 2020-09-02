#!/bin/bash
Reset_path(){
    cd ${0%/*};
};
Main_loop(){
    Reset_path
    python run.py
    echo 将在3秒后自动重启
    sleep 3
    Main_loop
}
Main_loop