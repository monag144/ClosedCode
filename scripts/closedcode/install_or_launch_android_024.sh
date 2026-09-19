#!/data/data/com.termux/files/usr/bin/sh
set -u

APK="/sdcard/Download/ClosedCode-cleanroom-v0.2.4-debug.apk"
PKG="com.monag.closedcode.mobile"
EXPECTED="1b4ee68b2f11bb8e359c618860aac99f5bb7d5857fbedfa9182553d1c89df381"

echo "ANDROID_024_INSTALL_HELPER_BEGIN"
test -f "$APK" || { echo "APK_MISSING=YES"; exit 41; }
ACTUAL="$(sha256sum "$APK" | awk '{print $1}')"
echo "APK_SHA256=$ACTUAL"
test "$ACTUAL" = "$EXPECTED" || { echo "APK_HASH_MISMATCH=YES"; exit 42; }

echo "PREINSTALL_PACKAGE_BEGIN"
(pm list packages --user 0 2>&1 | grep -F "$PKG" || true)
echo "PREINSTALL_PACKAGE_END"

echo "PM_INSTALL_ATTEMPT_BEGIN"
set +e
PM_OUT="$(timeout 20s pm install -r --user 0 "$APK" 2>&1)"
PM_RC=$?
set -e
printf '%s\n' "$PM_OUT"
echo "PM_INSTALL_RC=$PM_RC"
echo "PM_INSTALL_ATTEMPT_END"

if [ "$PM_RC" -eq 0 ] && printf '%s' "$PM_OUT" | grep -q "Success"; then
  echo "ANDROID_INSTALL_RESULT=SILENT_INSTALL_GREEN"
  echo "POSTINSTALL_PACKAGE_BEGIN"
  (pm list packages --user 0 2>&1 | grep -F "$PKG" || true)
  echo "POSTINSTALL_PACKAGE_END"
  exit 0
fi

echo "SYSTEM_INSTALLER_LAUNCH_BEGIN"
set +e
OPEN_OUT="$(termux-open --view --content-type application/vnd.android.package-archive "$APK" 2>&1)"
OPEN_RC=$?
set -e
printf '%s\n' "$OPEN_OUT"
echo "TERMUX_OPEN_RC=$OPEN_RC"
echo "SYSTEM_INSTALLER_LAUNCH_END"

if [ "$OPEN_RC" -eq 0 ]; then
  echo "ANDROID_INSTALL_RESULT=SYSTEM_INSTALLER_LAUNCHED"
  exit 0
fi

echo "ANDROID_INSTALL_RESULT=INSTALL_PATH_FAILED"
exit 43
