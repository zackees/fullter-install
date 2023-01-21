"""
Contains the install functions for the various components
"""

# pylint: disable=missing-function-docstring,consider-using-with,disable=invalid-name,subprocess-run-check,line-too-long

import os
import shutil


from pyflutterinstall.resources import (
    FLUTTER_GIT_DOWNLOAD,
    ANDROID_SDK,
    FLUTTER_TARGET,
)

from pyflutterinstall.util import (
    execute,
    make_title,
)

from pyflutterinstall.setenv import add_env_path


def install_flutter_sdk() -> None:
    make_title("Installing Flutter")
    if shutil.which("git") is None:
        error_msg = "'git' not found in path"
        error_msg += "\npath = \n"
        for path in os.environ["PATH"].split(os.path.pathsep):
            error_msg += f"  {path}\n"
        raise FileNotFoundError(error_msg)
    print(f"Install Flutter from {FLUTTER_GIT_DOWNLOAD} to {FLUTTER_TARGET}")
    if not FLUTTER_TARGET.exists():
        execute(f'{FLUTTER_GIT_DOWNLOAD} "{FLUTTER_TARGET}"', ignore_errors=False)
    else:
        print(f"Flutter already installed at {FLUTTER_TARGET}")
    if not os.path.exists(FLUTTER_TARGET):
        print(
            f"!!!!!!!!!!!!! FLUTTER FOLDER {FLUTTER_TARGET} DOES NOT EXIST EITHER !!!!!!!!!!!!!!!"
        )
        path = os.environ["PATH"]
        error_msg = f"Could not find {FLUTTER_TARGET} in path"
        error_msg += "\npath = \n"
        for path in path.split(os.pathsep):
            error_msg += f"  {path}\n"
        raise FileNotFoundError(error_msg)
    # Add flutter to path
    add_env_path(FLUTTER_TARGET / "bin")
    execute(
        f'flutter config --android-sdk "{ANDROID_SDK}" --no-analytics',
        send_confirmation="y\n",
        ignore_errors=False,
    )
    execute(
        "flutter doctor --android-licenses",
        send_confirmation="y\n",
        ignore_errors=False,
    )

    print("Flutter installed.\n")