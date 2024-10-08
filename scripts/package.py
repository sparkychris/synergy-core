#!/usr/bin/env python3

import lib.env as env

env.ensure_in_venv(__file__)

import platform
from lib.linux import PackageType
from dotenv import load_dotenv  # type: ignore

env_file = ".env"
default_package_prefix = "synergy"


def main():

    load_dotenv(dotenv_path=env_file)

    version = env.get_app_version()
    filename_base = get_filename_base(version)
    print(f"Package filename base: {filename_base}")

    if env.is_windows():
        windows_package(filename_base)
    elif env.is_mac():
        mac_package(filename_base)
    elif env.is_linux():
        linux_package(filename_base, version)
    else:
        raise RuntimeError(f"Unsupported platform: {env.get_os()}")


def get_filename_base(version, use_linux_distro=True):
    os = env.get_os()
    machine = platform.machine().lower()
    package_base = env.get_env("SYNERGY_PACKAGE_PREFIX", default=default_package_prefix)

    if os == "linux" and use_linux_distro:
        distro_name, _distro_like, distro_version = env.get_linux_distro()
        if not distro_name:
            raise RuntimeError("Failed to detect Linux distro")

        if distro_version:
            version_for_filename = distro_version.replace(".", "_")
            distro = f"{distro_name}-{version_for_filename}"
        else:
            distro = distro_name

        return f"{package_base}-{distro}-{machine}-{version}"
    else:
        # some windows users get confused by 'amd64' and think it's 'arm64',
        # so we'll use intel's 'x64' branding (even though it's wrong).
        if machine == "amd64":
            machine = "x64"

        return f"{package_base}-{os}-{machine}-{version}"


def windows_package(filename_base):
    import lib.windows as windows

    windows.package(filename_base)


def mac_package(filename_base):
    import lib.mac as mac

    mac.package(filename_base)


def linux_package(filename_base, version):
    import lib.linux as linux

    extra_packages = env.get_env_bool("LINUX_EXTRA_PACKAGES", False)

    linux.package(filename_base, PackageType.DISTRO)

    if extra_packages:
        filename_base = get_filename_base(version, use_linux_distro=False)
        linux.package(filename_base, PackageType.TGZ)


if __name__ == "__main__":
    main()
