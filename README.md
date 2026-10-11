# 🎵 Air Music Band (Virtual AI Instrument)

A real-time, touchless musical instrument system that lets you play drums, piano, guitar, and bells in mid-air using hand gestures and your webcam.

Powered by **Python**, **OpenCV**, **MediaPipe**, and procedural sound synthesis via **NumPy** & **Pygame** — **no external audio files required!**

---

## ✨ Features

- **Real-Time Hand Tracking:** High-precision 21-landmark tracking using MediaPipe.
- **4 Instrument Modes:**
  - 🥁 **Drum:** Kick, Snare, Hi-Hat, Tom, Crash
  - 🎹 **Piano:** C4, D4, E4, F4, G4
  - 🎸 **Guitar:** E2, A2, D3, G3, B3
  - 🔔 **Bells:** Multi-octave chime tones
- **Procedural Sound Synthesis:** Audio waves are mathematically generated on the fly with NumPy, eliminating missing file errors.
- **Dual Mode Switching:** Switch instruments using your index finger on virtual UI buttons or hotkeys (`1`–`4`).
- **Low Latency:** Optimized Pygame buffer settings for zero lag playback.

---

## 🛠️ Tech Stack & Requirements

- Python 3.9 – 3.11
- OpenCV (`cv2`)
- Google MediaPipe
- Pygame
- NumPy

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/air-music-band.git](https://github.com/your-username/air-music-band.git)
cd air-music-band
