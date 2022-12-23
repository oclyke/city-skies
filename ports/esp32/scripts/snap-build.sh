#!/usr/bin/env bash

# this script is meant to automate the export of build results

while getopts t:b:c:o: flag
do
  case "${flag}" in
    t) tag=${OPTARG};;
    b) build=${OPTARG};;
    o) outdir=${OPTARG};;
    c) clean='true';;
  esac
done

if [ -z "$tag" ]; then echo "tag (-t) must be provided" && exit 1; fi
if [ -z "$build" ]; then echo "build (-b) must be provided" && exit 1; fi
if [ -z "$outdir" ]; then echo "outdir (-o) must be provided" && exit 1; fi

# machinery
remove_dir () {
  dir=$1
  rm -rf $dir
}

make_dir () {
  dir=$1
  mkdir -p $dir
}

copy () {
  from=$1
  to=$2
  cp $from $to
}

# main functionality
outpath=$outdir/$tag

remove_dir $outpath
if [ -z ${clean+x} ]; then echo "removed $outpath"; else echo "cleaning $outpath" && exit 0; fi

make_dir $outpath
make_dir $outpath/bootloader
make_dir $outpath/partition_table

# copy blobs
copy $build/micropython.bin $outpath/app.bin
copy $build/bootloader/bootloader.bin $outpath/bootloader/bootloader.bin
copy $build/partition_table/partition-table.bin $outpath/partition_table/partition-table.bin
copy $build/ota_data_initial.bin $outpath/ota_data_initial.bin

echo "snapshot of $name $ver from $build saved at $outpath"

