import asyncio
import platform
import pygame # type: ignore
import ujson # type: ignore

# Constants
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
FONT_SIZE = 40

# Menu options
MENU_OPTIONS = ["Start New Game", "Load Game", "Credits", "Exit"]
SELECTED_INDEX = 0

# Game state variables
current_state = "menu"
current_scene = None
current_step = 0
scenes = {}
background = None
background_menu = None
credits_scroll_y = 0
credits_text = [
    "Stellar Odyssey: Humanity's Reach",
    "",
    "Developed by: Atom",
    "Designed by: Atom",
    "Art by: Atom",
    "Music by: Atom",
    "Story by: Atom",
    "Programming by: Atom",
    "",
    "Thank you for playing!"
]
paths = {}
ENDING_OPTIONS = ["Return to Main Menu", "View Credits"]
ending_selected_index = 0

def setup():
    global screen, font, menu_texts, menu_rects, background_menu, credits_scroll_y
    pygame.init()
    screen = pygame.display.set_mode((1000, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Stellar Odyssey: Humanity's Reach")
    font = pygame.font.Font(None, FONT_SIZE)
    
    # Load menu background
    background_menu = pygame.image.load("./images/background_menu.jpg")
    
    # Pre-render menu text and calculate positions
    menu_texts = []
    menu_rects = []
    for i, option in enumerate(MENU_OPTIONS):
        text = font.render(option, True, WHITE)
        rect = text.get_rect(center=(400, 200 + i * 60))
        menu_texts.append(text)
        menu_rects.append(rect)
    
    # Initialize credits scroll position
    credits_scroll_y = screen.get_height()
    
    # Initialize and play background music
    pygame.mixer.init()
    pygame.mixer.music.load("./audio/menu_music.wav")
    pygame.mixer.music.play(-1)

def save_game():
    save_data = {
        "current_scene": current_scene,
        "current_step": current_step,
        "selected_index": SELECTED_INDEX
    }
    with open("./data/save.json", "w") as f:
        ujson.dump(save_data, f)

def load_game():
    global current_state, current_scene, current_step, SELECTED_INDEX, scenes, background
    try:
        with open("./data/save.json", "r") as f:
            save_data = ujson.load(f)
        current_scene = save_data["current_scene"]
        current_step = save_data["current_step"]
        SELECTED_INDEX = save_data["selected_index"]
        
        # Load scenes if not already loaded
        if not scenes:
            with open("./data/scenes.json", "r") as f:
                data = ujson.load(f)
            global paths
            paths = data["paths"]
            scenes.clear()
            for scene_name, scene_data in data["scenes"].items():
                scenes[scene_name] = scene_data
                # Resolve background image path
                if scene_data["background_path"] in paths["images"]:
                    scenes[scene_name]["background"] = pygame.image.load(paths["images"][scene_data["background_path"]])
                else:
                    default_background = pygame.Surface((800, 600))
                    default_background.fill((20, 20, 50))
                    scenes[scene_name]["background"] = default_background
        
        background = scenes[current_scene]["background"]
        current_state = "game"
        pygame.mixer.music.stop()
        if scenes[current_scene]["background_audio"] in paths["audio"]:
            pygame.mixer.music.load(paths["audio"][scenes[current_scene]["background_audio"]])
            pygame.mixer.music.play(-1)
    except FileNotFoundError:
        print("No save file found. Starting new game instead.")
        start_game()

def start_game():
    global current_state, current_scene, current_step, scenes, background, paths
    current_state = "game"
    current_scene = "start"
    current_step = 0
    SELECTED_INDEX = 0
    
    # Load scenes from JSON file
    with open("./data/scenes.json", "r") as f:
        data = ujson.load(f)
    
    paths = data["paths"]
    scenes.clear()
    for scene_name, scene_data in data["scenes"].items():
        scenes[scene_name] = scene_data
        # Load background image or use default if empty
        if scene_data["background_path"] in paths["images"]:
            scenes[scene_name]["background"] = pygame.image.load(paths["images"][scene_data["background_path"]])
        else:
            default_background = pygame.Surface((800, 600))
            default_background.fill((20, 20, 50))
            scenes[scene_name]["background"] = default_background
    
    background = scenes[current_scene]["background"]
    # Stop menu music and play scene music if available
    pygame.mixer.music.stop()
    if scenes[current_scene]["background_audio"] in paths["audio"]:
        pygame.mixer.music.load(paths["audio"][scenes[current_scene]["background_audio"]])
        pygame.mixer.music.play(-1)
    save_game()

def render_multiline_text(text, font, color, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, color)
        if test_surface.get_width() <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return [font.render(line, True, color) for line in lines]

def draw_menu():
    global screen, background_menu, menu_texts, menu_rects
    width, height = screen.get_size()
    scaled_background = pygame.transform.scale(background_menu, (width, height))
    screen.blit(scaled_background, (0, 0))
    
    title_text = font.render("Stellar Odyssey: Humanity's Reach", True, WHITE)
    title_rect = title_text.get_rect(center=(width // 2, height // 5))
    screen.blit(title_text, title_rect)
    
    for i, (text, rect) in enumerate(zip(menu_texts, menu_rects)):
        rect.center = (width // 2, height // 3 + i * 60)
        color = WHITE if i == SELECTED_INDEX else GRAY
        text = font.render(MENU_OPTIONS[i], True, color)
        screen.blit(text, rect)
    
    pygame.display.flip()

def draw_game():
    global screen, background
    width, height = screen.get_size()
    scaled_background = pygame.transform.scale(background, (width, height))
    screen.blit(scaled_background, (0, 0))
    
    step = scenes[current_scene]["steps"][current_step]
    if step["type"] == "dialogue":
        # Display dialogue text
        lines = render_multiline_text(step["text"], font, WHITE, width - 40)
        text_box_rect = pygame.Rect(20, height * 3 // 4, width - 40, height // 4 - 20)
        pygame.draw.rect(screen, BLACK, text_box_rect, 0)
        y = text_box_rect.top + 10
        for line in lines:
            screen.blit(line, (text_box_rect.left + 10, y))
            y += line.get_height() + 5
        
        # If there are choices, display them higher on the screen
        if "choices" in step:
            choice_y = height // 4  # Moved higher to avoid overlap
            for i, choice in enumerate(step["choices"]):
                text = font.render(choice["text"], True, WHITE if i != SELECTED_INDEX else GRAY)
                rect = text.get_rect(center=(width // 2, choice_y + i * 60))
                screen.blit(text, rect)
    
    pygame.display.flip()

def draw_credits():
    global screen, background_menu, credits_scroll_y
    width, height = screen.get_size()
    scaled_background = pygame.transform.scale(background_menu, (width, height))
    screen.blit(scaled_background, (0, 0))
    
    y = credits_scroll_y
    for line in credits_text:
        text = font.render(line, True, WHITE)
        rect = text.get_rect(center=(width // 2, y))
        screen.blit(text, rect)
        y += 40
    
    # Scroll credits
    credits_scroll_y -= 2
    if y < 0:
        credits_scroll_y = height
    
    pygame.display.flip()

def draw_ending():
    global screen, background, ending_selected_index
    width, height = screen.get_size()
    scaled_background = pygame.transform.scale(background, (width, height))
    screen.blit(scaled_background, (0, 0))
    
    # Display "Game Over" message
    game_over_text = font.render("Game Over", True, WHITE)
    game_over_rect = game_over_text.get_rect(center=(width // 2, height // 4))
    screen.blit(game_over_text, game_over_rect)
    
    # Display ending options
    for i, option in enumerate(ENDING_OPTIONS):
        text = font.render(option, True, WHITE if i == ending_selected_index else GRAY)
        rect = text.get_rect(center=(width // 2, height // 2 + i * 60))
        screen.blit(text, rect)
    
    pygame.display.flip()

def handle_menu_input():
    global SELECTED_INDEX, screen, background_menu, menu_rects
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            pygame.quit()
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                SELECTED_INDEX = (SELECTED_INDEX - 1) % len(MENU_OPTIONS)
            if event.key == pygame.K_DOWN:
                SELECTED_INDEX = (SELECTED_INDEX + 1) % len(MENU_OPTIONS)
            if event.key == pygame.K_RETURN:
                return handle_selection()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(menu_rects):
                if rect.collidepoint(mouse_pos):
                    SELECTED_INDEX = i
                    return handle_selection()
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(menu_rects):
                if rect.collidepoint(mouse_pos):
                    SELECTED_INDEX = i
                    break
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            for i, rect in enumerate(menu_rects):
                rect.center = (event.w // 2, event.h // 3 + i * 60)
    return True

def handle_game_input():
    global current_step, current_scene, SELECTED_INDEX, background, current_state
    step = scenes[current_scene]["steps"][current_step]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False
        if "choices" in step:
            # Handle choice selection
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    SELECTED_INDEX = (SELECTED_INDEX - 1) % len(step["choices"])
                if event.key == pygame.K_DOWN:
                    SELECTED_INDEX = (SELECTED_INDEX + 1) % len(step["choices"])
                if event.key == pygame.K_RETURN:
                    next_scene = step["choices"][SELECTED_INDEX]["next"]
                    current_scene = next_scene
                    current_step = 0
                    SELECTED_INDEX = 0
                    background = scenes[current_scene]["background"]
                    # Change background music
                    pygame.mixer.music.stop()
                    if scenes[current_scene]["background_audio"] in paths["audio"]:
                        pygame.mixer.music.load(paths["audio"][scenes[current_scene]["background_audio"]])
                        pygame.mixer.music.play(-1)
                    save_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                width, height = screen.get_size()
                choice_y = height // 4
                for i, choice in enumerate(step["choices"]):
                    text = font.render(choice["text"], True, WHITE)
                    rect = text.get_rect(center=(width // 2, choice_y + i * 60))
                    if rect.collidepoint(mouse_pos):
                        next_scene = choice["next"]
                        current_scene = next_scene
                        current_step = 0
                        SELECTED_INDEX = 0
                        background = scenes[current_scene]["background"]
                        # Change background music
                        pygame.mixer.music.stop()
                        if scenes[current_scene]["background_audio"] in paths["audio"]:
                            pygame.mixer.music.load(paths["audio"][scenes[current_scene]["background_audio"]])
                            pygame.mixer.music.play(-1)
                        save_game()
                        break
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                width, height = screen.get_size()
                choice_y = height // 4
                for i, choice in enumerate(step["choices"]):
                    text = font.render(choice["text"], True, WHITE)
                    rect = text.get_rect(center=(width // 2, choice_y + i * 60))
                    if rect.collidepoint(mouse_pos):
                        SELECTED_INDEX = i
                        break
        else:
            # Handle dialogue advancement
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if current_step < len(scenes[current_scene]["steps"]) - 1:
                    current_step += 1
                    save_game()
                else:
                    # Transition to ending state for all paths
                    current_state = "ending"
                    pygame.mixer.music.stop()
    return True

def handle_credits_input():
    global current_state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            current_state = "menu"
            # Restart menu music
            pygame.mixer.music.stop()
            pygame.mixer.music.load("./audio/menu_music.wav")
            pygame.mixer.music.play(-1)
    return True

def handle_ending_input():
    global current_state, ending_selected_index
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ending_selected_index = (ending_selected_index - 1) % len(ENDING_OPTIONS)
            if event.key == pygame.K_DOWN:
                ending_selected_index = (ending_selected_index + 1) % len(ENDING_OPTIONS)
            if event.key == pygame.K_RETURN:
                if ending_selected_index == 0:  # Return to Main Menu
                    current_state = "menu"
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("./audio/menu_music.wav")
                    pygame.mixer.music.play(-1)
                elif ending_selected_index == 1:  # View Credits
                    current_state = "credits"
                    pygame.mixer.music.stop()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            width, height = screen.get_size()
            for i, option in enumerate(ENDING_OPTIONS):
                text = font.render(option, True, WHITE)
                rect = text.get_rect(center=(width // 2, height // 2 + i * 60))
                if rect.collidepoint(mouse_pos):
                    ending_selected_index = i
                    if ending_selected_index == 0:  # Return to Main Menu
                        current_state = "menu"
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("./audio/menu_music.wav")
                        pygame.mixer.music.play(-1)
                    elif ending_selected_index == 1:  # View Credits
                        current_state = "credits"
                        pygame.mixer.music.stop()
                    break
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            width, height = screen.get_size()
            for i, option in enumerate(ENDING_OPTIONS):
                text = font.render(option, True, WHITE)
                rect = text.get_rect(center=(width // 2, height // 2 + i * 60))
                if rect.collidepoint(mouse_pos):
                    ending_selected_index = i
                    break
    return True

def handle_selection():
    global current_state
    if SELECTED_INDEX == 0:
        start_game()
    elif SELECTED_INDEX == 1:
        load_game()
    elif SELECTED_INDEX == 2:
        current_state = "credits"
        pygame.mixer.music.stop()
    elif SELECTED_INDEX == 3:
        pygame.mixer.music.stop()
        pygame.quit()
        return False
    return True

def update_menu():
    if not handle_menu_input():
        return False
    draw_menu()
    return True

def update_game():
    if not handle_game_input():
        return False
    draw_game()
    return True

def update_credits():
    if not handle_credits_input():
        return False
    draw_credits()
    return True

def update_ending():
    if not handle_ending_input():
        return False
    draw_ending()
    return True

async def main():
    setup()
    while True:
        if current_state == "menu":
            if not update_menu():
                break
        elif current_state == "game":
            if not update_game():
                break
        elif current_state == "credits":
            if not update_credits():
                break
        elif current_state == "ending":
            if not update_ending():
                break
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())