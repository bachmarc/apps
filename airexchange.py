import appdaemon.plugins.hass.hassapi as hass
import time
import datetime

#
# 
#
# Args:
#

class AirExchange(hass.Hass):
    def initialize(self):
        self.active = self.args["active"]
        self.fan_switch = self.get_entity(self.args["fan_switch"])
        self.humidity_sensor= self.get_entity(self.args["humidity_sensor"])
        self.active_from = self.args["active_from"]
        self.active_to = self.args["active_to"]
        self.start_humidity = self.args["start_humidity"]
        self.stop_humidity = self.args["stop_humidity"]
        self.my_notifyer=self.get_app("notifyer")
        #do know about restarts off app
        self.log(f"App {self.name} initialized")
        #register listener
        if self.active == True:
            #get intention boolean available
            self.set_state(self.args["status_input_boolean"], state="on")
            self.input_boolean_switch = self.get_entity(self.args["status_input_boolean"])
            #initially start airex
            self.air_control()
            self.handle_fan = self.fan_switch.listen_state(self.air_control, attribute = "state") 
            self.handle_sensor= self.humidity_sensor.listen_state(self.air_control, attribute = "state")
            #trigger start and stop time based if no listener is triggered
            self.run_daily(self.air_control, self.active_from)
            #add one second to get it stopped with method time_str_offset
            self.run_daily(self.air_control, self.time_str_offset(self.active_to))

    

    def air_control(self, *args, **kwargs):
        if self.now_is_between(self.active_from, self.active_to) or float(self.humidity_sensor.state) >= self.start_humidity:
            self.input_boolean_switch.set_state(state="on")
            
            
        if not self.now_is_between(self.active_from, self.active_to) and float(self.humidity_sensor.state) <= self.stop_humidity:
            self.input_boolean_switch.set_state(state="off") 
            
        if self.input_boolean_switch.state == "on" and self.fan_switch.state == "off":
            self.fan_switch.turn_on()
            self.log(f"AirExchange started fan {self.fan_switch.name} at rel. humidity of {self.humidity_sensor.state} %. Start threshold: {self.start_humidity} %")
        
        if self.input_boolean_switch.state == "off" and self.fan_switch.state == "on":
            self.fan_switch.turn_off()
            self.log(f"AirExchange stopped fan {self.fan_switch.name} at rel. humidity of {self.humidity_sensor.state} %. Stop threshold: {self.stop_humidity} %")  


    def time_str_offset(self, time_str):
        #function to add 1 second to a time string... 
        if int(time_str[6:8]) <= 58:
            if int(time_str[6:8]) < 10:
                time_str = time_str[0:5] + ":0" +str(int(time_str[6:8])+1)
            else:
                time_str = time_str[0:5] + ":" +str(int(time_str[6:8])+1)
        else:
            time_str = time_str[0:5] + ":00"
            if int(time_str[3:5]) <= 58:
                time_str = time_str[0:2] +":"+ str(int(time_str[3:5])+1) + ":00"
            else:
                time_str = time_str[0:2]+":00:00"
                if int(time_str[0:2]) <= 22:
                    time_str = str(int(time_str[0:2])+1)+":00:00"
                else: 
                    time_str = "00:00:00"
        return time_str

    
