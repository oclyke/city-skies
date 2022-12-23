# build esp32 targets

first, follow the instructions in [setup](./setup.md)

then invoke the esp-idf with the following form

``` sh
idf.py -D MICROPY_BOARD=${ board } [-p ${ port }] ${ targets }
```

* ```board```: the name of the supported board
* ```port```: optional, can be used to target flash / erase operations to a particular port
* ```targets```: targets for idf.py, e.g. ```build | flash | erase_flash | monitor | fullclean```

# regenerate frozen python

it is not clear whether changes to python code properly triggers a regeneration of the frozen 
bytecode. for the time being it is simplest to just remove the ```build/genhdr``` and 
```build/frozen_mpy``` directories prior to rebuilding. in the future there may be a more 
efficient way to rebuild frozen mpy files.

you can augment the build command to forecefully remove these dirs ahead of time:

```sh
rm -rf build/genhdr && rm -rf build/frozen_mpy && idf.py -D MICROPY_BOARD=${ board } build
```
