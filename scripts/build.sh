#!/bin/bash
# Helper script to create a new release locally

set -e

# Get version from addon.xml
VERSION=$(grep '<addon' addon.xml | grep -oP 'version="\K[^"]+')
echo "Building version $VERSION"

# Clean build directory
rm -rf build
mkdir -p build/script.kodigithublogs
mkdir -p repo/script.kodigithublogs

# Copy addon files
rsync -av \
  --exclude='.git' \
  --exclude='.github' \
  --exclude='repo' \
  --exclude='build' \
  --exclude='repository.kodigithublogs' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='scripts' \
  . build/script.kodigithublogs/

# Create addon zip
cd build
zip -r "script.kodigithublogs-${VERSION}.zip" script.kodigithublogs
cd ..

# Copy to repo
cp "build/script.kodigithublogs-${VERSION}.zip" repo/script.kodigithublogs/

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

# Create repository zip (from parent directory to include folder structure)
zip -r build/repository.kodigithublogs.zip repository.kodigithublogs

echo ""
echo "Build complete!"
echo "Addon zip: build/script.kodigithublogs-${VERSION}.zip"
echo "Repository zip: build/repository.kodigithublogs.zip"
echo ""
echo "To create a release, commit changes and push with tag:"
echo "  git add repo/"
echo "  git commit -m 'Release ${VERSION}'"
echo "  git tag ${VERSION}"
echo "  git push origin main --tags"
