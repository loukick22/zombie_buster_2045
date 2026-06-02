import pygame
import cv2
import mediapipe as mp
import random
import math

# --- 1. INITIALIZE ---
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Buster 2045 - B.Tech Project")
clock = pygame.time.Clock()

# MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

# --- 2. ASSET LOADER (Set to 5 Frames) ---
def load_animation(action, count):
    images = []
    for i in range(1, count + 1):
        # This looks for files like assets/walk1.png, assets/walk2.png... assets/walk5.png
        img = pygame.image.load(f"assets/{action}{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (120, 120)) 
        images.append(img)
    return images

# Load all 20 images (5 per action)
zombie_walk = load_animation("walk", 5)
zombie_idle = load_animation("idle", 5)
zombie_attack = load_animation("attack", 5)
zombie_die = load_animation("die", 5)

# --- 3. GAME VARIABLES ---
zombies = [] 
score = 0

def spawn_zombie():
    # Format: [x, y, state, frame_index, is_dead_flag]
    return [random.randint(100, 900), random.randint(100, 550), "walk", 0, False]

# --- 4. MAIN LOOP ---
while True:
    # Set a dark background color
    screen.fill((20, 20, 25)) 
    
    success, frame = cap.read()
    if not success: break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    current_gesture = "IDLE"
    hx, hy = -100, -100 # Default hand position off-screen

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            # Get palm center coordinates
            hx = int(hand_lms.landmark[0].x * WIDTH)
            hy = int(hand_lms.landmark[0].y * HEIGHT)
            
            # GESTURE: Index Finger Pointing Up (SHOOT)
            # We compare the Tip of index (8) to the Joint (6)
            if hand_lms.landmark[8].y < hand_lms.landmark[6].y:
                current_gesture = "SHOOT"
                for z in zombies:
                    # Euclidean Distance Formula from Harish S. Paper
                    dist = math.sqrt((hx - z[0])**2 + (hy - z[1])**2)
                    
                    if dist < 85 and not z[4]: # If within range and not already dead
                        z[2] = "die"    
                        z[3] = 0        # Reset animation to first frame of death
                        z[4] = True     # Prevent double scoring
                        score += 1

            # Draw a crosshair (Red circle) at hand position
            pygame.draw.circle(screen, (255, 0, 0), (hx, hy), 25, 2)
            pygame.draw.line(screen, (255, 0, 0), (hx-10, hy), (hx+10, hy), 2)
            pygame.draw.line(screen, (255, 0, 0), (hx, hy-10), (hx, hy+10), 2)

    # Automatically spawn zombies if there are fewer than 4 on screen
    if random.random() < 0.02 and len(zombies) < 4: 
        zombies.append(spawn_zombie())

    # --- 5. DRAW & ANIMATE ZOMBIES ---
    for z in zombies[:]:
        state = z[2]
        frame_idx = int(z[3])
        
        # Determine which list of images to use
        if state == "walk": anim_list = zombie_walk
        elif state == "die": anim_list = zombie_die
        elif state == "attack": anim_list = zombie_attack
        else: anim_list = zombie_idle

        # Draw the zombie image (centered on its coordinates)
        screen.blit(anim_list[frame_idx], (z[0]-60, z[1]-60))

        # Animation Timing
        if state == "die":
            z[3] += 0.2 # Speed of falling down
            if z[3] >= 4.9: # Remove after the 5th frame finishes
                zombies.remove(z)
        else:
            # Cycle through frames 0 to 4 (Total 5 images)
            z[3] = (z[3] + 0.2) % 5 

    # --- 6. USER INTERFACE ---
    font = pygame.font.SysFont("Consolas", 30)
    score_txt = font.render(f"ZOMBIES BUSTED: {score}", True, (0, 255, 0))
    gst_txt = font.render(f"GESTURE: {current_gesture}", True, (255, 255, 0))
    screen.blit(score_txt, (20, 20))
    screen.blit(gst_txt, (20, 60))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); exit()

    pygame.display.flip()
    clock.tick(30) 