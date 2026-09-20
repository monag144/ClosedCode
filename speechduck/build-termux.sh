#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD="$ROOT/build-termux"
OUT="$ROOT/out"
rm -rf "$BUILD"
mkdir -p "$BUILD/gen" "$BUILD/obj" "$BUILD/dex" "$OUT"

SDK_ROOT="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/lib/android-sdk-9123335}}"
ANDROID_JAR=""

if [[ -f "$SDK_ROOT/platforms/android-34/android.jar" ]]; then
  ANDROID_JAR="$SDK_ROOT/platforms/android-34/android.jar"
else
  ANDROID_JAR="$(find "$HOME" -path '*/platforms/android-34/android.jar' -type f 2>/dev/null | head -n 1 || true)"
fi

find_tool() {
  local name="$1"
  local found=""
  found="$(command -v "$name" 2>/dev/null || true)"
  if [[ -n "$found" ]]; then printf '%s' "$found"; return 0; fi
  if [[ -d "$SDK_ROOT/build-tools" ]]; then
    found="$(find "$SDK_ROOT/build-tools" -type f -name "$name" 2>/dev/null | sort -V | tail -n 1 || true)"
  fi
  if [[ -z "$found" ]]; then
    found="$(find "$HOME" -path '*/build-tools/*' -type f -name "$name" 2>/dev/null | sort -V | tail -n 1 || true)"
  fi
  printf '%s' "$found"
}

AAPT2="$(find_tool aapt2)"
D8="$(find_tool d8)"
APKSIGNER="$(find_tool apksigner)"
ZIPALIGN="$(find_tool zipalign)"

for pair in "ANDROID_JAR:$ANDROID_JAR" "AAPT2:$AAPT2" "D8:$D8" "APKSIGNER:$APKSIGNER" "ZIPALIGN:$ZIPALIGN"; do
  key="${pair%%:*}"; val="${pair#*:}"
  if [[ -z "$val" || ! -e "$val" ]]; then
    echo "MISSING_TOOL=$key" >&2
    exit 20
  fi
  echo "$key=$val"
done

MANIFEST="$ROOT/app/src/main/AndroidManifest.xml"
RES="$ROOT/app/src/main/res"
JAVA="$ROOT/app/src/main/java"

"$AAPT2" compile --dir "$RES" -o "$BUILD/resources.zip"

"$AAPT2" link   -o "$BUILD/base.apk"   -I "$ANDROID_JAR"   --manifest "$MANIFEST"   --java "$BUILD/gen"   --min-sdk-version 24   --target-sdk-version 34   --version-code 1   --version-name 0.1.0   "$BUILD/resources.zip"

mapfile -t SOURCES < <(find "$JAVA" "$BUILD/gen" -name '*.java' -type f | sort)
javac --release 11 -classpath "$ANDROID_JAR" -d "$BUILD/obj" "${SOURCES[@]}"

mapfile -t CLASSES < <(find "$BUILD/obj" -name '*.class' -type f | sort)
"$D8" --release --min-api 24 --lib "$ANDROID_JAR" --output "$BUILD/dex" "${CLASSES[@]}"

cp "$BUILD/base.apk" "$BUILD/with-dex.apk"
(
  cd "$BUILD/dex"
  zip -q -u "$BUILD/with-dex.apk" classes*.dex
)

"$ZIPALIGN" -f -p 4 "$BUILD/with-dex.apk" "$BUILD/aligned.apk"

KEYSTORE="$BUILD/speechduck-debug.jks"
keytool -genkeypair -noprompt   -keystore "$KEYSTORE"   -alias speechduck   -keyalg RSA -keysize 2048 -validity 10000   -storepass android -keypass android   -dname "CN=Speech Duck Debug, OU=Local Build, O=Speech Duck, L=Salt Lake City, ST=Utah, C=US" >/dev/null 2>&1

"$APKSIGNER" sign   --ks "$KEYSTORE"   --ks-key-alias speechduck   --ks-pass pass:android   --key-pass pass:android   --out "$OUT/SpeechDuck-v0.1.0.apk"   "$BUILD/aligned.apk"

"$APKSIGNER" verify --verbose --print-certs "$OUT/SpeechDuck-v0.1.0.apk"
sha256sum "$OUT/SpeechDuck-v0.1.0.apk" | tee "$OUT/SpeechDuck-v0.1.0.apk.sha256"

echo "SPEECHDUCK_BUILD_GREEN"
echo "APK=$OUT/SpeechDuck-v0.1.0.apk"
