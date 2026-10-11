import cv2
import mediapipe as mp
import pygame
import numpy as np

# Initialize Pygame Audio Engine
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

SAMPLE_RATE = 44100

def generate_tone(frequency, duration, decay=True):
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, False)
    wave = np.sin(2 * np.pi * frequency * t)
    
    if decay:
        envelope = np.exp(-3 * t / duration)
        wave = wave * envelope
        
    audio = (wave * 32767).astype(np.int16)
    audio_stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(audio_stereo)

def generate_drum(sound_type):
    duration = 0.25
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, False)
    
    if sound_type == "kick":
        f = np.linspace(150, 40, total_samples)
        wave = np.sin(2 * np.pi * f * t)
        envelope = np.exp(-10 * t)
        wave = wave * envelope
    elif sound_type == "snare":
        noise = np.random.uniform(-1, 1, total_samples)
        tone = np.sin(2 * np.pi * 180 * t)
        wave = 0.6 * noise + 0.4 * tone
        envelope = np.exp(-12 * t)
        wave = wave * envelope
    elif sound_type == "hihat":
        noise = np.random.uniform(-1, 1, total_samples)
        envelope = np.exp(-30 * t)
        wave = noise * envelope
    elif sound_type == "tom":
        f = np.linspace(220, 90, total_samples)
        wave = np.sin(2 * np.pi * f * t)
        envelope = np.exp(-8 * t)
        wave = wave * envelope
    elif sound_type == "crash":
        noise = np.random.uniform(-1, 1, total_samples)
        envelope = np.exp(-4 * t)
        wave = noise * envelope
    else:
        wave = np.zeros(total_samples)

    audio = (wave * 32767).astype(np.int16)
    audio_stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(audio_stereo)

# Pre-generate all sound patches
SOUND_PATCHES = {
    "Drum": {
        "Thumb": ("Kick", generate_drum("kick")),
        "Index": ("Snare", generate_drum("snare")),
        "Middle": ("Hi-Hat", generate_drum("hihat")),
        "Ring": ("Tom", generate_drum("tom")),
        "Pinky": ("Crash", generate_drum("crash"))
    },
    "Piano": {
        "Thumb": ("C4", generate_tone(261.63, 0.6)),
        "Index": ("D4", generate_tone(293.66, 0.6)),
        "Middle": ("E4", generate_tone(329.63, 0.6)),
        "Ring": ("F4", generate_tone(349.23, 0.6)),
        "Pinky": ("G4", generate_tone(392.00, 0.6))
    },
    "Guitar": {
        "Thumb": ("E2", generate_tone(82.41, 0.8)),
        "Index": ("A2", generate_tone(110.00, 0.8)),
        "Middle": ("D3", generate_tone(146.83, 0.8)),
        "Ring": ("G3", generate_tone(196.00, 0.8)),
        "Pinky": ("B3", generate_tone(246.94, 0.8))
    },
    "Bells": {
        "Thumb": ("Bell 1", generate_tone(523.25, 1.0)),
        "Index": ("Bell 2", generate_tone(659.25, 1.0)),
        "Middle": ("Bell 3", generate_tone(783.99, 1.0)),
        "Ring": ("Bell 4", generate_tone(1046.50, 1.0)),
        "Pinky": ("Bell 5", generate_tone(1318.51, 1.0))
    }
}

# MediaPipe Hand Detector Setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Mapping finger tips and joint landmarks
FINGER_LANDMARKS = {
    "Thumb": (4, 3),
    "Index": (8, 6),
    "Middle": (12, 10),
    "Ring": (16, 14),
    "Pinky": (20, 18)
}

modes = ["Drum", "Piano", "Guitar", "Bells"]
active_mode = "Drum"
pressed_states = {f: False for f in FINGER_LANDMARKS}
last_played_note = ""

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape

    # Render top instrument selection buttons
    btn_w = width // len(modes)
    for i, mode_name in enumerate(modes):
        bx1 = i * btn_w
        bx2 = bx1 + btn_w
        btn_color = (40, 160, 40) if mode_name == active_mode else (50, 50, 50)
        cv2.rectangle(frame, (bx1 + 5, 10), (bx2 - 5, 65), btn_color, -1)
        cv2.rectangle(frame, (bx1 + 5, 10), (bx2 - 5, 65), (200, 200, 200), 2)
        cv2.putText(frame, mode_name, (bx1 + 25, 46), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

    # Process Hand Landmarks
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            # Check if Index Finger interacts with top UI buttons
            idx_x = int(lm[8].x * width)
            idx_y = int(lm[8].y * height)
            if idx_y < 65:
                selected_idx = idx_x // btn_w
                if 0 <= selected_idx < len(modes):
                    active_mode = modes[selected_idx]

            # Detect finger tap / fold to trigger sound
            for finger_name, (tip_id, joint_id) in FINGER_LANDMARKS.items():
                tip_y = lm[tip_id].y
                joint_y = lm[joint_id].y

                # Trigger condition: Finger folds downward
                is_folded = tip_y > joint_y

                if is_folded and not pressed_states[finger_name]:
                    note_name, sound_obj = SOUND_PATCHES[active_mode][finger_name]
                    sound_obj.play()
                    last_played_note = f"{active_mode} -> {note_name} ({finger_name})"
                    pressed_states[finger_name] = True
                elif not is_folded:
                    pressed_states[finger_name] = False

    # Bottom status overlay
    cv2.putText(frame, f"Active Sound: {last_played_note}", (20, height - 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(frame, "Hotkeys: 1-Drum | 2-Piano | 3-Guitar | 4-Bells | Q-Exit", (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)

    cv2.imshow("Air Music Band", frame)

    # Keyboard controls
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('1'):
        active_mode = "Drum"
    elif key == ord('2'):
        active_mode = "Piano"
    elif key == ord('3'):
        active_mode = "Guitar"
    elif key == ord('4'):
        active_mode = "Bells"

cap.release()
cv2.destroyAllWindows()
pygame.quit()
