#!/data/data/com.termux/files/usr/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
BUILD="$ROOT/build"
OUT_NAME="ClosedCode-cleanroom-v0.2.5-debug.apk"

find_sdk() {
  if [ -n "${ANDROID_HOME:-}" ] && [ -d "$ANDROID_HOME/platforms" ]; then
    printf '%s\n' "$ANDROID_HOME"
    return
  fi
  for candidate in "$HOME"/lib/android-sdk-* "$HOME/Android/Sdk" "$PREFIX"/share/android-sdk; do
    [ -d "$candidate/platforms" ] || continue
    printf '%s\n' "$candidate"
    return
  done
  return 1
}

SDK="$(find_sdk || true)"
if [ -z "$SDK" ]; then
  echo "BUILD_STATUS=RED"
  echo "REASON=ANDROID_SDK_NOT_FOUND"
  exit 10
fi

ANDROID_JAR="$SDK/platforms/android-34/android.jar"
if [ ! -f "$ANDROID_JAR" ]; then
  ANDROID_JAR="$(find "$SDK/platforms" -name android.jar -type f 2>/dev/null | sort -V | tail -n 1)"
fi
if [ ! -f "$ANDROID_JAR" ]; then
  echo "BUILD_STATUS=RED"
  echo "REASON=ANDROID_JAR_NOT_FOUND"
  exit 11
fi

BUILD_TOOLS="$(find "$SDK/build-tools" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -V | tail -n 1)"
AAPT2="$(command -v aapt2 2>/dev/null || true)"
[ -n "$AAPT2" ] || AAPT2="$BUILD_TOOLS/aapt2"
D8="$BUILD_TOOLS/d8"
APKSIGNER="$BUILD_TOOLS/apksigner"
ZIPALIGN="$(command -v zipalign 2>/dev/null || true)"
[ -n "$ZIPALIGN" ] || ZIPALIGN="$BUILD_TOOLS/zipalign"
BASH_BIN="$(command -v bash 2>/dev/null || true)"

for tool in "$AAPT2" "$D8" "$APKSIGNER" "$ZIPALIGN" "$BASH_BIN"; do
  if [ ! -x "$tool" ]; then
    echo "BUILD_STATUS=RED"
    echo "REASON=MISSING_TOOL:$tool"
    exit 12
  fi
done

rm -rf "$BUILD"
mkdir -p "$BUILD/compiled" "$BUILD/gen" "$BUILD/classes" "$BUILD/dex"

find "$ROOT/res" -type f | sort | while IFS= read -r resource; do
  "$AAPT2" compile "$resource" -o "$BUILD/compiled"
done

set -- "$BUILD"/compiled/*.flat
"$AAPT2" link \
  -o "$BUILD/resources.apk" \
  --manifest "$ROOT/AndroidManifest.xml" \
  -I "$ANDROID_JAR" \
  --java "$BUILD/gen" \
  --min-sdk-version 26 \
  --target-sdk-version 34 \
  --version-code 17 \
  --version-name "0.2.5-cleanroom" \
  --auto-add-overlay \
  "$@"

find "$ROOT/src" "$BUILD/gen" -name '*.java' -type f | sort > "$BUILD/sources.list"
javac \
  -encoding UTF-8 \
  -source 17 \
  -target 17 \
  -classpath "$ANDROID_JAR" \
  -d "$BUILD/classes" \
  @"$BUILD/sources.list"

jar cf "$BUILD/classes.jar" -C "$BUILD/classes" .
"$D8" --min-api 26 --lib "$ANDROID_JAR" --output "$BUILD/dex" "$BUILD/classes.jar"

cp "$BUILD/resources.apk" "$BUILD/unsigned.apk"
for dex in "$BUILD"/dex/*.dex; do
  [ -f "$dex" ] || continue
  jar uf "$BUILD/unsigned.apk" -C "$BUILD/dex" "$(basename "$dex")"
done

"$ZIPALIGN" -f 4 "$BUILD/unsigned.apk" "$BUILD/aligned.apk"

KEY_DIR="$ROOT/.debug"
KEYSTORE="$KEY_DIR/closedcode-debug.keystore"
mkdir -p "$KEY_DIR"
if [ ! -f "$KEYSTORE" ]; then
  keytool -genkeypair \
    -keystore "$KEYSTORE" \
    -storepass android \
    -keypass android \
    -alias closedcode \
    -dname "CN=ClosedCode Cleanroom Debug,O=ClosedCode" \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    >/dev/null 2>&1
  chmod 600 "$KEYSTORE"
fi

"$BASH_BIN" "$APKSIGNER" sign \
  --ks "$KEYSTORE" \
  --ks-key-alias closedcode \
  --ks-pass pass:android \
  --key-pass pass:android \
  --out "$BUILD/$OUT_NAME" \
  "$BUILD/aligned.apk"

"$BASH_BIN" "$APKSIGNER" verify --verbose "$BUILD/$OUT_NAME" >/dev/null

SHARED_OUT="/sdcard/Download/$OUT_NAME"
cp "$BUILD/$OUT_NAME" "$SHARED_OUT"

echo "BUILD_STATUS=GREEN"
echo "SDK=$SDK"
echo "ANDROID_JAR=$ANDROID_JAR"
echo "BUILD_TOOLS=$BUILD_TOOLS"
echo "AAPT2=$AAPT2"
echo "ZIPALIGN=$ZIPALIGN"
echo "PACKAGE=com.monag.closedcode.mobile"
echo "VERSION_NAME=0.2.5-cleanroom"
echo "APK=$SHARED_OUT"
echo "APK_BYTES=$(wc -c < "$SHARED_OUT")"
echo "APK_SHA256=$(sha256sum "$SHARED_OUT" | awk '{print $1}')"
