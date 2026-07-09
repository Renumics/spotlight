# FSD50K (tiny)

A tiny subset of **FSD50K: an open dataset of human-labeled sound events**
(20 samples), provided as sample data.

## Contents

- `<freesound-id>.wav`: individual audio clips, named after their original
  Freesound ID.
- `fsd50k-tiny.csv`: table referencing the clips with their `annotation`,
  `labels`, `split`, `title`, `description` and `uploader` (all taken from
  the original dataset), a `window` marking a time span within the clip, and
  a generated `prediction`, `embedding`, `entropy` and `prediction_incorrect`
  for each sample.

## Attribution

FSD50K by Eduardo Fonseca, Xavier Favory, Jordi Pons, Frederic Font and
Xavier Serra (Music Technology Group, Universitat Pompeu Fabra), built from
audio clips uploaded to [Freesound.org](https://freesound.org).

- **Source:** https://zenodo.org/records/4060432
- **Citation:** Fonseca, E., Favory, X., Pons, J., Font, F., & Serra, X.
  (2022). FSD50K: an open dataset of human-labeled sound events. IEEE/ACM
  Transactions on Audio, Speech, and Language Processing, 30, 829-852.

FSD50K is released as a collective work under
[Creative Commons Attribution 4.0 (CC BY 4.0)](http://creativecommons.org/licenses/by/4.0/).
Each underlying clip additionally keeps the individual Creative Commons
license its uploader chose on Freesound (CC0, CC BY, CC BY-NC or CC
Sampling+). The clips in this subset are individually attributed below:

| File | Title | Uploader | License |
| --- | --- | --- | --- |
| [111020.wav](https://freesound.org/s/111020/) | golden_breasted_starling.wav | soundbytez | [CC BY 3.0](http://creativecommons.org/licenses/by/3.0/) |
| [151359.wav](https://freesound.org/s/151359/) | KEY FOB.wav | shakaharu | [CC0 1.0](http://creativecommons.org/publicdomain/zero/1.0/) |
| [168258.wav](https://freesound.org/s/168258/) | Footsteps on Wood | gmarchisio | [CC0 1.0](http://creativecommons.org/publicdomain/zero/1.0/) |
| [176634.wav](https://freesound.org/s/176634/) | peugot 206 car interior horn claxon playing with engine | jorickhoofd | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |
| [176638.wav](https://freesound.org/s/176638/) | peugot 206 car exterior engine stationary horn claxon reverb | jorickhoofd | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |
| [176641.wav](https://freesound.org/s/176641/) | peugot 206 car interior accelerating and breaking suddenly suspension and tire squeek bumping objects inside vehicle | jorickhoofd | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |
| 179862.wav | car horn 1 - 26.3.11.wav | toiletrolltube | unknown — the original Freesound page has since been removed |
| [182474.wav](https://freesound.org/s/182474/) | car horn.wav | keweldog | [CC0 1.0](http://creativecommons.org/publicdomain/zero/1.0/) |
| [184623.wav](https://freesound.org/s/184623/) | Ambulance Siren | LanDub | [CC0 1.0](http://creativecommons.org/publicdomain/zero/1.0/) |
| [209045.wav](https://freesound.org/s/209045/) | Pajaroto En La Laguna Del Delta del Llobrejat | Insestanyricarda | [CC BY 3.0](http://creativecommons.org/licenses/by/3.0/) |
| [245704.wav](https://freesound.org/s/245704/) | Birdsong 01 (Carmarthen).aif | TicAshfield | [CC0 1.0](http://creativecommons.org/publicdomain/zero/1.0/) |
| [262278.wav](https://freesound.org/s/262278/) | Warning Siren / War Siren - Trondheim Norway.mp3 | Ubehag | [CC0 1.0](http://creativecommons.org/publicdomain/zero/1.0/) |
| [324331.wav](https://freesound.org/s/324331/) | ATV.mp3 | monkeyman535 | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |
| [339703.wav](https://freesound.org/s/339703/) | Audi V8 Acceleration Sound | FFKoenigsegg20012017 | [CC0 1.0](http://creativecommons.org/publicdomain/zero/1.0/) |
| [346933.wav](https://freesound.org/s/346933/) | Woods NL 01 160603_0902.wav | klankbeeld | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |
| [353265.wav](https://freesound.org/s/353265/) | Emergency Vehicles | TheSpiderWriter | [CC0 1.0](http://creativecommons.org/publicdomain/zero/1.0/) |
| [353448.wav](https://freesound.org/s/353448/) | brd27.mp3 | tec_studio | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |
| [421017.wav](https://freesound.org/s/421017/) | Ambulance in Oradea | GirlWithSoundRecorder | [CC0 1.0](http://creativecommons.org/publicdomain/zero/1.0/) |
| [59446.wav](https://freesound.org/s/59446/) | TC.Salta.08.RevvingUp.PatoDiPalma.wav | rfhache | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |
| [95955.wav](https://freesound.org/s/95955/) | FiaGT.08.PotreroFunes.RedHotBrakes.57.2.wav | rfhache | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |

None of the clips in this subset are licensed CC BY-NC or CC Sampling+.

## Changes

This is a **derivative work**: a small subset (20 clips) of the original
dataset was extracted, and a `window`, `prediction`, `embedding`, `entropy`
and `prediction_incorrect` were generated and added for each clip.

## License of this derivative

In accordance with the CC BY 4.0 license of the collective work, this
modified subset is distributed under
[CC BY 4.0](http://creativecommons.org/licenses/by/4.0/), with attribution to
each clip's original author as listed above.
