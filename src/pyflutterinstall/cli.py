"""
Runs the installer

When this is done, the directory structure will look like this
sdk/Android:
    build-tools
    cmdline-tools
    emulator       # Generated by the Android SDK Manager
    flutter
    java
    licenses       # Generated by the Android SDK Manager
    patcher        # Generated by the Android SDK Manager
    platforms      # Generated by the Android SDK Manager
    platform-tools # Generated by the Android SDK Manager
    system-images  # Generated by the Android SDK Manager
    tools          # Generated by the Android SDK Manager
"""

# pylint: disable=missing-function-docstring,consider-using-with,disable=invalid-name,subprocess-run-check
# pylint: disable=wrong-import-position

import argparse
import os
import shutil
import sys
from typing import Callable

# if --install-dir is specified, add it to the path
try:
    install_dir_found = sys.argv.index("--install-dir") + 1
    install_dir = sys.argv[install_dir_found]
    print(f"Setting install location to '{install_dir}'")
    os.chdir(install_dir)  # Do this early before any other imports
except BaseException:  # pylint: disable=broad-except
    pass

# isort: off
# black: off
from pyflutterinstall.flutter_doctor import postinstall_run_flutter_doctor
from pyflutterinstall.install.android_sdk import install_android_sdk
from pyflutterinstall.install.ant_sdk import install_ant_sdk
from pyflutterinstall.install.chrome import install_chrome
from pyflutterinstall.install.flutter_sdk import install_flutter_sdk
from pyflutterinstall.install.gradle import install_gradle
from pyflutterinstall.install.java_sdk import install_java_sdk
from pyflutterinstall.resources import (
    INSTALL_DIR,
    JAVA_SDK_VERSIONS,
    ANDROID_SDK,
    GRADLE_DIR,
)
from pyflutterinstall.util import make_dirs
from pyflutterinstall.config import config_load, config_save


# black: on
# isort: on

JAVA_VERSION = 21


def ask_if_interactive(
    is_interactive: bool, callback_name: str, callback: Callable[[], int]
) -> int:
    if not is_interactive:
        return callback()
    do_install = input(f"install {callback_name} (y/n)? ") == "y"
    if not do_install:
        return 0
    return callback()


def check_preqs() -> None:
    if shutil.which("git") is None:
        print("Git is not installed, please install, add it to the path then continue.")
        sys.exit(1)
    if sys.platform == "linux":
        if shutil.which("ninja") is None:
            print(
                "Ninja is not installed, please install, add it to the path then continue."
            )
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Installs Flutter Dependencies")
    parser.add_argument(
        "--skip-confirmation",
        "-y",
        action="store_true",
        help="Skip confirmation",
        default=False,
    )
    # Note that --install-dir is handled at the import level
    parser.add_argument("--install-dir", help="Install directory", default=None)
    parser.add_argument("--skip-java", action="store_true", help="Skip Java SDK")
    parser.add_argument("--skip-android", action="store_true", help="Skip Android SDK")
    parser.add_argument("--skip-ant", action="store_true", help="Skip Ant")
    parser.add_argument("--skip-flutter", action="store_true", help="Skip Flutter SDK")
    parser.add_argument("--skip-chrome", action="store_true", help="Skip Chrome")
    parser.add_argument(
        "--java-version",
        help="Java version to install",
        default=11,
        choices=JAVA_SDK_VERSIONS.keys(),
    )
    args = parser.parse_args()
    check_preqs()
    any_skipped = any(
        [args.skip_java, args.skip_android, args.skip_flutter, args.skip_chrome]
    )
    print(
        f"This will install Flutter and its dependencies into {os.path.basename(INSTALL_DIR)}"
    )
    skip_confirmation = (
        args.skip_confirmation or input("auto-accept all? (y/n): ").lower() == "y"
    )
    interactive = not skip_confirmation
    print("\nInstalling Flutter SDK and dependencies\n")
    config = config_load()
    config.update(
        {
            "ANDROID_SDK": str(ANDROID_SDK),
            "GRADLE_DIR": str(GRADLE_DIR),
            "INSTALL_DIR": str(INSTALL_DIR),
            "JAVA_DIR": str(INSTALL_DIR / "java"),
        }
    )
    config_save(config)
    make_dirs()
    if not args.skip_java:

        def install_java_sdk_version() -> int:
            return install_java_sdk(JAVA_VERSION)

        ask_if_interactive(interactive, "java_sdk", install_java_sdk_version)
    if not args.skip_android:

        def install_android_sdk_and_gradle():
            install_android_sdk(interactive)
            install_gradle()

        ask_if_interactive(
            interactive,
            "android_sdk",
            install_android_sdk_and_gradle,
        )
    if not args.skip_ant:
        install_ant_sdk()
    if not args.skip_flutter:
        ask_if_interactive(
            interactive, "flutter", lambda: install_flutter_sdk(interactive)
        )
    if not args.skip_chrome:
        ask_if_interactive(interactive, "chrome", install_chrome)
    if not args.skip_flutter:
        postinstall_run_flutter_doctor()
    if not any_skipped:
        print("\nDone installing Flutter SDK and dependencies\n")
    if sys.platform == "win32":
        print("Please restart your terminal to apply the changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())