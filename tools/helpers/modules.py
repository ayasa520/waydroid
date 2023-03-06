import glob
import os
import shutil
import tools.config


def remove(path):
    if "*" in path:
        for wildcard_file in glob.glob(path):
            if os.path.exists(wildcard_file):
                if os.path.isdir(wildcard_file):
                    shutil.rmtree(wildcard_file)
                else:
                    os.remove(wildcard_file)
    else:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

def create_modules_dir(dir):
    if not os.path.isdir(os.path.dirname(dir)):
        os.makedirs(os.path.dirname(dir),0o700)
    if not os.path.isdir(dir):
        os.mkdir(dir)
        os.mkdir(dir+"modules")

def collect_modules(dir, partition):
    modules_dir = dir + "/modules"

    if not os.path.isdir(modules_dir):
        return []

    modules = os.listdir(modules_dir)

    def filter(module_dir):
        files = os.listdir(modules_dir + "/" + module_dir)
        if partition in files and "disable" not in files:
            return True
        return False

    mounted=[modules_dir+"/"+dir+"/"+partition for dir in modules if filter(dir)]
    print(mounted)
    return mounted


def get_system_props(modules_dir):
    props = []

    if not os.path.isdir(modules_dir):
        return []

    for module in os.listdir(modules_dir):
        l = os.listdir(modules_dir+"/"+module)
        if "disable" in l or "system.prop" not in l:
            continue
        with open(modules_dir+"/"+module+"/system.prop") as f:
            props.extend(f.read().splitlines())
    return props


def prepare_modules(overlay_modules):
    modules_dir = overlay_modules+"/modules"
    modules_update = overlay_modules+"/modules_update"

    if not os.path.isdir(modules_update):
        return
    for entry in os.listdir(modules_update):
        if os.path.isdir(modules_update+"/"+entry):
            remove(modules_dir+"/"+entry+"/*")
            module_files = os.listdir(modules_update+"/"+entry)
            shutil.copytree(modules_update+"/"+entry,
                            modules_dir+"/"+entry, dirs_exist_ok=True, symlinks=True)
            if "disable" in module_files:
                os.mkdir(modules_dir+"/"+entry+"disable")
            # convert_to_rc(modules_dir+"/"+entry, entry)

    shutil.rmtree(modules_update)


def module_toggle(module_id, action, modules_dir):
    if module_id not in os.listdir(modules_dir):
        return
    module_dir = "{}/{}".format(modules_dir, module_id)
    if action == "enable":
        if os.path.exists(os.path.join(module_dir, "remove")):
            return
        if os.path.exists(os.path.join(module_dir, "disable")):
            os.rmdir(os.path.join(module_dir, "disable"))
    elif action == "disable":
        if os.path.exists(os.path.join(module_dir, "remove")):
            return
        if not os.path.exists(os.path.join(module_dir, "disable")):
            os.mkdir(os.path.join(module_dir, "disable"))
    elif action == "remove":
        if not os.path.exists(os.path.join(module_dir, "remove")):
            os.mkdir(os.path.join(module_dir, "remove"))
    elif action == "restore":
        if os.path.exists(os.path.join(module_dir, "remove")):
            os.rmdir(os.path.join(module_dir, "remove"))
