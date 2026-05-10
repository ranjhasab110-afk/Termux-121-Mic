#!/bin/bash
clear
echo -e "\e[1;32m      121 MIC MASTER MENU \e[0m"
echo -e "\e[1;34m-------------------------------\e[0m"
echo "1. Start 121 MIC (Zero Lag)"
echo "2. Stop MIC"
echo "3. Exit"
echo -e "\e[1;34m-------------------------------\e[0m"
read -p "Select an option: " choice

if [ $choice -eq 1 ]; then
    echo "Starting 121 MIC..."
    killall -9 pulseaudio python play 2>/dev/null
    termux-microphone-record -e none -l 0 | play -v 3.5 -t raw -r 44100 -c 1 -b 16 -e signed-integer -
elif [ $choice -eq 2 ]; then
    killall -9 play termux-microphone-record
    echo "MIC Stopped."
else
    exit
fi

