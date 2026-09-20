#!/usr/bin/env bash
set -euo pipefail

: "${GROUP:?JitPack GROUP is required}"
: "${ARTIFACT:?JitPack ARTIFACT is required}"
: "${VERSION:?JitPack VERSION is required}"

yes | sdkmanager --licenses >/dev/null 2>&1 || true
sdkmanager "platforms;android-34" "build-tools;34.0.0"

bash speechduck/build.sh

M2_DIR="$HOME/.m2/repository/${GROUP//.//}/$ARTIFACT/$VERSION"
mkdir -p "$M2_DIR"

# JitPack reliably serves the primary Maven JAR. The bytes are the signed APK
# unchanged; only the repository filename uses .jar. Consumers can rename it .apk.
cp speechduck/out/SpeechDuck-v0.1.0.apk "$M2_DIR/$ARTIFACT-$VERSION.jar"
cp speechduck/out/SpeechDuck-v0.1.0.apk "$M2_DIR/$ARTIFACT-$VERSION.apk"

cat > "$M2_DIR/$ARTIFACT-$VERSION.pom" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>$GROUP</groupId>
  <artifactId>$ARTIFACT</artifactId>
  <version>$VERSION</version>
  <packaging>jar</packaging>
  <name>Speech Duck APK build artifact</name>
</project>
EOF

echo "JITPACK_SPEECHDUCK_PUBLISHED=$M2_DIR/$ARTIFACT-$VERSION.jar"
