import logging
from functools import partial
from threading import Thread

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp as App
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from emu_config.core import *
from emu_config.variables import *

Builder.load_string("""
<LoadingScreen>:
    BoxLayout:
        Label:
            text: 'Loading'
        ProgressBar:
            id: progress
            max: 100

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'This is your application. Choose one of the options below:'
        BoxLayout:
            orientation: 'horizontal'
            MDRectangleFlatButton:
                text: 'Easy'
                on_release: root.on_easy_button()  # Calls the on_easy_button method of MainScreen when the button is released
            MDRectangleFlatButton:
                text: 'Custom'
                on_release: root.on_custom_button()  # Calls the on_custom_button method of MainScreen when the button is released
        MDRectangleFlatButton:
            text: 'Exit'
            on_release: app.stop()  # Exits the app when the button is released
""")


class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_loading()

    def start_loading(self):
        Clock.schedule_once(lambda dt: Thread(target=self.do_work).start(), 1)  # delay for 2 seconds

    def do_work(self):
        try:
            # instance some variables
            config = {}
            core = {}
            os_var = {}
            default = {}
            paths = {}
            programs = {}

            # load core variables and some one-offs so I only have to write the dicionary values once in case I rebase
            # initialize core dictionaries, variables, paths, and logging
            config, core, os_var, default = initialize_core()

            cache_path = core['cache']
            log_path = core['log']
            default_log_level = default['log_level']
            github_token = os.environ.get('GITHUB_TOKEN')

            initialize_core_paths(cache_path, log_path)
            initialize_log(log_path, default_log_level)
            Clock.schedule_once(self.update_progress_bar)

            # load paths and program variables and fetch current version numbers and download paths
            Logger.info("Main: Initializing variables - Fetching data from internet")
            # need to return any errors here to update the gui with info, such as, couldn't get an updated version and used cache
            # also need to handle if there is no cached version and couldn't get a version number, disable that particular app from update/install
            paths, programs = initialize_variables_get_versions(config, cache_path, github_token)
            Clock.schedule_once(self.update_progress_bar)

            Logger.info("Main: Initializing variables - Updating dicionary values")
            # maybe do a check for any remaining $[] in dictionaries, if exists, warning and exit
            paths, programs = initialize_variables_update_dictionaries(core, os_var, paths, programs)
            Clock.schedule_once(self.update_progress_bar)

            Logger.debug(f"Main: core - {json.dumps(core, indent=4)}")
            Logger.debug(f"Main: default settings dictionary - {json.dumps(default, indent=4)}")
            Logger.debug(f"Main: paths dictionary - {json.dumps(paths, indent=4)}")
            Logger.debug(f"Main: programs dictionary - {json.dumps(programs, indent=4)}")

            # After all tasks are done, switch to the main screen
            Clock.schedule_once(self.switch_to_main_screen)
        except Exception as exception:
            Logger.error(f"Main: Error occurred - {str(exception)}")
            Clock.schedule_once(partial(self.show_error_dialog, str(exception)))

    def update_progress_bar(self, *args):
        self.ids.progress.value += 100 / 3  # Adjust this value based on the number of tasks

    def switch_to_main_screen(self, *args):
        self.manager.current = 'main'

    def show_error_dialog(self, message, *args):
        dialog = MDDialog(
            text=message,
            size_hint=(0.8, 1),
            buttons=[
                MDFlatButton(
                    text="Exit",
                    on_release=self.exit_app
                )
            ]
        )
        dialog.open()

    @staticmethod
    def exit_app(*args):
        App.get_running_app().stop()


class MainScreen(Screen):
    def on_easy_button(self):
        Logger.info('MainScreen: Easy button pressed')

    def on_custom_button(self):
        Logger.info('MainScreen: Custom button pressed')


class EmuConfig(App):
    def build(self):
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', "logo.png")
        self.title = "Emu-Config"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Gray"
        self.icon = logo_path
        logging.debug(f"EmuConfig: {logo_path}")
        logging.debug(f"EmuConfig: Set icon to {self.icon}")
        logging.debug(f"EmuConfig: Current icon is {self.get_application_icon()}")
        from kivy.core.window import Window
        Window.minimum_width, Window.minimum_height = 640, 360
        sm = ScreenManager()
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == "__main__":
    EmuConfig().run()
