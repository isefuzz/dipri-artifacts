#!/bin/bash

# Download subjects

if [ $# -lt 1 ]; then
  echo "<DOWNLOAD-SUBJECTS>: <TARGET_DIR>"
  exit 1
fi

TARGET_DIR="$1"

# Each item: <download_url> <out_filename>
SUBJECTS=(
  "https://github.com/libjpeg-turbo/libjpeg-turbo/archive/refs/tags/2.1.5.1.tar.gz"             "libjpeg-turbo-2.1.5.1.tar.gz"
  "https://sourceforge.net/projects/libpng/files/libpng16/1.6.39/libpng-1.6.39.tar.gz/download" "libpng-1.6.39.tar.gz"
#  "https://github.com/the-tcpdump-group/tcpdump/archive/refs/tags/tcpdump-4.99.3.tar.gz"        "tcpdump-4.99.3.tar.gz"
  "https://github.com/the-tcpdump-group/tcpdump/archive/refs/tags/tcpdump-4.9.0.tar.gz"        "tcpdump-4.9.0.tar.gz"
  "https://ftp.gnu.org/gnu/binutils/binutils-2.40.tar.gz"                                       "binutils-2.40.tar.gz"
  "https://mupdf.com/downloads/archive/mupdf-1.21.1-source.tar.gz"                              "mupdf-1.21.1-source.tar.gz"
#  "https://github.com/GNOME/libxml2/archive/refs/tags/v2.11.4.tar.gz"                           "libxml2-2.11.4.tar.gz"
  "https://github.com/GNOME/libxml2/archive/refs/tags/v2.10.3.tar.gz"                           "libxml2-2.10.3.tar.gz"
  "https://github.com/libming/libming/archive/refs/tags/ming-0_4_8.tar.gz"            "libming-0_4_8.tar.gz"
  "https://github.com/cesanta/mjs/archive/refs/tags/2.20.0.tar.gz"                    "mjs-2.20.0.tar.gz"
  "https://mujs.com/downloads/mujs-1.2.0.tar.gz"                                      "mujs-1.2.0.tar.gz"
  "https://github.com/jasper-software/jasper/archive/refs/tags/version-3.0.6.tar.gz"  "jasper-3.0.6.tar.gz"
  "http://download.osgeo.org/libtiff/tiff-4.4.0.tar.gz"                               "libtiff-4.4.0.tar.gz"
  "https://dl.xpdfreader.com/xpdf-4.04.tar.gz"                                        "xpdf-4.04.tar.gz"
)

pushd "$TARGET_DIR" || exit 1

echo "================================================"
echo "Start to download subjects into $PWD..."
echo "================================================"
echo ""

# ${#SUBJECTS[@]} for arr length
for((i=0;i<${#SUBJECTS[@]};i+=2))
do
  URL=${SUBJECTS[$i]}
  O_NAME=${SUBJECTS[$((i+1))]}

  echo "Download: URL=$URL O_NAME=$O_NAME"
  if [ ! -e "$O_NAME" ]; then
    wget "$URL" -O "./$O_NAME"
  else
    echo "$O_NAME has already existed!"
  fi

  echo "------------------------------------------------"

done;

popd || exit 1

echo "Downloading subjects done."
