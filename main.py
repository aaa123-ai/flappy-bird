import pygame
import random
import cv2
import mediapipe as mp

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 204, 0)

try:
    # 修正文件名拼写错误，加载背景图片
    BACKGROUND_IMAGE = pygame.image.load('backgroud.png').convert()
    BACKGROUND_WIDTH = BACKGROUND_IMAGE.get_width()
    bg_x1 = 0
    bg_x2 = BACKGROUND_WIDTH
    bg_speed = 1
except pygame.error as e:
    print(f"图片加载失败: {e}")
    BACKGROUND_IMAGE = None

# Bird class
try:
    # 加载小鸟图片
    BIRD_IMAGE = pygame.image.load('bird.png').convert_alpha()
    BIRD_IMAGE.set_colorkey((255, 255, 255))
    # 定义缩放比例，将其调小到 0.2 ，你可以根据需要继续调整
    scale_factor = 0.2
    new_width = int(BIRD_IMAGE.get_width() * scale_factor)
    new_height = int(BIRD_IMAGE.get_height() * scale_factor)
    BIRD_IMAGE = pygame.transform.scale(BIRD_IMAGE, (new_width, new_height))
except pygame.error as e:
    print(f"小鸟图片加载失败: {e}")
    BIRD_IMAGE = None

# 定义不同类型小鸟的属性
BIRD_TYPES = {
    "normal": {"gravity": 0.5, "jump_strength": -8},
    "heavy": {"gravity": 0.8, "jump_strength": -10},
    "light": {"gravity": 0.3, "jump_strength": -6},
    "super": {"gravity": 0.2, "jump_strength": -12}
}

# 初始化字体
font = pygame.font.SysFont(None, 48)

# 在游戏循环前添加小鸟选择界面
def select_bird():
    selecting = True
    selected_bird = "normal"
    bird_type_list = list(BIRD_TYPES.keys())
    selected_index = 0

    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(bird_type_list)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(bird_type_list)
                elif event.key == pygame.K_RETURN:
                    selected_bird = bird_type_list[selected_index]
                    selecting = False

        screen.fill(BLACK)
        title_text = font.render("Select a Bird", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        for i, bird_type in enumerate(bird_type_list):
            color = WHITE if i == selected_index else (100, 100, 100)
            bird_text = font.render(bird_type, True, color)
            screen.blit(bird_text, (WIDTH // 2 - bird_text.get_width() // 2, 150 + i * 50))

        pygame.display.flip()
        clock.tick(60)

    return selected_bird

class Bird:
    def __init__(self, bird_type="normal"):
        self.x = 100
        self.y = HEIGHT // 2
        # 进一步调小鸟的大小，这里将其改为 15，你可以根据需要调整
        self.size = 15
        self.velocity = 0
        self.bird_type = bird_type
        self.gravity = BIRD_TYPES[bird_type]["gravity"]
        self.jump_strength = BIRD_TYPES[bird_type]["jump_strength"]

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        # Prevent bird from going off screen
        if self.y > HEIGHT - self.size:
            self.y = HEIGHT - self.size
            self.velocity = 0
            return True  # Game over if bird hits ground
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        return False

    def jump(self):
        self.velocity = self.jump_strength

    def draw(self):
        if BIRD_IMAGE:
            screen.blit(BIRD_IMAGE, (self.x, self.y))
        else:
            pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.size, self.size))



class Pipe:
    def __init__(self):
        # 调大柱子间的间距，这里将其从 150 改为 200，你可以根据需要调整
        self.spacing = 200
        # 上移管道，缩小随机范围并降低上限
        self.top_height = random.randint(100, HEIGHT - self.spacing - 250)
        self.bottom_height = HEIGHT - self.top_height - self.spacing
        self.x = WIDTH + 100 
        self.width = 50
        self.speed = 2  # 减慢管道移动速度
        self.passed = False

    def update(self):
        self.x -= self.speed
        return self.x + self.width < 0  # Return True if off-screen

    def draw(self):
        # 移除绘制图片的逻辑，只保留绘制矩形的代码
        # Top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.top_height))
        # Bottom pipe
        pygame.draw.rect(screen, GREEN, (self.x, HEIGHT - self.bottom_height, self.width, self.bottom_height))

    def collides(self, bird):
        bird_rect = pygame.Rect(bird.x, bird.y, bird.size, bird.size)
        top_pipe = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_pipe = pygame.Rect(self.x, HEIGHT - self.bottom_height, self.width, self.bottom_height)
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)

    def passes(self, bird):
        if not self.passed and bird.x > self.x + self.width:
            self.passed = True
            return True
        return False

# 新增道具颜色和类型
POWERUP_COLORS = {
    "invincible": (255, 0, 255),
    "speed_up": (255, 255, 0),
    "slow_down": (0, 255, 255)
}

class PowerUp:
    def __init__(self, current_pipe_speed):
        self.x = WIDTH
        self.y = random.randint(100, HEIGHT - 100)
        self.size = 20
        # 使用当前管道速度作为道具移动速度
        self.speed = current_pipe_speed
        # 随机选择道具类型
        self.type = random.choice(list(POWERUP_COLORS.keys()))
        self.color = POWERUP_COLORS[self.type]

    def update(self):
        self.x -= self.speed
        return self.x + self.size < 0

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def collides(self, bird):
        bird_rect = pygame.Rect(bird.x, bird.y, bird.size, bird.size)
        powerup_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        return bird_rect.colliderect(powerup_rect)

# 修改游戏变量
selected_bird_type = select_bird()
bird = Bird(selected_bird_type)
pipes = [Pipe()]
powerups = []  # 新增道具列表
score = 0
game_over = False
font = pygame.font.SysFont(None, 48)
invincible = False  # 新增无敌状态
invincible_timer = 0  # 新增无敌计时器

# 在游戏变量中添加减速计时器
slow_down_timer = 0

# 新增变量，记录当前管道速度
current_pipe_speed = 2

# 定义天气类型和对应的属性
WEATHER_TYPES = {
    "sunny": {"gravity_factor": 1, "bg_speed": 1},
    "rainy": {"gravity_factor": 1.2, "bg_speed": 0.5}
}

# 初始化天气
current_weather = "sunny"

# 初始化 Mediapipe 手部检测模块和摄像头
mp_hands = mp.solutions.hands

# 修改 max_num_hands 为 2，允许检测两只手
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
# 初始化摄像头
cap = cv2.VideoCapture(0)

# 新增闪烁背景颜色列表
FLASH_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
flash_index = 0
flash_timer = 0
FLASH_DURATION = 30  # 闪烁持续帧数

# Game loop
running = True
frame_count = 0
while running:
    # 读取摄像头帧
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        hand_count = len(results.multi_hand_landmarks)
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # 获取食指指尖坐标
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h, w, c = frame.shape
            index_x, index_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

            if i == 0:  # 第一只手控制小鸟跳跃
                if index_y < h // 2 and not game_over:
                    bird.jump()
            elif i == 1:  # 第二只手触发闪烁效果
                if index_y < h // 2:
                    flash_timer = FLASH_DURATION

    # 处理闪烁效果
    if flash_timer > 0:
        flash_timer -= 1
        screen.fill(FLASH_COLORS[flash_index])
        if flash_timer == 0:
            flash_index = (flash_index + 1) % len(FLASH_COLORS)
    elif BACKGROUND_IMAGE:
        screen.blit(BACKGROUND_IMAGE, (bg_x1, 0))
        screen.blit(BACKGROUND_IMAGE, (bg_x2, 0))
    else:
        screen.fill(BLACK)

    cv2.imshow('Hand Control', frame)
    cv2.waitKey(1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                # 让玩家重新选择小鸟类型
                new_bird_type = select_bird()
                bird = Bird(new_bird_type)
                pipes = [Pipe()]
                powerups = []  # 重置道具列表
                score = 0
                game_over = False
                frame_count = 0
                # 重置减速计时器
                slow_down_timer = 0
                # 重置管道速度
                current_pipe_speed = 2
                # 重置天气
                current_weather = "sunny"

    if not game_over:
        # Update bird
        if bird.update():
            game_over = True

        # Update pipes
        for pipe in pipes[:]:
            if pipe.update():
                pipes.remove(pipe)
            if not invincible and pipe.collides(bird):
                game_over = True
            if pipe.passes(bird):
                score += 1

        # 每 90 帧添加一个新管道
        frame_count += 1
        if frame_count % 90 == 0:
            new_pipe = Pipe()
            new_pipe.speed = current_pipe_speed
            pipes.append(new_pipe)

        # 增大帧数间隔，减少道具生成频率，例如每 300 帧添加一个新道具
        # 修改道具生成部分
        if frame_count % 300 == 0:
            powerups.append(PowerUp(current_pipe_speed))

        # 每 600 帧随机切换天气
        if frame_count % 600 == 0:
            weather_types = list(WEATHER_TYPES.keys())
            # 确保切换到不同的天气
            current_weather = random.choice([w for w in weather_types if w != current_weather])

        # 更新道具
        for powerup in powerups[:]:
            if powerup.update():
                powerups.remove(powerup)
            if powerup.collides(bird):
                print(f"Collided with {powerup.type} power-up")  # 添加调试信息
                powerups.remove(powerup)
                if powerup.type == "invincible":
                    invincible = True
                    invincible_timer = 180
                    print("Activated invincible power-up")  # 添加调试信息
                elif powerup.type == "speed_up":
                    current_pipe_speed = 4
                    for pipe in pipes:
                        pipe.speed = current_pipe_speed
                    print("Activated speed-up power-up")  # 添加调试信息
                elif powerup.type == "slow_down":
                    # 确保当前管道速度被正确设置为慢速
                    current_pipe_speed = 1
                    for pipe in pipes:
                        # 直接更新每个管道的速度
                        pipe.speed = current_pipe_speed
                    slow_down_timer = 180  # 设置减速时间为 3 秒（60 帧/秒）
                    print("Activated slow-down power-up")  # 添加调试信息

        # 根据天气调整小鸟重力和背景速度
        bird.gravity = BIRD_TYPES[bird.bird_type]["gravity"] * WEATHER_TYPES[current_weather]["gravity_factor"]
        bg_speed = WEATHER_TYPES[current_weather]["bg_speed"]

        # 减少无敌时间
        if invincible:
            invincible_timer -= 1
            if invincible_timer <= 0:
                invincible = False
                invincible_timer = 0  # 确保计时器不会为负数

        # 减少减速时间
        if slow_down_timer > 0:
            slow_down_timer -= 1
            if slow_down_timer <= 0:
                current_pipe_speed = 2
                for pipe in pipes:
                    pipe.speed = current_pipe_speed

    # 滚动背景
    if BACKGROUND_IMAGE:
        bg_x1 -= bg_speed
        bg_x2 -= bg_speed
        if bg_x1 <= -BACKGROUND_WIDTH:
            bg_x1 = BACKGROUND_WIDTH
        if bg_x2 <= -BACKGROUND_WIDTH:
            bg_x2 = BACKGROUND_WIDTH

    # Draw everything
    if BACKGROUND_IMAGE:
        screen.blit(BACKGROUND_IMAGE, (bg_x1, 0))
        screen.blit(BACKGROUND_IMAGE, (bg_x2, 0))
    else:
        screen.fill(BLACK)
    for pipe in pipes:
        pipe.draw()
    for powerup in powerups:
        powerup.draw()
    bird.draw()

    # 显示无敌状态
    if invincible:
        invincible_text = font.render("Invincible!", True, WHITE)
        screen.blit(invincible_text, (WIDTH // 2 - 70, 100))

    # Display score
    score_text = font.render(str(score), True, WHITE)
    screen.blit(score_text, (WIDTH // 2, 50))

    # Display game over screen
    if game_over:
        game_over_text = font.render("Game Over!", True, WHITE)
        score_display = font.render(f"Score: {score}", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        screen.blit(score_display, (WIDTH // 2 - 50, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))

    # 显示当前天气
    weather_text = font.render(f"Weather: {current_weather}", True, WHITE)
    screen.blit(weather_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

# 释放摄像头资源
cap.release()
cv2.destroyAllWindows()

pygame.quit()
