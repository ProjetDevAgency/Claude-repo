"""Montage final : coupe 61-63 s, miroir, étalonnage, sous-titres, bandeau titre, mix audio."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .common import ROOT, duration, run


def render_title(text, out_path, width, font_file, font_size):
    """Bandeau blanc arrondi, texte noir en majuscules (style du modèle)."""
    font = ImageFont.truetype(str(ROOT / font_file), font_size)
    max_w = int(width * 0.62)
    words, lines, cur = text.upper().split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if font.getlength(test) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    line_h = int(font_size * 1.12)
    tw = int(max(font.getlength(l) for l in lines))
    pad_x, pad_y = int(font_size * 0.55), int(font_size * 0.35)
    box_w, box_h = tw + 2 * pad_x, line_h * len(lines) + 2 * pad_y
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, box_w - 1, box_h - 1], radius=int(font_size * 0.4),
                        fill=(255, 255, 255, 255))
    for i, l in enumerate(lines):
        lw = font.getlength(l)
        d.text(((box_w - lw) / 2, pad_y + i * line_h), l, font=font, fill=(0, 0, 0, 255))
    img.save(out_path)
    return out_path


def build(video, voice, ass, out, cfg, final_dur, title_png=None, music=None):
    e = cfg["edit"]
    W, H, fps = e["width"], e["height"], e["fps"]
    src_dur = duration(video)
    start = e.get("skip_start", 0.0)
    avail = src_dur - start
    if avail < final_dur:
        # vidéo un poil trop courte : on la ralentit très légèrement plutôt que de figer
        stretch = final_dur / avail
        if stretch > 1.15:
            start, avail = 0.0, src_dur
            stretch = final_dur / avail
        print(f"   vidéo source ralentie x{1 / stretch:.3f} pour couvrir {final_dur:.1f}s")
    else:
        stretch = 1.0

    c = e["color"]
    z = e.get("zoom", 1.0)
    vf = [f"setpts={stretch:.5f}*(PTS-STARTPTS)" if stretch != 1 else "setpts=PTS-STARTPTS",
          f"scale={int(W * z)}:{int(H * z)}:force_original_aspect_ratio=increase:flags=lanczos",
          f"crop={W}:{H}"]
    if e.get("mirror", True):
        vf.append("hflip")
    vf.append(f"eq=contrast={c['contrast']}:saturation={c['saturation']}:"
              f"brightness={c['brightness']}:gamma={c['gamma']}")
    warm = c.get("warm", 0)
    if warm:
        vf.append(f"colorbalance=rm={warm:.3f}:gm={warm / 3:.3f}:bm={-warm:.3f}:"
                  f"rh={warm / 2:.3f}:bh={-warm / 2:.3f}")
    if c.get("vignette"):
        vf.append("vignette=PI/6")
    vf.append(f"fps={fps}")
    ass_path = str(ass).replace("\\", "/").replace(":", "\\:")
    fonts = str(ROOT / "assets" / "fonts").replace(":", "\\:")
    vf.append(f"ass='{ass_path}':fontsdir='{fonts}'")

    inputs = ["-ss", f"{start:.3f}", "-i", str(video), "-i", str(voice)]
    graph = f"[0:v]{','.join(vf)}[vs]"
    vlabel = "vs"
    idx = 2
    if title_png:
        inputs += ["-i", str(title_png)]
        y = int(H * cfg["title"]["position_y"])
        td = cfg["title"]["duration"]
        graph += (f";[{idx}:v]format=rgba,fade=t=out:st={td - 0.25:.2f}:d=0.25:alpha=1[tt]"
                  f";[vs][tt]overlay=x=(W-w)/2:y={y}:enable='lt(t,{td})'[vt]")
        vlabel = "vt"
        idx += 1

    # audio : voix + (ambiance d'origine) + (musique)
    mix = ["[1:a]aresample=48000,apad[va]"]
    labels = ["[va]"]
    if e.get("original_audio_volume", 0) > 0:
        mix.append(f"[0:a]atempo={1 / stretch:.5f},volume={e['original_audio_volume']},"
                   "aresample=48000[oa]")
        labels.append("[oa]")
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        mix.append(f"[{idx}:a]volume={e.get('music_volume', 0.06)},aresample=48000[ma]")
        labels.append("[ma]")
        idx += 1
    if len(labels) > 1:
        mix.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0[aout]")
    else:
        mix[-1] = mix[-1].replace("[va]", "[aout]")
    graph += ";" + ";".join(mix)

    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph,
           "-map", f"[{vlabel}]", "-map", "[aout]", "-t", f"{final_dur:.3f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
           str(out)]
    run(cmd)
    return Path(out)
