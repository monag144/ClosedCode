#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
if [[ -z "$SDK" ]]; then
  echo "ANDROID_HOME/ANDROID_SDK_ROOT is not set" >&2
  exit 2
fi

PLATFORM="$SDK/platforms/android-34"
BT="$SDK/build-tools/34.0.0"
if [[ ! -f "$PLATFORM/android.jar" ]]; then
  echo "Missing Android 34 platform at $PLATFORM" >&2
  exit 3
fi
if [[ ! -x "$BT/aapt" || ! -x "$BT/d8" || ! -x "$BT/zipalign" || ! -x "$BT/apksigner" ]]; then
  echo "Missing Android build-tools 34.0.0 at $BT" >&2
  exit 4
fi

BUILD="$ROOT/build"
OUT="$ROOT/out"
rm -rf "$BUILD" "$OUT"
mkdir -p "$BUILD/gen" "$BUILD/obj" "$BUILD/dex" "$OUT"

MANIFEST="$ROOT/app/src/main/AndroidManifest.xml"
RES="$ROOT/app/src/main/res"
JAVA="$ROOT/app/src/main/java"

"$BT/aapt" package -f -m \
  -J "$BUILD/gen" \
  -S "$RES" \
  -M "$MANIFEST" \
  -I "$PLATFORM/android.jar"

mapfile -t SOURCES < <(find "$JAVA" "$BUILD/gen" -name '*.java' -type f | sort)
javac --release 11 \
  -classpath "$PLATFORM/android.jar" \
  -d "$BUILD/obj" \
  "${SOURCES[@]}"

mapfile -t CLASSES < <(find "$BUILD/obj" -name '*.class' -type f | sort)
"$BT/d8" --release --min-api 24 \
  --lib "$PLATFORM/android.jar" \
  --output "$BUILD/dex" \
  "${CLASSES[@]}"

"$BT/aapt" package -f \
  -M "$MANIFEST" \
  -S "$RES" \
  -I "$PLATFORM/android.jar" \
  -F "$BUILD/SpeechDuck-unsigned.apk" \
  "$BUILD/dex"

"$BT/zipalign" -f -p 4 \
  "$BUILD/SpeechDuck-unsigned.apk" \
  "$BUILD/SpeechDuck-aligned.apk"

KEYSTORE="$BUILD/speechduck-debug.jks"
keytool -genkeypair -noprompt \
  -keystore "$KEYSTORE" \
  -alias speechduck \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -storepass android -keypass android \
  -dname "CN=Speech Duck Debug, OU=Local Build, O=Speech Duck, L=Salt Lake City, ST=Utah, C=US" >/dev/null 2>&1

"$BT/apksigner" sign \
  --ks "$KEYSTORE" \
  --ks-key-alias speechduck \
  --ks-pass pass:android \
  --key-pass pass:android \
  --out "$OUT/SpeechDuck-v0.1.0.apk" \
  "$BUILD/SpeechDuck-aligned.apk"

"$BT/apksigner" verify --verbose --print-certs "$OUT/SpeechDuck-v0.1.0.apk"
sha256sum "$OUT/SpeechDuck-v0.1.0.apk" | tee "$OUT/SpeechDuck-v0.1.0.apk.sha256"
echo "APK=$OUT/SpeechDuck-v0.1.0.apk"
