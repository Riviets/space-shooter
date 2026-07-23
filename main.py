from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.image import Image
from random import randint
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.core.window import Keyboard

Window.size = 300, 600

class MainScreen(MDScreen):
    ...

class GameOverScreen(MDScreen):
    ...

FPS = 60

BULLET_SPEED = dp(10)
SHIP_SPEED = dp(2)

DIR_UP = 1
DIR_DOWN = -1

SPAWN_ENEMY_TIME = 2


class Shot(MDWidget):
    def __init__(self, direction, owner, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        self.owner = owner


class Ship(Image):
    def __init__(self, direction = DIR_UP, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction

    def moveLeft(self):
        self.pos[0] -= SHIP_SPEED

    def moveRight(self):
        self.pos[0] += SHIP_SPEED

    def shot(self):
        shot = Shot(self.direction, owner=self)
        shot.center_x = self.center_x
        shot.y = self.top if self.direction == DIR_UP else self.y - shot.height
        self.parent.parent.parent.parent.cartridge.append(shot)
        self.parent.add_widget(shot)

    def update(self):          
        pass


class PlayerShip(Ship):
    def __init__(self, **kwargs):
        super().__init__(direction=DIR_UP, **kwargs)

    def update(self, keys):
        for key in keys:
            if keys[key] == True:
                if key == 'left' and self.x > 0:
                    self.moveLeft()
                if key == 'right' and self.right < Window.width:
                    self.moveRight()
                if key == 'shot':
                    self.shot()
                    keys[key] = False


class EnemyShip(Ship):
    def __init__(self, *args, **kwargs):
        super().__init__(direction=DIR_DOWN, **kwargs)
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
        self.cartridge = []

        self.ship = None
        self.enemyShips = []

        self.pauseMenu = None

        self.spawn_delay = SPAWN_ENEMY_TIME
        self.time_last_spawn = 0

        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)

    def on_enter(self, *args):
        self.updateEvent = Clock.schedule_interval(self.update, 1 / FPS)

        self.ship = self.ids.ship

        return super().on_enter(*args)

    def spawn_enemy(self):
        ship = EnemyShip()
        ship.pos = (randint(0, int(Window.size[0] - ship.size[0])), Window.size[1])
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

            if ship.collide_widget(self.ship):
                self.game_over()

        self.manage_cartridge()

    def manage_cartridge(self):
        for bullet in self.cartridge[:]:
            bullet.y += BULLET_SPEED * bullet.direction

            self.check_collisions(bullet)

            if bullet.y > Window.height or bullet.top < 0:
                self.remove_shot(bullet)

    def check_collisions(self, bullet):
        if bullet.owner == self.ship:
            for enemy in self.enemyShips[:]:
                if bullet.collide_widget(enemy):
                    self.enemyShips.remove(enemy)
                    self.ids.front.remove_widget(enemy)

                    self.remove_shot(bullet)
                    break
        else:
            if bullet.collide_widget(self.ship):
                self.game_over()
                self.remove_shot(bullet)

    def remove_shot(self, bullet):
        if bullet in self.cartridge:
            self.cartridge.remove(bullet)
            self.ids.front.remove_widget(bullet)

    def game_over(self):
        self.updateEvent.cancel()

        for enemy in self.enemyShips[:]:
            self.enemyShips.remove(enemy)
            self.ids.front.remove_widget(enemy)

        for bullet in self.cartridge[:]:
            self.ids.front.remove_widget(bullet)
            self.cartridge.remove(bullet)

        self.manager.current = 'game_over'

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
                        on_press=self.pauseStop
                    )
                ],
            )
        self.pauseMenu.open()

    def pauseStop(self, *args):
        self.pauseMenu.dismiss()

    def resumeGame(self, *args):
        self.updateEvent = Clock.schedule_interval(self.update, 1 / FPS)

    def _on_key_down(self, window, keycode, *args, **kwargs):
        key = key if (key := Keyboard.keycode_to_string(window, keycode)) != 'spacebar' else 'shot'
        
        self.eventkeys[key] = True

    def _on_key_up(self, window, keycode, *args, **kwargs):
        key = key if (key := Keyboard.keycode_to_string(window, keycode)) != 'spacebar' else 'shot'

        self.eventkeys[key] = False


class ShooterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"

        self.sm = MDScreenManager()

        self.sm.add_widget(GameScreen(name='game'))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(GameOverScreen(name='game_over'))

        return self.sm
    

app = ShooterApp()
app.run()
