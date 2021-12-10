from os import listdir, mkdir
from pyrogram import Client
from fumck import config
from fumck.lumd.tgcallsrun.queues import (clear, get, is_empty, put, task_done)
from fumck.lumd.tgcallsrun.downloader import download
from fumck.lumd.tgcallsrun.convert import convert
from fumck.lumd.tgcallsrun.music import run
from fumck.lumd.tgcallsrun.music import smexy as ASS_ACC
smexy = 1
