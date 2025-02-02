import appdaemon.plugins.hass.hassapi as hass

#
# Hellow World App
#
# Args:
#

class Caller(hass.Hass):

  def initialize(self):
    MyApp = self.get_app("notifyer")
    MyApp.notify(message="Test", tag="spulmaschine",urgency=2)
    

