from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

Window.size = (300, 600)

class MainScreen(MDScreen):
    ...

class GameScreen(MDScreen):
    ...

class ShooterApp(MDApp):
    def build(self):

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"

        sm = MDScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(GameScreen(name='game'))
        return sm

app = ShooterApp()
app.run()
