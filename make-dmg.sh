mkdir dist/dmg/
cp -r dist/Servo\ Tool.app dist/dmg/
create-dmg \
    --volname "Servo Tool" \
    --volicon icons/feetech-tool.icns \
    --icon "Servo Tool.app" 175 120 \
    --app-drop-link 425 120 \
    "dist/Servo Tool.dmg" \
    dist/dmg
rm -r dist/dmg/
