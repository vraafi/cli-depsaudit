#!/usr/bin/env python3
"""Alat CLI depsaudit untuk mengaudit berkas requirements.txt.

Fungsi utama:
- Mendeteksi pin longgar (misalnya '>=1.0', '~=2.0', '*', tanpa batas atas).
- Mendeteksi paket duplikat (nama sama, abaikan case dan ekstra).
- Mendeteksi versi tidak valid (format versi tidak sesuai PEP 440 secara sederhana).
- Mendeteksi paket tanpa pin (tanpa operator versi).

Keluaran dapat berupa teks ringkas berbahasa Indonesia atau JSON dengan opsi --json.
Hanya menggunakan pustaka standar Python 3.11.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


VERSION_PATTERN = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)(?:\[(?P<extras>[^\]]+)\])?\s*"
    r"(?:(?P<op>===|==|~=|!=|<=|>=|<|>)\s*(?P<version>[^\s,;]+))?\s*$"
)

VALID_VERSION_RE = re.compile(
    r"^(?:\d+!)?\d+(?:\.\d+)*(?:(?:a|b|rc)\d+)?(?:\.post\d+)?(?:\.dev\d+)?(?:\+[a-zA-Z0-9.]+)?$",
    re.IGNORECASE,
)

LOOSE_OPS = {">=", "~=", ">", "!=", "<="}


def baca_baris(path: Path) -> List[str]:
    """Membaca berkas requirements.txt dan mengembalikan daftar baris non-kosong."""
    try:
        with path.open("r", encoding="utf-8") as f:
            return [line.rstrip("\n") for line in f]
    except FileNotFoundError:
        print(f"Galat: berkas '{path}' tidak ditemukan.", file=sys.stderr)
        raise SystemExit(2)
    except PermissionError:
        print(f"Galat: tidak memiliki izin membaca berkas '{path}'.", file=sys.stderr)
        raise SystemExit(2)
    except OSError as exc:
        print(f"Galat: gagal membaca berkas '{path}': {exc}", file=sys.stderr)
        raise SystemExit(2)


def bersihkan_baris(line: str) -> Optional[str]:
    """Mengembalikan baris yang sudah dibersihkan atau None jika komentar/kosong."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    tanpa_komentar = stripped.split("#", 1)[0].strip()
    return tanpa_komentar or None


def parse_requirement(line: str, nomor: int) -> Tuple[str, str, List[str]]:
    """Mengurai baris requirement menjadi (nama, versi, masalah)."""
    masalah: List[str] = []
    m = VERSION_PATTERN.match(line)
    if not m:
        masalah.append("format baris tidak dikenali")
        token = line.split()[0] if line.split() else line
        return token.lower(), "", masalah

    name = m.group("name")
    op = m.group("op")
    version = m.group("version") or ""

    if op is None:
        masalah.append("paket tanpa pin versi")
    else:
        if op in LOOSE_OPS:
            masalah.append(f"pin longgar ('{op}')")
        if version and not VALID_VERSION_RE.match(version):
            masalah.append(f"versi tidak valid ('{version}')")
        if op == "==" and version.endswith(".*"):
            masalah.append("pin wildcard (==x.*)")
        if version == "*":
            masalah.append("versi wildcard ('*')")

    return name.lower(), version, masalah


def audit(baris: List[str]) -> Dict[str, List[dict]]:
    """Menjalankan audit dan mengembalikan hasil terstruktur."""
    hasil: Dict[str, List[dict]] = {
        "pin_longgar": [],
        "duplikat": [],
        "versi_tidak_valid": [],
        "tanpa_pin": [],
        "format_tidak_dikenal": [],
    }
    terlihat: Dict[str, int] = {}

    for idx, line in enumerate(baris, start=1):
        cleaned = bersihkan_baris(line)
        if cleaned is None:
            continue

        name, version, masalah = parse_requirement(cleaned, idx)

        if "format baris tidak dikenali" in masalah:
            hasil["format_tidak_dikenal"].append(
                {"baris": idx, "konten": cleaned}
            )
            continue

        if name in terlihat:
            hasil["duplikat"].append(
                {
                    "baris": idx,
                    "nama": name,
                    "kemunculan_pertama": terlihat[name],
                }
            )
        else:
            terlihat[name] = idx

        if "pin longgar" in " ".join(masalah):
            hasil["pin_longgar"].append(
                {"baris": idx, "nama": name, "versi": version or "-"}
            )
        if "versi tidak valid" in " ".join(masalah):
            hasil["versi_tidak_valid"].append(
                {"baris": idx, "nama": name, "versi": version}
            )
        if "paket tanpa pin versi" in " ".join(masalah):
            hasil["tanpa_pin"].append({"baris": idx, "nama": name})

    return hasil


def cetak_teks(hasil: Dict[str, List[dict]]) -> None:
    """Mencetak hasil audit dalam format teks ringkas berbahasa Indonesia."""
    total = sum(len(v) for v in hasil.values())
    print(f"Audit selesai. Total temuan: {total}")
    for kunci, label in (
        ("pin_longgar", "Pin longgar"),
        ("duplikat", "Duplikat"),
        ("versi_tidak_valid", "Versi tidak valid"),
        ("tanpa_pin", "Tanpa pin"),
        ("format_tidak_dikenal", "Format tidak dikenal"),
    ):
        items = hasil[kunci]
        if not items:
            continue
        print(f"\n{label} ({len(items)}):")
        for item in items:
            if kunci == "duplikat":
                print(
                    f"  - baris {item['baris']}: '{item['nama']}' "
                    f"(pertama di baris {item['kemunculan_pertama']})"
                )
            elif kunci == "format_tidak_dikenal":
                print(f"  - baris {item['baris']}: {item['konten']}")
            elif kunci == "tanpa_pin":
                print(f"  - baris {item['baris']}: '{item['nama']}'")
            else:
                print(
                    f"  - baris {item['baris']}: '{item['nama']}' "
                    f"versi {item.get('versi', '-')}"
                )


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="depsaudit",
        description=(
            "Audit requirements.txt: temukan pin longgar, duplikat, "
            "versi tidak valid, dan paket tanpa pin."
        ),
        epilog="Contoh: depsaudit requirements.txt --json",
    )
    parser.add_argument(
        "berkas",
        type=Path,
        nargs="?",
        default=Path("requirements.txt"),
        help="Path ke requirements.txt (default: requirements.txt)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Keluarkan hasil dalam format JSON",
    )

    args = parser.parse_args()
    baris = baca_baris(args.berkas)
    hasil = audit(baris)

    if args.json:
        print(json.dumps(hasil, indent=2, ensure_ascii=False))
    else:
        cetak_teks(hasil)

    return 0


if __name__ == "__main__":
    sys.exit(main())
