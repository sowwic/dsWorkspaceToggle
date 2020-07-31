import pymel.core as pm
import os
import json


def toggleWorkspace():
    OPTION_VAR = "dsWorkspaceToggle"
    options = pm.optionVar.get(OPTION_VAR, default={"workspaces": []})
    if isinstance(options, basestring):
        options = json.loads(options)

    workspaces = options["workspaces"]  # type: list
    if not options["workspaces"]:
        return

    currentLayout = pm.workspaceLayoutManager(cu=1, q=1)
    if currentLayout not in workspaces:
        nextIndex = 0
    else:
        nextIndex = workspaces.index(currentLayout) + 1
        if nextIndex == len(workspaces):
            nextIndex = 0

    pm.workspaceLayoutManager(sc=workspaces[nextIndex])


def delete_old_hotkey(hotkey_nameCommand):
    hotkey_dir = pm.internalVar(uhk=1)
    current_set_mel = os.path.join(hotkey_dir, "userHotkeys_" + pm.hotkeySet(q=1, current=1) + ".mel")

    with open(current_set_mel, "r") as hotkey_file:
        lines = hotkey_file.readlines()

    with open(current_set_mel, "w") as hotkey_file:
        for each in lines:
            if hotkey_nameCommand not in each:
                hotkey_file.write(each)
        hotkey_file.truncate()
