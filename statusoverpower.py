import appdaemon.plugins.hass.hassapi as hass

class StatusOverPower(hass.Hass):

  def initialize(self):
    self.status_input_boolean_name=self.args["status_input_boolean"] #for logging output
    self.estimated_device_state = "off" #used for tracking the status in the app
    self.power_entity_name = self.args["power_entity"]
    self.power_entity=self.get_entity(self.power_entity_name)
    self.switch_entity_name = self.args["switch_entity"]    
    self.switch_entity = self.get_entity(self.switch_entity_name)
    self.start_power = self.args["start_power"]
    self.stop_power = self.args["stop_power"]
    self.start_timer = self.args["start_timer"]
    self.stop_timer = self.args["stop_timer"]
    self.active = self.args["active"]
    self.tag=self.args["notify_tag"]
    self.start_timer_handle = None
    self.stop_timer_handle = None
    self.my_notifyer=self.get_app("notifyer")
    #do know about restarts off app
    self.log(f"App {self.name} initialized")
    
    #set listeners and create entity if active: 
    if self.active:
      self.set_state(self.status_input_boolean_name,state="off") #create status entity within HA
      self.listen_state(self.power_changed, self.power_entity_name, attribute = "state")
      self.listen_state(self.switch_changed, self.switch_entity_name, attribute ="state")
    #call callback once to be sure constant high power is not overseen
      self.power_changed()

  def switch_changed(self, *args, **kwargs):
  #check whether the devive is currently active
    if self.estimated_device_state == "on":
      #for active device we need to verify the real state of switch    
      if self.switch_entity.state == "off":
        self.switch_entity.turn_on() 
        self.log(f"Smartplug {self.switch_entity_name} turned off while device {self.status_input_boolean_name} was concidered active, turned on again!")
        self.my_notifyer.notify(message=f"Das Gerät {self.name} hatte Ausetzer beim Smartplug", tag=self.tag ,urgency=1) 

  
  def power_changed(self, *args, **kwargs):
    #check whether app should mark device as active
    try:
      self.current_power = float(self.power_entity.state)
    except:
      self.current_power=0.0

    if self.estimated_device_state == "on":
      #Device is already marked as running
      if self.current_power < self.stop_power:
        #if no stop_timer is available, create one
        if not self.timer_running(self.stop_timer_handle):
          self.stop_timer_handle= self.run_in(self.callback_stop_timer, self.stop_timer)
      else:
        #value to high to stop device 
        if self.timer_running(self.stop_timer_handle):
          self.cancel_timer(self.stop_timer_handle)        
      
    if self.estimated_device_state == "off":
      #Device is already marked as NOT running
      if self.current_power >= self.start_power:
        #if no start_timer is running create one...
        if not self.timer_running(self.start_timer_handle):
          self.start_timer_handle = self.run_in(self.callback_start_timer, self.start_timer)
      else:
        #value to small we need to abort the start sequence for device and cancel timmer if existing
        if self.timer_running(self.start_timer_handle):
          self.cancel_timer(self.start_timer_handle)



  def callback_start_timer(self, **kwargs):
    self.log("start detected")
    self.my_notifyer.notify(message=f"Das Gerät {self.name} läuft", tag=self.tag ,urgency=1)
    self.estimated_device_state = "on" #realtime...
    self.set_state(self.status_input_boolean_name, state="on") #takes ages 
  
  def callback_stop_timer(self, **kwargs):
    self.log("stop detected")
    self.my_notifyer.notify(message=f"Das Gerät {self.name} ist nicht mehr aktiv", tag=self.tag ,urgency=3)
    self.estimated_device_state = "off" #fast
    self.set_state(self.status_input_boolean_name, state="off") #slow 
    
    
