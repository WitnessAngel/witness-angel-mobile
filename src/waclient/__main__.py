
import os
from waclient.waclient_app import WitnessAngelClientApp

os.environ["KIVY_NO_ARGS"] = "1"


def main():
    WitnessAngelClientApp().run()


if __name__ == "__main__":
    main()
