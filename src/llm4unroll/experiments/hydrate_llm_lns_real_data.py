from __future__ import annotations

import argparse
import shutil
import tarfile
import zipfile
from pathlib import Path

import gdown

from llm4unroll.utils import ensure_dir


MILPBENCH_DRIVE_IDS = {
    "IS": {
        "easy": "1slfuVvma5R5qwoFtIw1I3wLeIzg5EGvM",
        "medium": "1DOSR3rZ3ezwaMJAB-5aHtwKWoOngUQzH",
        "hard": "15ZkWUq5dysm-3D9VAL2kb1nr-Sgwjain",
    },
    "MVC": {
        "easy": "10CCgHflKtxO4XOXZZCkD-pLU7vh81GZ0",
        "medium": "11Frntl0fDKf0bnbgvrZun_vHJxbTKxbu",
        "hard": "1y80fAwcty8e3yR93dR5whD6xx39_QLXE",
    },
    "SC": {
        "easy": "1Oa9NiP6I1XpOkneLETGfKgTeYMDybVJX",
        "medium": "1OOEiav-07UmCtCKOfnpWraN5Rxz980bk",
        "hard": "1uJFOUz6Xr_qgrmXhZcisWUG0hw_fnCSV",
    },
    "MIKS": {
        "easy": "1YYIAWqxzHAtfQQmKqdWy_UOhx8f3V8ZU",
        "medium": "1TCZCsJcLDzNurjvpvSzuBmrNxn_wIUJt",
        "hard": "18hcNsm4jmZvFGm7NjNGSNR73gfbq5_mh",
    },
}

CANONICAL_TARGETS = {
    "IS": "data/llm_lns/IS_easy_instance/LP",
    "MVC": "data/llm_lns/MVC_easy_instance/LP",
    "SC": "data/llm_lns/SC_easy_instance/LP",
    "MIKS": "data/llm_lns/MIKS_easy_instance/LP",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Download and hydrate real MILPBench LLM-LNS LP assets.")
    parser.add_argument("--families", nargs="*", default=["IS", "MVC", "SC", "MIKS"])
    parser.add_argument("--levels", nargs="*", default=["easy"], choices=["easy", "medium", "hard"])
    parser.add_argument("--cache-dir", default="external/MILPBench/download_cache")
    parser.add_argument("--extract-dir", default="external/MILPBench/extracted")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def _archive_path(cache_dir: Path, family: str, level: str) -> Path:
    return cache_dir / ("%s_%s.zip" % (family.lower(), level))


def _extract_archive(archive_path: Path, extract_root: Path) -> Path:
    target_dir = extract_root / archive_path.stem
    ensure_dir(str(target_dir))
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(target_dir)
            return target_dir
    except zipfile.BadZipFile:
        pass
    try:
        with tarfile.open(archive_path, "r:*") as tf:
            tf.extractall(target_dir)
            return target_dir
    except tarfile.TarError:
        pass
    raise RuntimeError("Unsupported archive format for %s" % archive_path)


def _hydrate_lp_files(source_dir: Path, family: str, level: str, force: bool) -> int:
    target_dir = Path(CANONICAL_TARGETS[family])
    ensure_dir(str(target_dir))
    copied = 0
    for lp_path in sorted(source_dir.rglob("*.lp")):
        name = "%s_%s_%s" % (family.lower(), level, lp_path.name)
        dst = target_dir / name
        if dst.exists() and not force:
            continue
        shutil.copy2(lp_path, dst)
        copied += 1
    return copied


def main() -> None:
    args = parse_args()
    cache_dir = Path(args.cache_dir)
    extract_dir = Path(args.extract_dir)
    ensure_dir(str(cache_dir))
    ensure_dir(str(extract_dir))

    total_copied = 0
    for family in args.families:
        family = family.upper()
        if family not in MILPBENCH_DRIVE_IDS:
            raise KeyError("Unknown family %s" % family)
        for level in args.levels:
            archive_path = _archive_path(cache_dir, family, level)
            if args.force or not archive_path.exists():
                url = "https://drive.google.com/uc?id=%s" % MILPBENCH_DRIVE_IDS[family][level]
                gdown.download(url, str(archive_path), quiet=False, fuzzy=True)
            extracted = _extract_archive(archive_path, extract_dir)
            copied = _hydrate_lp_files(extracted, family, level, force=args.force)
            total_copied += copied
            print("hydrated family=%s level=%s copied=%d from=%s" % (family, level, copied, extracted))
    print("Hydrated %d LP files into data/llm_lns" % total_copied)


if __name__ == "__main__":
    main()
