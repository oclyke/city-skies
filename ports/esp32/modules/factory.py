def factory_reset():
    import config
    import pathutils

    print("Factory Reset... ", end="")
    pathutils.rmdirr(config.EPHEMERAL_DIR)
    print("done")
