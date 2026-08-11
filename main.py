from random import randint

from kivy.clock import Clock
from kivy.core.window import Keyboard, Window
from kivy.metrics import dp
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.widget import MDWidget

Window.size = 300, 600


class MainScreen(MDScreen): ...


class GameOverScreen(MDScreen): ...


FPS = 60

BULLET_SPEED = dp(10)
SHIP_SPEED = dp(2)

DIR_UP = 1
DIR_DOWN = -1

SPAWN_ENEMY_TIME = 2


class Shot(MDWidget):
    def __init__(self, direction, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction


class Ship(Image):
    def __init__(self, direction=DIR_UP, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        self.size_hint = (None, None)
        self.size = (dp(50), dp(50))

    def moveLeft(self):
        self.pos[0] -= SHIP_SPEED

    def moveRight(self):
        self.pos[0] += SHIP_SPEED

    def shot(self):
        shot = Shot(self.direction)
        shot.center_x = self.center_x
        shot.y = self.top if self.direction == DIR_UP else self.y - shot.height
        self.parent.parent.parent.parent.cartridge.append(shot)
        self.parent.add_widget(shot)

    def update(self):
        pass


class PlayerShip(Ship):
    def __init__(self, **kwargs):
        super().__init__(direction=DIR_UP, **kwargs)
        self.source = "spaceship.png"

    def update(self, keys):
        for key in keys:
            if keys[key] == True:
                if key == "left" and self.center_x > 0:
                    self.moveLeft()
                if key == "right" and self.center_x < Window.width:
                    self.moveRight()
                if key == "shot":
                    self.shot()
                    keys[key] = False


class EnemyShip(Ship):
    def __init__(self, *args, **kwargs):
        super().__init__(direction=DIR_DOWN, **kwargs)
        self.source = "ufo.png"
        self.frame = 0

    def update(self):
        super().update()
        self.pos[1] -= dp(3)
        if self.frame % 100 == 0:
            self.shot()
        self.frame += 1


class GameScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.eventkeys = {}
        self.ship = self.ids.ship
        self.enemyShips = []

        self.cartridge = []

        self.pauseMenu = None
        self.spawn_delay = SPAWN_ENEMY_TIME
        self.time_last_spawn = 0

        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)

    def on_enter(self, *args):
        self.updateEvent = Clock.schedule_interval(self.update, 1 / FPS)

        self.ship = self.ids.ship

        return super().on_enter(*args)

    def spawn_enemy(self, *args):
        ship = EnemyShip()
        max_x = max(0, int(Window.width - ship.width))
        ship.x = randint(0, max_x)
        ship.y = Window.height
        self.enemyShips.append(ship)
        self.ids.front.add_widget(ship)

    def update(self, dt):
        self.ship.update(self.eventkeys)

        self.time_last_spawn += dt
        if self.time_last_spawn >= self.spawn_delay:
            self.spawn_enemy()
            self.time_last_spawn = 0

        for ship in self.enemyShips[:]:
            ship.update()
            if ship.top < 0:
                self.enemyShips.remove(ship)
                self.ids.front.remove_widget(ship)
                continue

            if ship.collide_widget(self.ship):
                self.game_over()
                return

        self.manage_cartridge()

    def game_over(self):
        self.updateEvent.cancel()

        for enemy in self.enemyShips[:]:
            self.enemyShips.remove(enemy)
            self.ids.front.remove_widget(enemy)

        for bullet in self.cartridge[:]:
            self.ids.front.remove_widget(bullet)
            self.cartridge.remove(bullet)

        self.manager.current = "game_over"

    def manage_cartridge(self):
        for bullet in self.cartridge[:]:
            bullet.y += BULLET_SPEED * bullet.direction

            if bullet.y > Window.height or bullet.top < 0:
                self.ids.front.remove_widget(bullet)
                self.cartridge.remove(bullet)
                continue

            if bullet.direction == DIR_UP:
                hit_enemy = None
                for ship in self.enemyShips:
                    if bullet.collide_widget(ship):
                        hit_enemy = ship
                        break

                if hit_enemy:
                    self.enemyShips.remove(hit_enemy)
                    self.ids.front.remove_widget(hit_enemy)
                    self.ids.front.remove_widget(bullet)
                    self.cartridge.remove(bullet)
                    continue

            if bullet.direction == DIR_DOWN:
                if bullet.collide_widget(self.ship):
                    self.ids.front.remove_widget(bullet)
                    self.cartridge.remove(bullet)
                    self.game_over()
                    return

    def pressKey(self, key):
        self.eventkeys[key] = True

    def releaseKey(self, key):
        self.eventkeys[key] = False

    def show_menu(self):
        self.updateEvent.cancel()

        if not self.pauseMenu:
            self.pauseMenu = MDDialog(
                title="Game Paused",
                text="Resume the game?",
                on_dismiss=self.resumeGame,
                buttons=[
                    MDFlatButton(
                        text="RESUME",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,
                        on_press=self.pauseStop,
                    ),
                ],
            )
        self.pauseMenu.open()

    def pauseStop(self, *args):
        self.pauseMenu.dismiss()

    def resumeGame(self, *args):
        self.updateEvent = Clock.schedule_interval(self.update, 1 / FPS)

    def _on_key_down(self, window, keycode, *args, **kwargs):
        key = (
            key
            if (key := Keyboard.keycode_to_string(window, keycode)) != "spacebar"
            else "shot"
        )

        self.eventkeys[key] = True

    def _on_key_up(self, window, keycode, *args, **kwargs):
        key = (
            key
            if (key := Keyboard.keycode_to_string(window, keycode)) != "spacebar"
            else "shot"
        )

        self.eventkeys[key] = False


class ShooterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"

        self.sm = MDScreenManager()

        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(GameScreen(name="game"))
        self.sm.add_widget(GameOverScreen(name="game_over"))

        return self.sm


app = ShooterApp()
app.run()
