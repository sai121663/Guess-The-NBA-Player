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
        pygame.draw.rect(screen, colours['RED'], button_rect)

        button_text = fonts['big_font'].render(name, True, colours['WHITE'])    # Draws the text
        rect_text = button_text.get_rect(center=button_rect.center)     # Centres the text inside the button
        screen.blit(button_text, rect_text)     # Draws the current text on the screen in a centered position

        pygame.display.update()


def get_difficulty() -> str:
    """Display the screen that allows the player to choose between a CASUAL and DIEHARD gameplay mode"""

    # Adds a background image of basketballs
    background_img = pygame.image.load("basketball_background.jpg").convert()
    scaled_background = pygame.transform.smoothscale(background_img, (900, 500))
    screen.blit(scaled_background, (0, 0))

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


def check_correct_ans(correct_ans: str, user_ans: str, clutch_moments: list, choke_moments: list) -> Optional[bool]:
    """Display whether the user's answer is CORRECT or WRONG."""

    if correct_ans == user_ans:
        screen.fill(colours['WHITE'])
        is_correct = True
        display_message = fonts['big_font'].render("CORRECT!", True, colours['GREEN'])
        display_nba_moment(clutch_moments)

    else:
        screen.fill(colours['BLACK'])
        is_correct = False
        display_message = fonts['big_font'].render("WRONG!", True, colours['RED'])
        display_nba_moment(choke_moments)

    screen.blit(display_message, (350, 185))

    press_enter_msg = fonts['small_font'].render('(Press ENTER to continue)', True, colours['GREY'])
    screen.blit(press_enter_msg, (275, 250))

    pygame.display.update()

    play_announcer_sound(is_correct)  # Testing purposes

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_program()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return is_correct


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
    nba_image = pygame.image.load(random_image).convert_alpha()
    scaled_nba_image = pygame.transform.smoothscale(nba_image, (271, 153))
    screen.blit(scaled_nba_image, (540, 325))


def update_points(is_prev_correct: bool, difficulty: str, points: int) -> int:
    """Update & display the user's point total after each question."""

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
    points_text = fonts["points_font"].render(f"Points:  {points}", True, colours['YELLOW'])
    screen.blit(points_text, (50, 425))

    # Displaying how much the user's point total went UP/DOWN by
    screen.blit(points_change_text, (75, 468))

    pygame.display.update()

    return points


def fetch_next_player(difficulty: str, music_playing: bool) -> tuple:
    """Update the screen to show the next question. Return the player & the list of options."""

    screen.fill(colours['BLACK'])

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

        singing_img = pygame.image.load("simpson_vibing.png").convert_alpha()
        downsized_singing_img = pygame.transform.smoothscale(singing_img, (60, 60))
        screen.blit(downsized_singing_img, (810, 420))

    else:

        # Muting the volume
        music_channel.set_volume(0.0)

        muted_img = pygame.image.load("simpson_bored.png").convert_alpha()
        downsized_muted_img = pygame.transform.smoothscale(muted_img, (60, 60))
        screen.blit(downsized_muted_img, (810, 420))


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
        for filename in file:

            # Creating a valid filepath (e.g. "Announcer Audio/Good/Bang.mp3")
            filepath = os.path.join("Announcer Audio", file, filename)

            if file == "Good":
                good_calls.append(filepath)

            elif file == "Bad":
                bad_calls.append(filepath)

<<<<<<< HEAD

        return good_calls, bad_calls

# Testing Github
=======
        return good_calls, bad_calls

>>>>>>> cc4b40679fa9c62cdbcddcaee7fe23a3e06a4c86

def play_announcer_sound(is_correct: bool) -> None:
    """Plays NBA announcer calls, based on whether the user was correct/wrong."""

    music_channel.set_volume(0.2)

    if is_correct:
        sound = pygame.mixer.Sound("Bang.mp3")

    # Creating a 2nd channel to control the announcer's audio
    announcer_channel = pygame.mixer.Channel(1)
    announcer_channel.play(sound)

    # Check every 10 ms if the announcer_channel is still being played
    while announcer_channel.get_busy():
        pygame.time.delay(10)

    # Resetting the music_channel's volume to its original state
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
    simpsons_unmuted_img = pygame.image.load("simpson_vibing.png").convert_alpha()
    downsized_simpson_1 = pygame.transform.smoothscale(simpsons_unmuted_img, (60, 60))
    screen.blit(downsized_simpson_1, (225, 175))

    # Image of "music off" icon
    simpsons_muted_img = pygame.image.load("simpson_bored.png").convert_alpha()
    downsized_simpson_2 = pygame.transform.smoothscale(simpsons_muted_img, (60, 60))
    screen.blit(downsized_simpson_2, (340, 175))

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

# Loading images
clutch_images = load_clutch_images()
choke_images = load_choke_images()

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

                if 400 <= click_x <= 800 and button_y <= click_y <= button_y + 65:
                    user_answer = choices[i]    # Storing the user's response

                    is_correct = check_correct_ans(player.full_name, user_answer, clutch_images, choke_images)

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
# - Fix fetch_player() method to ensure that the music is muted when the user clicks on singing icon, and vice versa
# - Create a CLUE button:
#         - Either the player's NICKNAME (if it exists) or the year they RETIRED


