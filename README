# Central heating
This codebase is for controlling a centralized heating system.

The central design point is that all modules communicate over MQTT, 
so the sensors send data to the mqtt broker and the controller and logger 
will subscribe to the data they need.

The design idea is to use 1-wire temperature sensors to measure some water temperatures, 
mainly main supply temperature, return water temperature and water tank, 
 also NTC thermistors to measure each under floor water section supply and return.

Each room will have a zigbee temperature and humidity sensor so those will be read using zigbee2mqtt.

The temperature from the room sensors will be used to turn on and off the flow of water to the rooms 
and regulating the temperature.
A simple regulator module will be made that subscribe to temperatures and send on/off message to the 
configured actuator also through mqtt.

Since all modules will be communicating through the MQTT system upgrading, fixing and changing each module 
should be quite easy, making this a modular system that can scale quite easy.

A module for calculating the power delivered to each loop will be made, this depends on the flow of 
water and temperature in and out. Since there will be no flow sensor (at least first) this module 
will rely on a configured flow read from the manual flow meters, temperature from temp sensors and 
if the actuator is on or of (water flows or not).

