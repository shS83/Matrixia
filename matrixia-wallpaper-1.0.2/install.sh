#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.local/share/plasma/wallpapers/io.shs.matrixia"
CONFIG_FILE="${HOME}/.config/matrixia.conf"

mkdir -p "$(dirname -- "${TARGET_DIR}")" "$(dirname -- "${CONFIG_FILE}")"
rm -rf -- "${TARGET_DIR}"
cp -a -- "${SOURCE_DIR}/io.shs.matrixia" "${TARGET_DIR}"

if [[ ! -f "${CONFIG_FILE}" ]]; then
	cp -- "${SOURCE_DIR}/matrixia.conf" "${CONFIG_FILE}"
fi

printf 'Installed Matrixia wallpaper to:\n  %s\n' "${TARGET_DIR}"
printf 'Configuration file:\n  %s\n' "${CONFIG_FILE}"
printf '\nRestart Plasma after updating the QML source:\n'
printf '  systemctl --user restart plasma-plasmashell.service\n'
printf '\nThen choose Matrixia in Desktop and Wallpaper settings.\n'
