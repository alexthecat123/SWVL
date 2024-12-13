#!/bin/bash

arduino-cli compile --fqbn arduino:avr:uno && arduino-cli upload --fqbn arduino:avr:uno -p /dev/ttyUSB0
