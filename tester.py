import appdaemon.plugins.hass.hassapi as hass

class Tester(hass.Hass):
  def initialize(self):
    try:
      self.input2 = self.args["input2"]
    except:
      self.input2 = "leer eztjjjf xfddddj"    
    self.call_service("notify/mobile_app_handy_marc",message="test aus appdaemon")
  




