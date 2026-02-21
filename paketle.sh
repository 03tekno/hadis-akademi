#!/bin/bash

# Değişkenler
APP_NAME="hadis-akademi"
VERSION="1.0"
BUILD_DIR="build_pkg"

echo "--- Debian Paket Hazırlama Başladı ---"

# 1. Temizlik ve Klasör Yapısı
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/DEBIAN
mkdir -p $BUILD_DIR/usr/bin
mkdir -p $BUILD_DIR/opt/$APP_NAME
mkdir -p $BUILD_DIR/usr/share/applications
mkdir -p $BUILD_DIR/usr/share/pixmaps

# 2. Dosyaları Kopyala
echo "Dosyalar kopyalanıyor..."
cp hadis-akademi.py $BUILD_DIR/opt/$APP_NAME/main.py
cp hdslr.json $BUILD_DIR/opt/$APP_NAME/
cp serh.json $BUILD_DIR/opt/$APP_NAME/
cp hadis.png $BUILD_DIR/usr/share/pixmaps/$APP_NAME.png

# 3. Control Dosyası Oluştur
cat <<EOT > $BUILD_DIR/DEBIAN/control
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-pyqt6
Maintainer: mt
Description: Akademik Hadis Araştırma Kütüphanesi
 Modern temalı ve geniş kapsamlı hadis araştırma uygulaması.
EOT

# 4. Çalıştırıcı Script Oluştur (/usr/bin/hadis-akademi)
cat <<EOT > $BUILD_DIR/usr/bin/$APP_NAME
#!/bin/bash
cd /opt/$APP_NAME && python3 main.py "\$@"
EOT
chmod +x $BUILD_DIR/usr/bin/$APP_NAME

# 5. Masaüstü Kısayolu (.desktop) Oluştur
cat <<EOT > $BUILD_DIR/usr/share/applications/$APP_NAME.desktop
[Desktop Entry]
Name=Hadis Akademi
Comment=Hadis Araştırma Kütüphanesi
Exec=/usr/bin/$APP_NAME
Icon=$APP_NAME
Terminal=false
Type=Application
Categories=Education;
EOT

# 6. İzinleri Ayarla ve Paketle
chmod -R 755 $BUILD_DIR/DEBIAN
echo "Paket oluşturuluyor..."
dpkg-deb --build $BUILD_DIR ${APP_NAME}_${VERSION}_all.deb

# 7. Temizlik
rm -rf $BUILD_DIR

echo "--- İşlem Tamamlandı! ---"
echo "Dosya: ${APP_NAME}_${VERSION}_all.deb"