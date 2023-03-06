# Copyright 2023 Takanashi Rikka
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import shutil
import time
import zipfile
import glob
import tools.config
import tools.helpers.props
import tools.helpers.ipc
import tools.helpers.lxc
from tools.interfaces import IPlatform
from tools.interfaces import IStatusBarService
import dbus


def install(args):
    try:
        cm = tools.helpers.ipc.DBusContainerService()
        session = cm.GetSession()

        if session["state"] == "FROZEN":
            cm.Unfreeze()
        tmp_dir = session["modules"] + "/modules_tmp"
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        zip_dir = tmp_dir + "/base.zip"
        shutil.copyfile(args.MODULE, zip_dir)
        # platformService = IPlatform.get_service(args)
        # if platformService:
        #     platformService.installApp("/data/waydroid_tmp/base.apk")
        # else:
        #     logging.error("Failed to access IPlatform service")

        # 好像不需要, instasll.sh 已经有同样的逻辑
        # zip_file = zipfile.ZipFile(zip_dir)
        # if "module.prop" in zip_file.namelist():
        #     def not_empty(s):
        #         return s and s.strip()
        #     c = filter(not_empty,zip_file.read("module.prop").decode().split("\n"))
        #     module_prop={ k:v for k,v in [tuple(a.split("=")) for a in list(c)]}
        #     print(module_prop)
        # else:
        #     print("module.prop not found!")
        #     return
        # module_id =  module_prop["id"]
        # module_dir = tools.config.session_defaults["modules"] + "/modules" + module_id
        # remove(module_dir + "/*")

        # zip_file.extractall(module_dir)
        # zip_file.close()

        with open(tools.config.tools_src +
               "/data/scripts/installer.sh") as f:
            args.command_string = True
            INSTALLER_CONTENT = f.read()
            BUSYBOX_LINK = "/data/adb/overlay_modules/bin/busybox --install /data/adb/overlay_modules/bin;"
            INSTALL_MODULE_SCRIPT = BUSYBOX_LINK + INSTALLER_CONTENT+"\n"+"install_module"+"\n"+"exit 0"+"\n"
            args.COMMAND = ["export PATH=/data/adb/overlay_modules/bin:$PATH;export ZIPFILE=/data/adb/overlay_modules/modules_tmp/base.zip;export OUTFD=1;export ASH_STANDALONE=1","\n", INSTALL_MODULE_SCRIPT]
        tools.helpers.lxc.shell(args)

        # os.remove(zip_dir)

        if session["state"] == "FROZEN":
            cm.Freeze()
    except (dbus.DBusException, KeyError) as e:
        logging.error("WayDroid session is stopped")
