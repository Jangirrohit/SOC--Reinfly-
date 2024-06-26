# Import necessary libraries
import pygame
import sys
import random

# Define global constants
WIDTH, HEIGHT = 576, 800
BIRD_JUMP = 5
PIPE_GAP = 200
PIPE_VELOCITY = 3
BIRD_WIDTH, BIRD_HEIGHT = 64, 48
PIPE_WIDTH, PIPE_HEIGHT = 100, 800
BACKGROUND_COLOR = (0, 102, 204)
game_active = False 
score = 0
time = 0
final_score = 0

# Initialize Pygame and Set Up the Display
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Load digit images
digit_images = {i: pygame.image.load(f'sprites/{i}.png') for i in range(10)}

# Load sounds
flap_sound = pygame.mixer.Sound('audio/wing.wav')
hit_sound = pygame.mixer.Sound('audio/hit.wav')
die_sound = pygame.mixer.Sound('audio/die.wav')
point_sound = pygame.mixer.Sound('audio/point.wav')
start_sound = pygame.mixer.Sound('audio/game-start-6104.mp3')

# Load background music
pygame.mixer.music.load('audio/Fluffing-a-Duck(chosic.com).mp3')
pygame.mixer.music.set_volume(0.5)  # Adjust volume if needed
pygame.mixer.music.play(-1)  # Play music in an infinite loop

# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        downflap_bird = pygame.image.load('sprites/redbird-downflap.png').convert_alpha()
        downflap_bird = pygame.transform.scale(downflap_bird, (BIRD_WIDTH, BIRD_HEIGHT))
        midflap_bird = pygame.image.load('sprites/redbird-midflap.png').convert_alpha()
        midflap_bird = pygame.transform.scale(midflap_bird, (BIRD_WIDTH, BIRD_HEIGHT))
        upflap_bird = pygame.image.load('sprites/redbird-upflap.png').convert_alpha()
        upflap_bird = pygame.transform.scale(upflap_bird, (BIRD_WIDTH, BIRD_HEIGHT))
        self.frame = [upflap_bird, downflap_bird]
        self.gravity = 0
        self.GRAVITY = 0
        self.animation_index = 0
        self.image = self.frame[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(WIDTH / 4, HEIGHT / 2))

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.GRAVITY = 0.25
            self.gravity = -BIRD_JUMP
            flap_sound.play()

    def jump(self):
        self.gravity += self.GRAVITY
        self.rect.y += self.gravity

    def animation(self):
        self.animation_index += 0.5
        if self.animation_index >= len(self.frame):
            self.animation_index = 0
        self.image = self.frame[int(self.animation_index)]

    def update(self):
        self.player_input()
        self.jump()
        self.animation()

    def reset(self):
        self.rect.y = HEIGHT / 2  # Reset bird position
        self.gravity = 0  # Reset bird's gravity velocity
        self.GRAVITY = 0

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, inverted):
        super().__init__()
        self.x = x
        if inverted:
            self.y = y
            image = pygame.image.load('sprites/pipe-green.png').convert_alpha()
            image = pygame.transform.scale(image, (PIPE_WIDTH, PIPE_HEIGHT))
            self.image = pygame.transform.rotate(image, 180)
            self.rect = self.image.get_rect(midbottom=(x, y))
        else:
            self.y = y
            image = pygame.image.load('sprites/pipe-green.png').convert_alpha()
            self.image = pygame.transform.scale(image, (PIPE_WIDTH, PIPE_HEIGHT))
            self.rect = self.image.get_rect(midtop=(x, y))

    def move(self):
        self.rect.x -= PIPE_VELOCITY

    def destroy(self):
        if self.rect.x < -50:
            self.kill()

    def update(self):
        self.move()
        self.destroy()

# Function to create pipes
def create_pipe():
    x = WIDTH
    y_bot = random.randint(100 + PIPE_GAP, int(0.8 * HEIGHT) - 100)
    y_top = y_bot - PIPE_GAP
    bot_pipe = Pipe(x, y_bot, False)
    top_pipe = Pipe(x, y_top, True)
    return [top_pipe, bot_pipe]

# Score counting function
def Score(bird, pipe_group):
    global time, score
    time = pygame.time.get_ticks()
    bird_mid = bird.sprite.rect.x + BIRD_WIDTH / 2
    for pipe in pipe_group:
        pipe_end = PIPE_WIDTH / 2 + pipe.rect.x
        if pipe_end < bird_mid <= pipe_end + 4 and pipe.rect.bottom > HEIGHT:
            score += 1
            point_sound.play()
    return score

# Function to display score
def Display_score(score, y):
    score = str(score)
    total_width = sum([digit_images[int(digit)].get_width() for digit in score])
    x_offset = (WIDTH - total_width) / 2

    for digit in score:
        screen.blit(digit_images[int(digit)], (x_offset, y))
        x_offset += digit_images[int(digit)].get_width()

# Collision detection function
def check_collision(bird, pipe_group, y):
    global score
    if pygame.sprite.spritecollide(bird.sprite, pipe_group, False):
        bird.sprite.reset()  # Reset bird's position and gravity
        pipe_group.empty()  # Clear pipes on collision
        die_sound.play()
        return False
    elif y >= int(0.8 * HEIGHT) or y <= 0:
        bird.sprite.reset()  # Reset bird's position and gravity
        pipe_group.empty()  # Clear pipes on collision
        die_sound.play()
        return False
    else:
        return True

# Function to create a gradient surface
def create_gradient_surface(width, height, start_color, end_color):
    gradient_surface = pygame.Surface((width, height))
    for y in range(height):
        color = [
            start_color[i] + (end_color[i] - start_color[i]) * y // height
            for i in range(3)
        ]
        pygame.draw.line(gradient_surface, color, (0, y), (width, y))
    gradient_surface.set_alpha(128)  # Set transparency level (0-255)
    return gradient_surface

# Main Game Loop.

# Load background images
sky_back = pygame.image.load("sprites/background-day.png").convert()
sky_back = pygame.transform.scale(sky_back, (WIDTH, HEIGHT))
ground_back = pygame.image.load("sprites/base.png").convert()
ground_back = pygame.transform.scale(ground_back, (WIDTH, 0.8 * HEIGHT))

# Load fonts and text
test_font = pygame.font.Font("font/Pixeltype.ttf", 50)
game_over_text = test_font.render('Game Over', True, (255, 255, 255))

# Gradient surface for game-over screen
gradient_surface = create_gradient_surface(WIDTH, HEIGHT, (0, 255, 128), (0, 128, 255))

def main():
    global game_active, score

    # Create bird/pipe instances and score counter
    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())

    pipe_group = pygame.sprite.Group()

    # Timer for pipe spawn
    pipe_spawn_timer = pygame.USEREVENT
    pygame.time.set_timer(pipe_spawn_timer, 1200)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Set an event checker to allow user to jump
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_sound.play()
                score = 0
            if game_active and event.type == pipe_spawn_timer:
                pipes = create_pipe()
                pipe_group.add(pipes)

        if game_active:
            screen.blit(sky_back, (0, 0))
            screen.blit(ground_back, (0, 0.8 * HEIGHT))

            bird.draw(screen)
            bird.update()
            pipe_group.draw(screen)
            pipe_group.update()

            game_active = check_collision(bird, pipe_group, bird.sprite.rect.y)
            score = Score(bird, pipe_group)

            Display_score(score, 100)
        else:
            screen.blit(gradient_surface, (0, 0))  # Apply the gradient overlay
            if time == 0:
                home = pygame.image.load('sprites/home (2).jpeg').convert_alpha()
                home = pygame.transform.scale(home, (WIDTH, HEIGHT))
                home.set_alpha(128)
                screen.blit(home, (0, 0))

                # Add instructions text with heading
                heading = test_font.render('Instructions to Play', False, (255, 255, 255))
                heading_rect = heading.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(heading, heading_rect)

                instructions1 = test_font.render('Press UP Arrow to Make Bird Fly', False, (255, 255, 255))
                instructions1_rect = instructions1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
                screen.blit(instructions1, instructions1_rect)

                instructions2 = test_font.render('Press SPACE to Start Game', False, (255, 255, 255))
                instructions2_rect = instructions2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
                screen.blit(instructions2, instructions2_rect)
            else:
                sky_back.set_alpha(128)
                screen.blit(sky_back, (0, 0))
                Display_score(score, HEIGHT / 2 - 20)

                score_msg = test_font.render(f'Your Score:', False, (255, 255, 255))
                score_msg_rect = score_msg.get_rect(center=(WIDTH // 2, HEIGHT / 2 - 50))
                screen.blit(score_msg, score_msg_rect)

                screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT / 6))

                bird_over = pygame.image.load('sprites/redbird-midflap.png').convert_alpha()
                bird_over = pygame.transform.rotozoom(bird_over, 0, 3.0)
                bird_over_rect = bird_over.get_rect(center=(WIDTH // 2, HEIGHT / 6 + 100))
                screen.blit(bird_over, bird_over_rect)

                restart_msg1 = test_font.render('Press Space To', False, (255, 255, 255))
                restart_msg1_rect = restart_msg1.get_rect(center=(WIDTH // 2, HEIGHT / 1.2 - 130))
                screen.blit(restart_msg1, restart_msg1_rect)

                restart_msg2 = test_font.render('Restart The Game', False, (255, 255, 255))
                restart_msg2_rect = restart_msg2.get_rect(center=(WIDTH // 2, HEIGHT / 1.2 - 70))
                screen.blit(restart_msg2, restart_msg2_rect)

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
