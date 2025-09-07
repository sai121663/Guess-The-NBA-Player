"""This file will contain the backend of the 'Guess the Player' game."""

import pygame
import sys
from typing import Optional
from Backend import get_player, get_options
import os
import random

# Display setup
pygame.init()
pygame.mixer.init()     # Lets us play music clips
screen = pygame.display.set_mode((900, 500))

# Fonts & Colours
fonts = {'small_font': pygame.font.SysFont("comic sans", 24),
         'big_font': pygame.font.SysFont("comic sans", 32),
         'bold_font': pygame.font.SysFont("impact", 32),
         'title_font': pygame.font.SysFont("chelsea market", 64),
         'points_font': pygame.font.SysFont("impact", 36),
         'points_font_2': pygame.font.SysFont("impact", 18),
         'points_font_3': pygame.font.SysFont("impact", 24)}

colours = {'WHITE': (255, 255, 255), 'GREY': (128, 128, 128), 'GREEN': (34, 139, 34), 'RED': (200, 50, 50),
           'BLUE': (30, 144, 255), 'YELLOW': (255, 215, 0), 'BLACK': (0, 0, 0)}

# Game variables
clock = pygame.time.Clock()
player_points = 0
music_on = True

# Load background theme music
background_music = pygame.mixer.Sound("NBA on NBC Theme.mp3")
music_channel = pygame.mixer.Channel(0)     # Creates a channel for the background score to be played (able to pause/lower volume)


def end_program() -> None:
    """Ends the program."""

    pygame.quit()
    sys.exit()


def display_player_image() -> None:
    """Display the current's player's headshot."""

    player_img = pygame.image.load("curr_player.jpg").convert()
    screen.blit(player_img, (50, 125))

    pygame.display.update()

# Not used
def draw_clue_button() -> None:
    """DRAW the CLUE button."""

    # Drawing a red circle & "clue" as text
    pygame.draw.circle(screen, 'RED', (175, 400), 50)
    clue_label = fonts['small_font'].render("CLUE", True, colours['WHITE'])
    screen.blit(clue_label, (145, 380))

    pygame.display.update()


def display_options(choices_list: list[str]) -> None:
    """Display the buttons for the corresponding options."""

    start_x = 400
    vertical_spacing = 50

    for i, name in enumerate(choices_list):
        # Draw a rectangle around each option
        # Parameters: (screen, colour, (x, y, width, height))
        button_rect = pygame.Rect(start_x, 80 + i * (40 + vertical_spacing), 400, 65)
        pygame.draw.rect(screen, colours['BLUE'], button_rect)

        button_text = fonts['big_font'].render(name, True, colours['WHITE'])    # Draws the text
        rect_text = button_text.get_rect(center=button_rect.center)     # Centers the text inside the button
        screen.blit(button_text, rect_text)     # Draws the current text on the screen in a centered position

        pygame.display.update()


def get_difficulty() -> str:
    """Display the screen that allows the player to choose between a CASUAL and DIEHARD gameplay mode"""

    # Adds a background image of basketballs
    display_scaled_image(os.path.join("Backgrounds", "basketballs.jpg"), (900, 500), (0, 0))

    # The last parameter creates a WHITE background for the text
    screen_text = fonts["title_font"].render("PICK A MODE:", True, colours['BLACK'], (255, 255, 255))
    screen.blit(screen_text, (100, 50))

    # Displaying images of MJ and a random NBA player
    casual_player_img = pygame.image.load("casual_player_img.png").convert()
    screen.blit(casual_player_img, (100, 150))
    diehard_player_img = pygame.image.load("diehard_player_img.jpg").convert()
    screen.blit(diehard_player_img, (500, 150))

    # Creating "CASUAL" and "DIEHARD" labels
    casual_label = fonts["big_font"].render("CASUAL", True, colours['BLACK'], (255, 255, 255))
    screen.blit(casual_label, (175, 400))
    diehard_label = fonts["big_font"].render("DIEHARD", True, colours['BLACK'], (255, 255, 255))
    screen.blit(diehard_label, (575, 400))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_program()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos_x, pos_y = pygame.mouse.get_pos()

                if 100 <= pos_x <= 400 and 150 <= pos_y <= 450:
                    return "casual"
                elif 500 <= pos_x <= 800 and 150 <= pos_y <= 450:
                    return "diehard"


def check_correct_ans(correct_ans: str, user_ans: str, nba_images: tuple[list, list], audio_calls: tuple[list, list]) -> Optional[bool]:
    """Display whether the user's answer is CORRECT or WRONG."""

    if correct_ans == user_ans:
        display_scaled_image(os.path.join("Backgrounds", "basketball_net.jpg"), (900, 500), (0, 0))
        is_correct = True
        display_message = fonts['big_font'].render("CORRECT!", True, colours['GREEN'], (255, 255, 0))
        display_nba_moment(nba_images[0])   # nba_images is a tuple of (clutch_images, choke_images)  # audio_calls is a tuple of (good calls, bad calls)

    else:
        display_scaled_image(os.path.join("Backgrounds", "man_disappointed.jpg"), (900, 500), (0, 0))
        is_correct = False
        display_message = fonts['big_font'].render("WRONG!", True, colours['RED'], (255, 255, 0))
        display_nba_moment(nba_images[1])

    screen.blit(display_message, (350, 185))

    press_enter_msg = fonts['small_font'].render('(Press ENTER to continue)', True, colours['GREY'], (255, 255, 0))
    screen.blit(press_enter_msg, (275, 250))

    pygame.display.update()

    # Playing the announcer's call after updating the result screen
    # audio_calls is a tuple of (good calls, bad calls)
    if is_correct:
        play_announcer_sound(audio_calls[0])
    else:
        play_announcer_sound(audio_calls[1])

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_program()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return is_correct

def display_scaled_image(file_path: str, new_size: tuple[int, int], position: tuple[int, int]) -> None:
    """Scale the given image to 'new_size' & draw it to the screen at 'position'. """

    unscaled_img = pygame.image.load(file_path).convert_alpha()
    scaled_img = pygame.transform.smoothscale(unscaled_img, new_size)
    screen.blit(scaled_img, position)



def load_clutch_images() -> list:
    """Return a list of valid file paths for the images in the 'Clutch Moments' folder. """

    clutch_moments = []

    # Traverses through "Clutch Moments" folder and creates a list of valid file paths
    # e.g. ["Clutch Moments/jordan_1998.jpg", "Clutch Moments/kawhi_2019.jpg"]
    for filename in os.listdir("Clutch Moments"):
        img_path = os.path.join("Clutch Moments", filename)
        clutch_moments.append(img_path)

    return clutch_moments


def load_choke_images() -> list:
    """Return a list of valid file paths for the images in the 'Choke Moments' folder. """

    choke_moments = []

    for filename in os.listdir("Choke Moments"):
        img_path = os.path.join("Choke Moments", filename)
        choke_moments.append(img_path)

    return choke_moments


def display_nba_moment(images_list: list) -> None:
    """Display an image of a clutch/choke NBA moment, based on whether the user's answer was correct."""

     # Randomly selecting one of the images
    random_image = random.choice(images_list)

    # Scaling the image and displaying it to the screen
    display_scaled_image(random_image, (271, 153), (540, 325))


def update_points(is_prev_correct: bool, difficulty: str, points: int) -> int:
    """Update point total based on whether their answer was correct/wrong."""

    # convert_alpha() removes the white background & makes the image transparent
    up_arrow_img = pygame.image.load("green_arrow.png").convert_alpha()
    scaled_up_arrow = pygame.transform.smoothscale(up_arrow_img, (15, 15))

    down_arrow_img = pygame.image.load("red_arrow.png").convert_alpha()
    scaled_down_arrow = pygame.transform.smoothscale(down_arrow_img, (15, 15))

    if is_prev_correct:

        if difficulty == "casual":
            points += 100
            points_change_text = fonts["points_font_2"].render(f"100", True, colours['GREEN'])
        else:
            points += 200
            points_change_text = fonts["points_font_2"].render("200", True, colours['GREEN'])

        screen.blit(scaled_up_arrow, (50, 473))

    else:
        points -= 50
        points_change_text = fonts["points_font_2"].render("50", True, colours['RED'])

        screen.blit(scaled_down_arrow, (50, 473))

    # Printing the user's point total
    display_points(points)

    # Displaying how much the user's point total went UP/DOWN by
    screen.blit(points_change_text, (75, 468))

    pygame.display.update()

    return points

def display_points(total_points: int) -> None:
    """Displaying the user's current point total."""

    points_text = fonts["points_font"].render(f"Points:  {total_points}", True, colours['YELLOW'])
    screen.blit(points_text, (50, 425))

def fetch_next_player(difficulty: str, music_playing: bool) -> tuple:
    """Update the screen to show the next question. Return the player & the list of options."""

    # Uploading a background image
    screen.fill(colours['BLACK'])
    display_scaled_image(os.path.join("Backgrounds", "dark_background.jpg"), (900, 500), (0, 0))

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            end_program()

    # Creating a player object based on whether the user clicked "CASUAL" or "DIEHARD"
    player_obj = get_player(difficulty)
    display_player_image()

    choices_list = get_options(player_obj.full_name)
    display_options(choices_list)

    # Shows whether the music is playing
    draw_music_icon(music_playing)

    # Give the user the option to quit the game OR change the mode
    draw_quit_button()
    draw_switch_mode_button()

    pygame.display.update()

    return player_obj, choices_list, music_playing


def draw_music_icon(music_playing: bool) -> None:
    """Displays an image of Homer Simpson, based on whether the music is ON/OFF."""

    # Drawing a black rectangle to cover up the previous icon
    black_rect = pygame.Rect(810, 420, 60, 60)
    pygame.draw.rect(screen, colours['BLACK'], black_rect)

    # Shows that the music is ON
    if music_playing:

        music_channel.set_volume(1.0)

        display_scaled_image("simpson_vibing.png", (60, 60), (810, 420))

    else:

        # Muting the volume
        music_channel.set_volume(0.0)

        display_scaled_image("simpson_bored.png", (60, 60), (810, 420))


    pygame.display.update()


def play_music() -> None:
    """Plays the background song & allows the user to mute the music"""

    music_channel.play(background_music, loops=-1)


def load_announcer_calls() -> Optional[tuple]:
    """Return two lists consisting of the filenames of the good & bad announcer calls."""

    good_calls = []
    bad_calls = []

    # Traversing through the subfolders in "Announcer Audio" folder
    for file in os.listdir("Announcer Audio"):

        # Traversing through the folders in each of the subfolders
        for filename in os.listdir(os.path.join("Announcer Audio", file)):

            # Creating a valid filepath (e.g. "Announcer Audio/Good/Bang.mp3")
            filepath = os.path.join("Announcer Audio", file, filename)

            if file == "Good":
                good_calls.append(filepath)

            elif file == "Bad":
                bad_calls.append(filepath)

    return good_calls, bad_calls


def play_announcer_sound(audio_list: list) -> None:
    """Plays a random NBA announcer call, from the given list."""

    if music_on:
        music_channel.set_volume(0.2)

    # Randomly choosing an audio file from the list & turning it into a Sound object
    random_announcer_call = random.choice(audio_list)
    sound = pygame.mixer.Sound(random_announcer_call)

    # Creating a 2nd channel to control the announcer's audio
    announcer_channel = pygame.mixer.Channel(1)
    announcer_channel.play(sound)

    # Check every 10 ms if the announcer_channel is still being played
    while announcer_channel.get_busy():
        pygame.time.delay(10)

    # Resetting the music_channel's volume to its original state
    if music_on:
        music_channel.set_volume(1.0)


def intro_screen() -> None:
    """Display disclaimers & instructions before the game starts."""

    screen.fill(colours['BLACK'])

    pygame.draw.rect(screen, colours['YELLOW'], (0, 0, 900, 100))

    # Creating a SHADOW of the game title
    shadow = fonts['title_font'].render("hOOpster", True, colours['WHITE'])
    screen.blit(shadow, (322, 30))

    game_title = fonts['title_font'].render("hOOpster", True, colours['RED'])
    screen.blit(game_title, (325, 35))

    screen.blit(fonts['bold_font'].render("BEFORE YOU START...",
                                           True, colours['WHITE']), (20, 115))

    # Message 1: Mute/unmute music
    message_1 = fonts['small_font'].render("Toggle between          and          to mute/unmute music",
                                           True, colours['BLUE'])
    screen.blit(message_1, (50, 190))

    # Image of "music on" icon
    display_scaled_image("simpson_vibing.png", (60, 60), (225, 175))

    # Image of "music off" icon
    display_scaled_image("simpson_bored.png", (60, 60), (340, 175))

    # Message 2: Points gained/lost for each question
    message_2 = fonts['small_font'].render("        for \"CASUAL\" mode,          for \"DIEHARD\","
                                           "        for wrong guesses", True, colours['BLUE'])
    screen.blit(message_2, (50, 290))

    points_msg_1 = fonts['points_font_3'].render("+100", True, colours['GREEN'])
    screen.blit(points_msg_1, (50, 293))

    points_msg_2 = fonts['points_font_3'].render("+200", True, colours['GREEN'])
    screen.blit(points_msg_2, (348, 293))

    points_msg_3 = fonts["points_font_3"].render("-50", True, colours['RED'])
    screen.blit(points_msg_3, (608, 293))

    # Telling the user to press enter
    press_enter_msg = fonts["small_font"].render("(Click ENTER)", True, colours['WHITE'])
    screen.blit(press_enter_msg, (675, 440))

    pygame.display.update()

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_program()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

def draw_quit_button() -> None:
    """Draw the quit button."""

    rect_button = pygame.Rect(800, 0, 100, 50)
    pygame.draw.rect(screen, colours['RED'], rect_button)   # Draws a red rectangle on the screen

    button_text = fonts['bold_font'].render("QUIT", True, colours['WHITE'])
    rect_text = button_text.get_rect(center=rect_button.center)     # Centers the text inside the button
    screen.blit(button_text, rect_text)

    pygame.display.update()


def quit_game() -> None:
    """Display the player's points before ending the game."""

    screen.fill(colours['BLACK'])

    # If the user has (-) points, display it in red
    if player_points >= 0:
        points_msg = fonts['bold_font'].render(f"You ended with {player_points} points!", True, colours['GREEN'])

    else:
        points_msg = fonts['bold_font'].render(f"You ended with {player_points} points!", True, colours['RED'])

    screen.blit(points_msg, (50, 50))

    display_scaled_image(os.path.join("Images", "mamba_out.jpg"), (480, 334), (200, 125))

    pygame.display.update()
    pygame.time.wait(3000)

    end_program()

def draw_switch_mode_button() -> None:
    """Display a button that allows the user to change the mode mid-game."""

    rect_button = pygame.Rect(0, 0, 170, 50)
    pygame.draw.rect(screen, colours['GREEN'], rect_button)  # Draws a green rectangle on the screen

    button_text = fonts['points_font_3'].render("SWITCH MODE", True, colours['WHITE'])
    rect_text = button_text.get_rect(center=rect_button.center)  # Centers the text inside the button
    screen.blit(button_text, rect_text)

    pygame.display.update()

def switch_mode(game_mode: str) -> str:
    """Change the mode from 'casual' to 'diehard', and vice versa, and return the new game mode."""

    if game_mode == "casual":
        game_mode = "diehard"
    else:
        game_mode = "casual"

    return game_mode

# Loading images (tuple of (clutch images, choke images))
images = load_clutch_images(), load_choke_images()

# Loading announcer calls (tuple of (good calls, bad calls))
announcer_calls = load_announcer_calls()

play_music()
intro_screen()
mode = get_difficulty()

# Fetch the first NBAPlayer object
player, choices, music_on = fetch_next_player(mode, music_on)

# Game loop
running = True
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            # Checks if the user clicked on the options
            click_x, click_y = pygame.mouse.get_pos()

            for i in range(len(choices)):
                button_y = 80 + (i * 90)   # Starting y-position of current option box

                # Checks if the user clicked on the "QUIT" button
                if 800 <= click_x <= 900 and 0 <= click_y <= 50:
                    quit_game()

                # Switch the game mode
                elif 0 <= click_x <= 170 and 0 <= click_y <= 50:
                    mode = switch_mode(mode)

                    # Display the next question & options
                    player, choices, music_on = fetch_next_player(mode, music_on)
                    display_points(player_points)

                    break

                elif 400 <= click_x <= 800 and button_y <= click_y <= button_y + 65:
                    user_answer = choices[i]    # Storing the user's response

                    is_correct = check_correct_ans(player.full_name, user_answer, images, announcer_calls)

                    # Display the next question & options
                    player, choices, music_on = fetch_next_player(mode, music_on)

                    # Display the updated points total
                    player_points = update_points(is_correct, mode, player_points)

            # Checks whether the user clicked on the Simpson image and toggles between music ON/OFF icon
            if 810 <= click_x <= 870 and 420 <= click_y <= 480:
                music_on = not music_on
                draw_music_icon(music_on)   # Immediately changes the icon to indicate that the music is MUTED (and vice versa)

    pygame.display.update()

    clock.tick(60)  # Prevents glitches by ensuring the game runs at a reasonable speed


# End the program
end_program()


# Instructions:
# ------------------------------------
# - Create a CLUE button:
#         - Either the player's NICKNAME (if it exists) or the year they RETIRED


