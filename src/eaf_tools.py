from pathlib import Path
import pympi

def relink_media(eaf_path: Path, media_dir: Path, out_path: Path=None):
    eaf = pympi.Elan.Eaf(str(eaf_path))
    media_dir = media_dir.resolve()
    # récupère les media déclarés
    linked = eaf.media_descriptors if hasattr(eaf, "media_descriptors") else eaf.get_linked_files()
    # stratégie: pour chaque media déclaré, on tente de retrouver un fichier "proche" par nom
    new_descriptors = []
    for md in linked:
        # md peut être tuple (path, mime, relativeMediaUrl, timeOrigin)
        old = md[0] if isinstance(md, (list, tuple)) else md
        base = Path(old).name
        candidates = list(media_dir.rglob(base))
        if not candidates:
            # parfois noms approximatifs: essayer sans _v1/_cut etc
            stem = Path(base).stem
            lo = stem.lower().replace("_v1","").replace("_cut","").replace("_part2","")
            cand = [p for p in media_dir.rglob("*") if p.suffix.lower() in (".wav",".mp4",".m4a",".mp3") and lo in p.stem.lower()]
            candidates = cand
        if candidates:
            new_path = candidates[0].as_uri()
            # pympi ≥ 1.70: set_media_descriptors; sinon: set_linked_files
            try:
                eaf.add_linked_file(candidates[0].as_posix(), mimetype=None, relative_media_url=None, time_origin=None)
            except Exception:
                pass
            new_descriptors.append(new_path)
        else:
            new_descriptors.append(old)  # on laisse tel quel si introuvable

    # Sauvegarde
    out = out_path or eaf_path
    eaf.to_file(str(out))
    return out