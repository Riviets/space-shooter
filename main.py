from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.widget import MDWidget

FPS = 60
BULLET_SPEED = dp(10)
SHIP_SPEED = dp(1)

class Shot(MDWidget):
    ...

class MainScreen(MDScreen):
    ...

class GameScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1/FPS)

        self.eventkeys = {}
        self.cartridge = []

    def update(self, dt):
        for key in self.eventkeys:
            if self.eventkeys[key] == True:
                if key == 'left':
                    self.moveLeft()
                if key == 'right':
                    self.moveRight()
                if key == 'shot':
                    self.shot()
                    self.eventkeys[key] = False

        for bullet in self.cartridge:
            bullet.pos[1] += BULLET_SPEED

    def presskey(self, key):
        self.eventkeys[key] = True

    def releasekey(self, key):
        self.eventkeys[key] = False

    def moveLeft(self):
        self.ids.ship.pos[0] -= SHIP_SPEED

    def moveRight(self):
        self.ids.ship.pos[0] += SHIP_SPEED

    def shot(self):
        shot = Shot(pos = (self.ids.ship.center_x - 10, self.ids.ship.top))
        self.cartridge.append(shot)
        self.ids.front.add_widget(shot)

class ShooterApp(MDApp):
    def build(self):
        sm = MDScreenManager()
        sm.add_widget(GameScreen(name = 'game'))
        sm.add_widget(MainScreen(name = 'main'))

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        return sm
    
Window.size = (300, 600)

app = ShooterApp()
app.run()