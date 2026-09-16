#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRADLE_VERSION="8.9"
GRADLE_SHA256="d725d707bfabd4dfdc958c624003b3c80accc03f7037b5122c4b1d0ef15cecab"
TOOLS_ROOT="${CLOSEDCODE_AGENT_TOOLS:-$HOME/.local/share/closedcode-agent}"
GRADLE_HOME="$TOOLS_ROOT/gradle-$GRADLE_VERSION"
GRADLE_ZIP="$TOOLS_ROOT/gradle-$GRADLE_VERSION-bin.zip"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/lib/android-sdk-9123335}}"
AAPT2="${CLOSEDCODE_AGENT_AAPT2:-$(command -v aapt2 || true)}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT="$HOME/ClosedCode-Agent-debug-$STAMP.apk"
DOWNLOAD_OUTPUT="/sdcard/Download/ClosedCode-Agent-debug-$STAMP.apk"

mkdir -p "$TOOLS_ROOT"

if [ ! -x "$GRADLE_HOME/bin/gradle" ]; then
    if [ -e "$GRADLE_HOME" ]; then
        echo "RED: existing Gradle directory is incomplete; refusing to overwrite it: $GRADLE_HOME" >&2
        exit 2
    fi

    if [ -f "$GRADLE_ZIP" ]; then
        actual="$(sha256sum "$GRADLE_ZIP" | awk '{print $1}')"
        if [ "$actual" != "$GRADLE_SHA256" ]; then
            echo "RED: existing Gradle archive hash mismatch; refusing to overwrite it" >&2
            echo "Expected: $GRADLE_SHA256" >&2
            echo "Actual:   $actual" >&2
            exit 3
        fi
    else
        echo "Provisioning Gradle $GRADLE_VERSION in the ClosedCode-only tool directory..."
        python - "$GRADLE_ZIP" <<'PY'
from pathlib import Path
import sys
import urllib.request

out = Path(sys.argv[1])
url = "https://services.gradle.org/distributions/gradle-8.9-bin.zip"
with urllib.request.urlopen(url, timeout=60) as response, out.open("xb") as handle:
    while True:
        chunk = response.read(1024 * 1024)
        if not chunk:
            break
        handle.write(chunk)
PY
    fi

    actual="$(sha256sum "$GRADLE_ZIP" | awk '{print $1}')"
    if [ "$actual" != "$GRADLE_SHA256" ]; then
        echo "RED: Gradle archive hash mismatch" >&2
        echo "Expected: $GRADLE_SHA256" >&2
        echo "Actual:   $actual" >&2
        exit 4
    fi

    python - "$GRADLE_ZIP" "$TOOLS_ROOT" <<'PY'
from pathlib import Path
import sys
import zipfile

archive = Path(sys.argv[1])
out = Path(sys.argv[2])
target = out / "gradle-8.9"
if target.exists():
    raise SystemExit("refusing to overwrite existing Gradle directory")
with zipfile.ZipFile(archive) as zf:
    zf.extractall(out)
PY
    chmod 700 "$GRADLE_HOME/bin/gradle"
fi

if [ ! -d "$SDK/platforms/android-34" ]; then
    echo "RED: Android SDK platform 34 not found under $SDK" >&2
    exit 5
fi
if [ -z "$AAPT2" ] || [ ! -x "$AAPT2" ]; then
    echo "RED: Termux-compatible aapt2 not found" >&2
    exit 6
fi

echo "GRADLE=$GRADLE_HOME/bin/gradle"
echo "SDK=$SDK"
echo "AAPT2=$AAPT2"

export ANDROID_HOME="$SDK"
export ANDROID_SDK_ROOT="$SDK"

cd "$HERE"
"$GRADLE_HOME/bin/gradle" \
    --no-daemon \
    -Pandroid.aapt2FromMavenOverride="$AAPT2" \
    assembleDebug

APK="$HERE/app/build/outputs/apk/debug/app-debug.apk"
if [ ! -f "$APK" ]; then
    echo "RED: Gradle completed but debug APK is missing" >&2
    exit 7
fi

if [ -e "$OUTPUT" ]; then
    echo "RED: timestamped output already exists; refusing overwrite: $OUTPUT" >&2
    exit 8
fi
cp "$APK" "$OUTPUT"
chmod 600 "$OUTPUT"
SHA="$(sha256sum "$OUTPUT" | awk '{print $1}')"

echo "APK_BUILD=GREEN"
echo "PACKAGE=com.monag.closedcode.agent"
echo "APK=$OUTPUT"
echo "SHA256=$SHA"

if [ -d /sdcard/Download ]; then
    if [ -e "$DOWNLOAD_OUTPUT" ]; then
        echo "DOWNLOAD_COPY=SKIPPED_EXISTING"
    else
        cp "$OUTPUT" "$DOWNLOAD_OUTPUT"
        echo "DOWNLOAD_COPY=GREEN"
        echo "DOWNLOAD_APK=$DOWNLOAD_OUTPUT"
    fi
fi

echo "APK_INSTALL=NOT_ATTEMPTED"
