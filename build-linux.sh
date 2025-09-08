pyinstaller --name 'Servo-Tool' --icon 'icons/feetech-tool.png' --add-data icons/feetech-tool.png:icons/ --windowed --onefile main.py
mkdir -p dist/Servo-Tool.AppDir/usr/bin
cp -f dist/Servo-Tool dist/Servo-Tool.AppDir/usr/bin
ln -sf dist/Servo-Tool.AppDir/usr/bin dist/AppRun
cp -f Servo-Tool.desktop dist/Servo-Tool.AppDir/
cp -f icons/feetech-tool.png dist/Servo-Tool.AppDir/Servo-Tool.png
cd dist
appimagetool Servo-Tool.AppDir/

