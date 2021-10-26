import pygame
from pygame.locals import *
import operator


def main():
    # initialize all pygame modules (some need initialization)
    pygame.init()
    pygame.font.init()  # you have to call this at the start,
    # if you want to use this module.
    pygame.display.set_mode((500, 400))
    pygame.display.set_caption("Pong")
    w_surface = pygame.display.get_surface()
    game = Game(w_surface)
    game.play()
    pygame.quit()


class Game:
    # An object in this class represents a complete game.

    def __init__(self, surface):
        self.surface = surface
        self.bg_color = pygame.Color("black")
        self.fg_color = pygame.Color("white")

        self.FPS = 60

        self.game_Clock = pygame.time.Clock()
        self.close_clicked = False
        self.continue_game = True
        self.scores = [0, 0]
        self.max_score = 11
        self.paddles_velocity = 10
        paddles_width = 10
        paddles_height = 50
        paddles_top = 180
        p_x_offset = 100

        self.small_ball = Ball(self.fg_color, 4, [50, 50], [4, 1], self.surface)
        self.paddle_1 = Paddle(
            paddle_color="yellow",
            surface=self.surface,
            paddle_width=paddles_width,
            paddle_height=paddles_height,
            paddle_top=paddles_top,
            paddle_left=self.surface.get_width() - p_x_offset - paddles_width,
            velocity=0,
        )
        self.paddle_2 = Paddle(
            paddle_color="red",
            surface=self.surface,
            paddle_width=paddles_width,
            paddle_height=paddles_height,
            paddle_top=paddles_top,
            paddle_left=p_x_offset,
            velocity=0,
        )
        self.max_frames = 150
        self.frame_counter = 0

    def play(self):

        while not self.close_clicked:
            self.handle_events()
            # self.paddle_2.move()
            # self.paddle_1.move()
            self.draw()
            if self.continue_game:
                self.update()
                self.decide_continue()
            self.game_Clock.tick(self.FPS)  # run at most with FPS Frames Per Second

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.close_clicked = True
            if event.type == pygame.KEYDOWN:
                self.handle_key_down(event.key)
            if event.type == pygame.KEYUP:
                self.handle_key_up(event.key)

    def handle_key_down(self, key):
        if key == K_UP:
            self.paddle_1.start(self.paddles_velocity)
        if key == K_q:
            self.paddle_2.start(self.paddles_velocity)
        if key == K_DOWN:
            self.paddle_1.start(-1 * self.paddles_velocity)
        if key == K_a:
            self.paddle_2.start(-1 * self.paddles_velocity)

    def handle_key_up(self, key):
        if key == K_q and self.paddle_2.moving_up():
            self.paddle_2.stop()
        if key == K_a and self.paddle_2.moving_down():
            self.paddle_2.stop()

        if key == K_UP and self.paddle_1.moving_up():
            self.paddle_1.stop()
        if key == K_DOWN and self.paddle_1.moving_down():
            self.paddle_1.stop()

    def draw(self):

        self.surface.fill(self.bg_color)  # clear the display surface first
        self.draw_score()
        self.small_ball.draw()
        self.paddle_1.draw()
        self.paddle_2.draw()

        pygame.display.update()  # make the updated surface appear on the display

    def draw_score(self):
        text_font = pygame.font.SysFont("", 50)
        for index in range(2):
            text_string = str(self.scores[index])
            text_image = text_font.render(
                text_string, True, self.fg_color, self.bg_color
            )
            if index == 1:
                location = (0, 0)
            else:
                location = (self.surface.get_width() - text_image.get_width(), 0)
            self.surface.blit(text_image, location)

    def update(self):
        self.paddle_2.move()
        self.paddle_1.move()
        edge = self.small_ball.move(self.paddle_1, self.paddle_2)
        if edge == "left":
            self.scores[0] += 1
        elif edge == "right":
            self.scores[1] += 1
        self.frame_counter = self.frame_counter + 1

    def decide_continue(self):

        if self.max_score in self.scores:
            self.continue_game = False


class Ball:
    # An object in this class represents a ball that moves

    def __init__(self, ball_color, ball_radius, ball_center, ball_velocity, surface):

        self.color = ball_color
        self.radius = ball_radius
        self.center = ball_center
        self.velocity = ball_velocity
        self.surface = surface

    def move(self, paddle_1, paddle_2):
        new_coordinates = [0, 0]
        new_coordinates[0] = self.center[0] + self.velocity[0]
        new_coordinates[1] = self.center[1] + self.velocity[1]
        surface_height = self.surface.get_height()
        surface_width = self.surface.get_width()

        if paddle_1.in_paddle(self.center) and self.velocity[0] > 0:
            print("COLISION wITH PADDLE 1!!!")
            self.center = new_coordinates
            self.bounce("x")
            return ""
        elif paddle_2.in_paddle(self.center) and self.velocity[0] < 0:
            print("Collision with PADDLE 2!!!!!")
            self.center = new_coordinates
            self.bounce("x")
            return ""
        if (
            new_coordinates[1] < self.radius
            or new_coordinates[1] + self.radius >= surface_height
        ):
            # collision with bottom or top
            self.center[0] = new_coordinates[0]
            self.center[1] = sorted([0, new_coordinates[1], surface_height])[1]
            self.bounce("y")
            return ""
        if new_coordinates[0] <= self.radius:
            self.center[1] = new_coordinates[1]
            self.center[0] = sorted([0, new_coordinates[0], surface_width])[1]
            self.bounce("x")
            return "left"
        if new_coordinates[0] + self.radius >= surface_width:
            self.center[1] = new_coordinates[1]
            self.center[0] = sorted([0, new_coordinates[0], surface_width])[1]
            self.bounce("x")
            return "right"

        self.center = new_coordinates

        return ""

    def bounce(self, axis):
        if axis == "x":
            self.velocity[0] *= -1
        else:
            self.velocity[1] *= -1

    def draw(self):
        pygame.draw.circle(self.surface, self.color, self.center, self.radius)


class Paddle:
    def __init__(
        self,
        paddle_color,
        paddle_left,
        paddle_top,
        paddle_width,
        paddle_height,
        surface,
        velocity,
    ):
        self.color = pygame.Color(paddle_color)
        self.surface = surface
        self.velocity = velocity
        self.width = paddle_width
        self.height = paddle_height
        self.rect = pygame.Rect(paddle_left, paddle_top, self.width, self.height)

    def draw(self):
        pygame.draw.rect(self.surface, self.color, self.rect)

    def move(self):
        if self.velocity > 0:
            self.rect.top = max(self.rect.top - self.velocity, 0)
        elif self.velocity < 0:
            self.rect.top = min(
                self.rect.top - self.velocity, self.surface.get_height() - self.height
            )

    def stop(self):
        self.velocity = 0

    def start(self, velocity):
        self.velocity = velocity

    def in_paddle(self, coordinates):
        if self.rect.collidepoint(coordinates[0], coordinates[1]):
            return True
        return False

    def moving_up(self):
        return self.velocity > 0

    def moving_down(self):
        return self.velocity < 0


main()
