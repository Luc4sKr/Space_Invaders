import pygame
import sys
from random import choice, randint

import obstacle
from player import Player
from alien import Alien, Extra
from laser import Laser

class Game:
    def __init__(self):
        # Player
        player_sprite = Player((SCREEN_X / 2, SCREEN_Y), SCREEN_X, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        # Health
        self.lives = 3
        self.lives_surface = pygame.image.load("assets/images/player.png").convert_alpha()
        self.lives_x_start_pos = SCREEN_X - (self.lives_surface.get_size()[0] * 3  + 30)

        # Score
        self.score = 0
        self.font = pygame.font.Font("assets/8-bit_font.ttf", 20)

        # Obstacle
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks_group = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (SCREEN_X / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacle_x_positions, x_start=SCREEN_X/15, y_start=480) # Não sei pq 15 :)

        # Alien
        self.alien_group = pygame.sprite.Group()
        self.alien_setup(rows=6, cols=8, x_distance=60, y_distance=48, x_offet=70, y_offset=100)
        self.alien_direction = 1
        self.alien_lasers_group = pygame.sprite.Group()

        # Extra alien
        self.extra_alien = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400, 800)


    def create_obstacle(self, x_start, y_start, off_set_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == "1":
                    x = x_start + col_index * self.block_size + off_set_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size, (240, 80, 80), x, y)
                    self.blocks_group.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols, x_distance, y_distance, x_offet, y_offset):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offet
                y = row_index * y_distance + y_offset

                if row_index == 0:
                    alien_sprite = Alien("yellow", x, y)
                elif 1 <= row_index <= 2:
                    alien_sprite = Alien("green", x, y)
                else:
                    alien_sprite = Alien("red", x, y)

                self.alien_group.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.alien_group.sprites()
        for aliens in all_aliens:
            if aliens.rect.right >= SCREEN_X:
                self.alien_direction = -1
                self.alien_move_down(2)
            if aliens.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(2)

    def alien_move_down(self, distance):
        if self.alien_group:
            for alien in self.alien_group.sprites():
                alien.rect.y += distance

    def alien_shot(self):
        if self.alien_group.sprites():
            random_alien = choice(self.alien_group.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6)
            self.alien_lasers_group.add(laser_sprite)

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra_alien.add(Extra(choice(["right", "left"])))
            self.extra_spawn_time = randint(400, 800)

    def collision_checks(self):
        # Player lasers
        if self.player.sprite.laser_group:
            for laser in self.player.sprite.laser_group:
                # Obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks_group, True):
                    laser.kill()

                # Alien collisions
                alien_hit = pygame.sprite.spritecollide(laser, self.alien_group, True)
                if alien_hit:
                    for alien in alien_hit:
                        self.score += alien.value
                    laser.kill()

                # Extra alien collision
                if pygame.sprite.spritecollide(laser, self.extra_alien, True):
                    laser.kill()
                    self.score += 500

        # Alien lasers
        if self.alien_lasers_group:
            for laser in self.alien_lasers_group:
                # Obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks_group, True):
                    laser.kill()

                # Player collision
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()


        # Aliens
        if self.alien_group:
            for alien in self.alien_group:
                pygame.sprite.spritecollide(alien, self.blocks_group, True)

                if pygame.sprite.spritecollide(alien, self.player, False):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        for live in range(self.lives):
            x = self.lives_x_start_pos + (live * (self.lives_surface.get_size()[0] + 10))
            screen.blit(self.lives_surface, (x, 8))

    def display_score(self):
        score_surface = self.font.render(f"Score: {self.score}", False, "white")
        score_rect = score_surface.get_rect()
        score_rect.topleft = (10, 10)
        screen.blit(score_surface, score_rect)

    def run(self):
        # Atualiza todos os grupos de sprites
        self.player.update()
        self.alien_lasers_group.update()
        self.extra_alien.update()

        self.alien_group.update(self.alien_direction)
        self.alien_position_checker()
        self.extra_alien_timer()
        self.collision_checks()

        self.display_lives()
        self.display_score()

        # Desenha todos os grupos de sprites
        self.player.sprite.laser_group.draw(screen)
        self.player.draw(screen)

        self.blocks_group.draw(screen)
        self.alien_group.draw(screen)
        self.alien_lasers_group.draw(screen)
        self.extra_alien.draw(screen)


class CRT:
    def __init__(self):
        self.tv = pygame.image.load("assets/images/tv.png").convert_alpha()
        self.tv = pygame.transform.scale(self.tv, (SCREEN_X, SCREEN_Y))

    def draw(self):
        self.tv.set_alpha(randint(75, 90))
        self.create_crt_lines()

        screen.blit(self.tv, (0, 0))

    def create_crt_lines(self):
        line_height = 3
        line_amount = int(SCREEN_X / line_height)
        for line in range(line_amount):
            y_pos = line * line_height
            pygame.draw.line(self.tv, "black", (0, y_pos), (SCREEN_X, y_pos), 1)


if __name__ == '__main__':
    pygame.init()

    SCREEN_X = 600
    SCREEN_Y = 600

    screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()

    game = Game()
    crt = CRT()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == ALIENLASER:
                game.alien_shot()

        screen.fill((0, 0, 0))

        game.run()
        crt.draw()

        pygame.display.flip()
        clock.tick(60)