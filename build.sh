#!/bin/sh
# Assemble every demo in src/ with NASM and enforce its size budget (all are under 9 bytes).
set -eu
cd "$(dirname "$0")"
command -v nasm >/dev/null 2>&1 || { echo 'ERROR: NASM is required.' >&2; exit 1; }
fail=0
: > SHA256SUMS.tmp
for spec in overlap:8 oversub:8 stackmap:7 stkrain:8 bullets:7 snow:8 breath:7 buzz:6 static:6 ticker:6 geiger:7 typer:7 mirror:8 spectrum:8 stripe:8 big:4 tall:6 keyscan:6 pspback:7 state:7 flux:8 weave:8 codepal:8 psppal:7 noisepal:8 mode3:5 evo1:8 evo2:8; do
    name=${spec%%:*}; budget=${spec##*:}
    upper=$(echo "$name" | tr 'a-z' 'A-Z')
    [ "${#name}" -le 8 ] || { echo "ERROR: $upper.COM is not a valid 8.3 DOS file name" >&2; fail=1; }
    nasm -f bin -Wall -Werror "src/$name.asm" -o "$upper.COM"
    size=$(wc -c < "$upper.COM" | tr -d ' ')
    printf '%-14s %s bytes (budget %s)\n' "$upper.COM" "$size" "$budget"
    [ "$size" -le "$budget" ] || { echo "ERROR: $upper.COM grew past its $budget-byte budget" >&2; fail=1; }
    [ "$size" -le 8 ] || { echo "ERROR: $upper.COM is not under 9 bytes" >&2; fail=1; }
done
rm -f SHA256SUMS.tmp
[ "$fail" -eq 0 ] || exit 2
if command -v sha256sum >/dev/null 2>&1; then sha256sum *.COM > SHA256SUMS; else shasum -a 256 *.COM > SHA256SUMS; fi
