rm -rf log
DISPLAY=:0.0 ./xproxy > log &
ps -all
