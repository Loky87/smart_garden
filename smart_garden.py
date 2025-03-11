import sys
import requests
import random
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer

API_KEY = "4feb07238d7b41a183f175355250703"
CITY = "Zagreb"

class SmartGarden(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_file = QFile("smart_garden.ui")
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui)

        self.ui.zalijevanje.clicked.connect(self.rucno_zalij)

        self.timer = QTimer()
        self.timer.timeout.connect(self.apdejt)
        self.timer.start(100000)

        self.sprica_li = False
        self.apdejt()

    def prognoza(self):
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={CITY}&days=1&aqi=no&alerts=no"
        riker = requests.get(url)
        picard = riker.json()

        if "current" in picard and "forecast" in picard:
            stepeni = picard["current"]["temp_c"]
            vlaga = picard["current"]["humidity"]
            nives = picard["forecast"]["forecastday"][0]["hour"]
            seansa = max(hour.get("chance_of_rain", 0) for hour in nives)
            pada_li = any(hour["will_it_rain"] == 1 or hour["chance_of_rain"] > 50 for hour in nives)
            return stepeni, vlaga, pada_li, seansa
       

    def vlaznost_tla(self):
        return random.randint(10, 100)

    def apdejt(self):
        stepeni, vlaga, pada_li, seansa = self.prognoza()
        tlo = self.vlaznost_tla()

        if stepeni is not None:
            self.ui.temperatura.setText(f"Temperatura: {stepeni} °C")
            self.ui.vlaznost_zraka.setText(f"Vlažnost zraka: {vlaga} %")

        self.ui.vlaznost_tla.setText(f"Vlažnost tla: {tlo} %")
        self.ui.kisa.setText(f"Vjerojatnost kiše: {seansa}%" if seansa is not None else "Vjerojatnost kiše: --%")

        if tlo < 30 and not pada_li:
            self.zalijevaj()
        else:
            self.nemoj_zalijevati()

    def zalijevaj(self):
        if not self.sprica_li:
            self.sprica_li = True
            self.ui.status.setText("Status zalijevanja: Uključeno")

    def nemoj_zalijevati(self):
        if self.sprica_li:
            self.sprica_li = False
            self.ui.status.setText("Status zalijevanja: Isključeno")

    def rucno_zalij(self):
        self.zalijevaj() if not self.sprica_li else self.nemoj_zalijevati()

def main():
    app = QApplication()
    window = SmartGarden()
    window.ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
