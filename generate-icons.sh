#!/bin/bash
# Skrypt generujący ikony PNG z pliku lumen.svg

# Źródłowa ikona (SVG)
SRC="data/icons/lumen.svg"

# Folder docelowy
DEST="data/icons/hicolor"

# Rozmiary ikon, które chcemy wygenerować
SIZES=(16 32 48 64 128 256)

# Sprawdź czy mamy narzędzie rsvg-convert (pakiet librsvg2-bin)
if ! command -v rsvg-convert &> /dev/null
then
    echo "[ERROR] Brak programu rsvg-convert. Zainstaluj go poleceniem:"
    echo "sudo apt install librsvg2-bin"
    exit 1
fi

# Generowanie ikon
for SIZE in "${SIZES[@]}"
do
    mkdir -p "$DEST/${SIZE}x${SIZE}/apps"
    rsvg-convert -w $SIZE -h $SIZE "$SRC" > "$DEST/${SIZE}x${SIZE}/apps/lumen.png"
    echo "[OK] Wygenerowano ${SIZE}x${SIZE}"
done

echo "✅ Wszystkie ikony zostały wygenerowane!"
