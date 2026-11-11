"""Jour 2, vidéo courte : élection de l'adjoint du maire, Maël contre Michael (15-20 s)."""
from cartoon import INK, RED, WHITE, YEL, CartoonVideo, big_number, dim, flash, push, shake, tag
from village import ROUGE, bouton_abonner, gros_plan_maire, titre2
import facades
import iso
import village_ep2 as v2

T = {}


def s_ouverture(lt, dur):
    img, _ = v2.vue(push(lt, dur, 1.0, 1.1), (540, 960))
    titre2(img, "JOUR 2 · FAUCHÉ-LES-OIES", "C'EST L'ÉLECTION", k=1.0, y=190)
    tag(img, 540, 1250, "POSTE D'ADJOINT DU MAIRE", 60, ROUGE, WHITE, rot=-3, k=(lt - 0.6) / 0.25)
    return shake(img, lt)


def s_duo(lt, dur):
    img = v2.duo(lt + 0.9, dur, "Maël", "Michael", "JOUR 2 · ÉLECTION", "2 CANDIDATS")
    big_number(img, (540, 1250), "VS", 150, RED, k=(lt - 0.3) / 0.25)
    return shake(flash(img, lt), lt - 0.3, dur=0.25, amp=12)


def s_mael(lt, dur):
    img = v2.fiche(lt + 0.9, dur, "Maël", nom="@MAËL", role="CANDIDAT N°1")
    tag(img, 540, 540, "LA FÊTE POUR REMPLIR LA CAISSE", 44, YEL, INK, rot=3, k=(lt - 0.8) / 0.25)
    if lt > 2.2:
        tag(img, 540, 640, "PUIS RÉPARER LE PONT", 44, WHITE, INK, rot=-2, k=(lt - 2.2) / 0.25)
    return img


def s_michael(lt, dur):
    img = v2.fiche(lt + 0.9, dur, "Michael", nom="@MICHAEL", role="CANDIDAT N°2")
    tag(img, 540, 540, "COMPTE SUR VOS VOIX", 50, YEL, INK, rot=3, k=(lt - 0.6) / 0.25)
    return img


def s_vote(lt, dur):
    img = v2.duo(9.0, dur, "Maël", "Michael", "UN SEUL SERA", "ADJOINT")
    tv = T["vote"] - T["s_vote"]
    if lt > tv:
        tag(img, 285, 470, "1 · MAËL", 64, YEL, INK, rot=-4, k=(lt - tv) / 0.25)
        tag(img, 800, 470, "2 · MICHAEL", 64, YEL, INK, rot=4, k=(lt - tv - 0.4) / 0.25)
    tr = T["resultat"] - T["s_vote"]
    if lt > tr:
        tag(img, 540, 620, "RÉSULTAT DEMAIN", 58, ROUGE, WHITE, rot=-3, k=(lt - tr) / 0.25)
    return shake(img, lt - tv, dur=0.3, amp=10)


def main():
    v = CartoonVideo("village_election", "scripts/village/election_adjoint.txt", "", "", corner="")
    v.length = (17.0, 18.0, 20.0)
    v.hook_head_start = 0.0
    v.voice("output/_work_village_election/voice_raw.mp3")
    sc = [("Jour deux", s_ouverture), ("Deux candidats", s_duo), ("Maël, qui veut", s_mael),
          ("Et Michael", s_michael), ("Un seul sera", s_vote)]
    for phrase, fn in sc:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    T["vote"], T["resultat"] = v.at("Vote un pour"), v.at("Résultat demain")
    v.sfx(0.0, "impact", 1.0)
    v.sfx(T["s_duo"], "whoosh", 0.5)
    v.sfx(T["s_duo"] + 0.3, "impact", 0.8)
    for k in ("s_mael", "s_michael"):
        v.sfx(T[k], "whoosh", 0.45)
        v.sfx(T[k] + 0.05, "pop", 0.7)
    v.sfx(T["vote"], "pop", 0.8)
    v.sfx(T["vote"] + 0.4, "pop", 0.8)
    v.sfx(T["resultat"], "impact", 0.8)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
