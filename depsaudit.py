"""depsaudit: Alat CLI untuk mengaudit requirements.txt.

Memeriksa pin longgar, duplikat, versi tidak valid, dan paket tanpa pin.
Mendukung keluaran JSON dan teks.

Penggunaan:
    python depsaudit.py requirements.txt
    python depsaudit.py requirements.txt --json

Exit code:
    0: tidak ada masalah ditemukan
    1: ada masalah ditemukan
    2: berkas tidak ditemukan atau tidak dapat dibaca, atau kesalahan argumen
"""

import argparse
import json
import re
import sys
from pathlib import Path


SUMBOY = "depsaudit"

# Pola nama paket sesuai PEP 508 (disederhanakan)
RE_PAKET = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$")

# Operator versi yang valid
OPERATOR_VALID = {"==", "!=", "<=", ">=", "<", ">", "~=", "==="}

# Pola specifier versi (satu atau lebih, dipisah koma)
RE_SPEC = re.compile(r"^([<>=!~]=?)\s*([^,\s]+)(?:\s*,\s*([<>=!~]=?)\s*([^,\s]+))*$")


def baca_baris(path: Path) -> list[str]:
    """Baca berkas requirements.txt dan kembalikan daftar baris (tanpa newline)."""
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        print(f"Kesalahan: Berkas '{path}' tidak ditemukan.", file=sys.stderr)
        sys.exit(2)
    except PermissionError:
        print(f"Kesalahan: Tidak dapat membaca berkas '{path}' (izin ditolak).", file=sys.stderr)
        sys.exit(2)
    except OSError as exc:
        print(f"Kesalahan: Gagal membaca berkas '{path}': {exc}", file=sys.stderr)
        sys.exit(2)


def bersihkan_baris(baris: str) -> str | None:
    """Bersihkan komentar dan spasi, kembalikan None jika baris kosong."""
    # Hapus komentar (hanya jika '#' di awal atau didahului spasi)
    hasil = ""
    for i, ch in enumerate(baris):
        if ch == "#" and (i == 0 or baris[i - 1].isspace()):
            break
        hasil += ch
    hasil = hasil.strip()
    return hasil if hasil else None


def parse_requirement(baris: str) -> dict:
    """Parse satu baris requirement menjadi komponen."""
    # Pisahkan specifier dari nama (operators)
    m = re.match(r"^([A-Za-z0-9._-]+)\s*(.*)$", baris)
    if not m:
        return {
            "nama": baris,
            "valid": False,
            "masalah": ["format tidak valid"],
            "pin_ketat": False,
            "operator": None,
            "versi": None,
        }

    nama = m.group(1)
    sisa = m.group(2).strip()

    masalah = []
    if not RE_PAKET.match(nama):
        masalah.append("nama paket tidak valid")

    pin_ketat = False
    operator = None
    versi = None

    if not sisa:
        masalah.append("tanpa pin versi")
    else:
        # Cek apakah ada ekstra atau marker (tidak didukung penuh, anggap valid jika ada)
        if sisa.startswith("["):
            masalah.append("ekstra tidak didukung")
            sisa = ""
        elif ";" in sisa:
            # ada environment marker, ambil bagian specifier saja
            sisa = sisa.split(";", 1)[0].strip()

        if sisa:
            # Validasi specifier: pisah per koma
            parts = [p.strip() for p in sisa.split(",")]
            for part in parts:
                op_match = re.match(r"^(==|!=|<=|>=|<|>|~=|===)\s*(.+)$", part)
                if not op_match:
                    masalah.append(f"specifier tidak valid: '{part}'")
                    continue
                op = op_match.group(1)
                ver = op_match.group(2).strip()
                if op not in OPERATOR_VALID:
                    masalah.append(f"operator tidak dikenal: '{op}'")
                if not ver:
                    masalah.append(f"versi kosong untuk operator '{op}'")
                if op == "==" and len(parts) == 1:
                    pin_ketat = True
                    operator = op
                    versi = ver
                elif operator is None:
                    operator = op
                    versi = ver

    return {
        "nama": nama,
        "valid": len(masalah) == 0,
        "masalah": masalah,
        "pin_ketat": pin_ketat,
        "operator": operator,
        "versi": versi,
    }


def audit(baris_list: list[str]) -> list[dict]:
    """Audit daftar baris requirements, kembalikan daftar temuan."""
    temuan = []
    seen: dict[str, list[tuple[int, dict]]] = {}

    for idx, baris in enumerate(baris_list, start=1):
        bersih = bersihkan_baris(baris)
        if bersih is None:
            continue

        parsed = parse_requirement(bersih)
        nama_lower = parsed["nama"].lower()
        seen.setdefault(nama_lower, []).append((idx, parsed))

        if parsed["masalah"]:
            temuan.append({
                "baris": idx,
                "paket": parsed["nama"],
                "tipe": "tidak_valid",
                "pesan": "; ".join(parsed["masalah"]),
            })
        elif not parsed["pin_ketat"]:
            temuan.append({
                "baris": idx,
                "paket": parsed["nama"],
                "tipe": "pin_longgar",
                "pesan": f"pin longgar (operator: {parsed['operator'] or 'tidak ada'})",
            })

    # Deteksi duplikat
    for nama, daftar in seen.items():
        if len(daftar) > 1:
            baris_angka = [d[0] for d in daftar]
            temuan.append({
                "baris": baris_angka[0],
                "paket": nama,
                "tipe": "duplikat",
                "pesan": f"paket duplikat pada baris {baris_angka}",
            })

    temuan.sort(key=lambda x: (x["baris"], x["tipe"]))
    return temuan


def main() -> int:
    """Titik masuk utama CLI."""
    parser = argparse.ArgumentParser(
        prog="depsaudit",
        description="Audit requirements.txt: temukan pin longgar, duplikat, versi tidak valid, dan paket tanpa pin.",
        epilog="Contoh: python depsaudit.py requirements.txt --json",
    )
    parser.add_argument(
        "berkas",
        type=Path,
        help="Path ke berkas requirements.txt yang akan diaudit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Keluarkan hasil dalam format JSON",
    )
    args = parser.parse_args()

    baris_list = baca_baris(args.berkas)
    temuan = audit(baris_list)

    if args.json_output:
        hasil = {
            "berkas": str(args.berkas),
            "jumlah_masalah": len(temuan),
            "temuan": temuan,
        }
        print(json.dumps(hasil, ensure_ascii=False, indent=2))
    else:
        if not temuan:
            print(f"Tidak ada masalah ditemukan pada '{args.berkas}'.")
        else:
            print(f"Ditemukan {len(temuan)} masalah pada '{args.berkas}':")
            for t in temuan:
                print(f"  Baris {t['baris']}: [{t['tipe']}] {t['paket']} - {t['pesan']}")

    return 0 if not temuan else 1


if __name__ == "__main__":
    sys.exit(main())
