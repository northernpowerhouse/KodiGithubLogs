#!/bin/bash
# Helper script to create a new release locally

set -e

# Get version from addon.xml
VERSION=$(grep '<addon' addon.xml | grep -oP 'version="\K[^"]+')
echo "Building version $VERSION"

# Clean build directory
rm -rf build
mkdir -p build/script.kodiloguploader
mkdir -p repo/script.kodiloguploader

# Copy addon files
rsync -av \
  --exclude='.git' \
  --exclude='.github' \
  --exclude='repo' \
  --exclude='build' \
  --exclude='repository.kodiloguploader' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='scripts' \
  . build/script.kodiloguploader/

# Create addon zip
cd build
zip -r "script.kodiloguploader-${VERSION}.zip" script.kodiloguploader
cd ..

# Copy to repo
cp "build/script.kodiloguploader-${VERSION}.zip" repo/script.kodiloguploader/

# Update addons.xml
cat > repo/addons.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<addons>
EOF

sed '1d' addon.xml >> repo/addons.xml

cat >> repo/addons.xml << 'EOF'
</addons>
EOF

# Generate MD5
md5sum repo/addons.xml | awk '{print $1}' > repo/addons.xml.md5

# Create repository zip
cd repository.kodiloguploader
zip -r ../build/repository.kodiloguploader.zip .
cd ..

echo ""
echo "Build complete!"
echo "Addon zip: build/script.kodiloguploader-${VERSION}.zip"
echo "Repository zip: build/repository.kodiloguploader.zip"
echo ""
echo "To create a release, commit changes and push with tag:"
echo "  git add repo/"
echo "  git commit -m 'Release v${VERSION}'"
echo "  git tag v${VERSION}"
echo "  git push origin main --tags"
