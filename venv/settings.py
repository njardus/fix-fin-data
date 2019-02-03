from loguru import logger

debug = False

iterationlimit = 1000

data_path = """..\\data\\"""
prefix = "fixed-"

fixingmargin = 0.70

def getdebug():
    return debug

def data_path():
    logger.info(f"Data path returned from settings: {data_path}")
    return data_path

def prefix():
    return prefix

def errormargin():
    return fixingmargin

def iterlimit():
    if getdebug():
        return iterationlimit
    else:
        return 0

