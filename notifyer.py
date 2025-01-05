import appdaemon.plugins.hass.hassapi as hass
import time

#
# Hellow World App
#
# Args:
#

class Notifyer(hass.Hass):
    def initialize(self):
        
        self.alexa_service_data = {
            "type": "announce",
            "method": "speak"}
        
        # empty array
        self.alexa_array =[]
        alexas = self.args["alexas"]
        #interate over all alexas 
        for current_alexa in alexas:
            #create an instance of Class Alexa
            alexa_inst = Alexa(current_alexa)
            #copy the registration dict into instance
            alexa_inst.set_registrations(alexas[current_alexa])
            self.alexa_array.append(alexa_inst)

        #empty array for mobiles
        self.mobile_array=[]
        mobiles = self.args["mobiles"]
        #iterate over all mobiles
        for current_mobile in mobiles:
            #creates mobile instance and set name
            mobile_instance = Mobile(current_mobile)
            mobile_instance.set_registrations(mobiles[current_mobile])
            self.mobile_array.append(mobile_instance)
        
        
    def get_notify_alexa_array(self, tag, prio):
        registered_alexas=[]
        for current_alexa in self.alexa_array:
            if current_alexa.is_registered(tag):
                if current_alexa.get_prio(tag) <= prio and current_alexa.get_prio(tag) != 0:
                    registered_alexas.append(current_alexa)
        return registered_alexas     

    def get_notify_mobile_array(self, tag, prio):
        registered_mobiles=[]
        for current_mobile in self.mobile_array:
            if current_mobile.is_registered(tag):
                if current_mobile.get_prio(tag) <= prio and current_mobile.get_prio(tag) !=0:
                    registered_mobiles.append(current_mobile)
        return registered_mobiles


    def call_out(self,message, alexa_array):
        work_array=[]
        for current_alexa in alexa_array:
            work_array.append(current_alexa.media_player)
        self.call_service("notify/alexa_media", message=message, target=work_array, data = self.alexa_service_data)
        
    def send_out_notification(self, message, mobile_array):
        for current_mobile in mobile_array:
            self.log(f"Sending notification to mobile_app_{current_mobile.name} with message: {message}" )
            self.call_service(f"notify/mobile_app_{current_mobile.name}",message=message)


    def notify(self, message="", tag="default", urgency=1):
        volume_changed=False
        alexa_array=self.get_notify_alexa_array(tag, urgency)
        mobile_array=self.get_notify_mobile_array(tag, urgency)
        if len(alexa_array) > 0:
            if urgency >= 3:
                self.set_volume(alexa_array, 0.5)
                volume_changed=True
            if urgency >= 4:
                self.turnoff_dnd(alexa_array) 
            self.call_out(message, alexa_array)
            #some logging
            name_csv="["
            for alexa in alexa_array:
                name_csv = name_csv+" "+alexa.name
            name_csv =name_csv +"]"
            self.log(f"Call out to {name_csv} on urgency: {urgency} with message: {message}" )  
            if volume_changed:
                self.restore_volume(alexa_array)
        else:
            self.log(f"No target alexa on urgency: {urgency} found for message: {message}")            

        if len(mobile_array) > 0:
            self.send_out_notification(message, mobile_array)
        else:
            self.log(f"No target mobile on urgency: {urgency} found for message: {message}")   
            
    def set_volume(self, alexa_array, volume):
        for current_alexa in alexa_array:
            current_alexa.previous_volume= self.get_state(current_alexa.media_player, attribute="volume_level")
            self.call_service("media_player/volume_set", entity_id = current_alexa.media_player, volume_level = volume)
    
    # needed because the delay with run_in has trouble with other than **kwargs
    def service_wrapper(self, **kwargs):
        service = kwargs.get("service")
        entity_id = kwargs.get("entity_id")
        volume_level=kwargs.get("volume_level")
        self.call_service(service, entity_id = entity_id, volume_level = volume_level)

    def restore_volume(self, alexa_array):
        for current_alexa in alexa_array:
            self.run_in(self.service_wrapper, 10, service="media_player/volume_set", entity_id = current_alexa.media_player, volume_level = current_alexa.previous_volume)


    def turnoff_dnd(self, alexa_array):
        for current_alexa in alexa_array:
            self.turn_off(current_alexa.dnd_switch)
    


class Alexa:
    def __init__(self, name):
        self.name = name
        self.media_player = "media_player."+name
        self.dnd_switch = "switch."+name+"_do_not_disturb_switch"
        self.registrations = {}
        self.previous_volume=0.3

    def set_registrations(self, registrations):
        self.registrations=registrations
    
    def add_registration(self, tag, prio):
        self.registrations[tag] = prio

    def is_registered(self, tag):
        if self.registrations.get(tag,0) > 0:
            return True
        else:
            return False 
    def get_prio(self, tag):
        return self.registrations.get(tag, 0) 

#could have been a child of alexa or generic class... not so important 
class Mobile:
    def __init__(self, name):
        self.name = name
        self.registrations ={}

    def set_registrations(self, registrations):
        self.registrations=registrations

    def add_registration(self, tag, prio):
        self.registrations[tag] = prio        
    
    def is_registered(self, tag):
        if self.registrations.get(tag,0) > 0:
            return True
        else:
            return False 
    def get_prio(self, tag):
        return self.registrations.get(tag, 0) 






