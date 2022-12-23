#!/usr/bin/env bash

# this script is meant to automate the export of build results

ESPTOOL=esptool.py
CHIP=esp32
APP=app

while getopts p:d: flag
do
  case "${flag}" in
    p) PORT=${OPTARG};;
    d) DIR=${OPTARG};;
  esac
done

#check inputs
if [ -z "$PORT" ]; then echo "PORT (-p) must be provided" && exit 1; fi
if [ -z "$DIR" ]; then echo "DIR (-d) must be provided" && exit 1; fi

${ESPTOOL} \
  --chip ${CHIP} \
  -p ${PORT} \
  -b 460800 \
  --before=default_reset \
  --after=hard_reset \
  write_flash \
  --flash_mode dio \
  --flash_freq 40m \
  --flash_size 4MB \
  0x1000 ${DIR}/bootloader/bootloader.bin \
  0x10000 ${DIR}/${APP}.bin \
  0x8000 ${DIR}/partition_table/partition-table.bin \
  0xd000 ${DIR}/ota_data_initial.bin
