# Why Notiband
How do warn someone that is hearing impaired? For example, when cycling together you notice a danger of which you inform your fellow cyclist. The notiband project is an attempt to prototype a solution for this type of situations. 

# Approach
An off the shelf fitness tracker is used to give haptic signals. These signals are sent out when the warn button is pressed. The button and tracker commmunicate wirelessly over Bluetooth (BLE).

The M3 tracker is used as fitness tracker since it is readily available. Furthermore, it's hardware is well documented. Projects like [GadgetBridge](https://codeberg.org/Freeyourgadget/Gadgetbridge) took the effort of documenting versions of this band. Other bands that have been documented by GadgetBridge could be used when needed. 
Unfortunately, the protocol in GadgetBridge wasn't completely accurate for my band. I also had to retrieve some specifics like the correct service. The sample service explorer from the Bleak library worked perfectly for this purpose (see examples/service_explorer.py in the [bleak-repository](https://github.com/hbldh/bleak.git)). With the retrieved address and service numbers, I could experiment with sending different messages. For the exploration phase, I created a simple program to send a raw data packet. It allowed me to verify the effect on the band. To document the actual protocol, I wrote a program to test the relevant features (setting the time faking calls and messages). The repository contains both.

The button is an [MDBT42Q-board](https://www.espruino.com/MDBT42Q), a nRF52832-SOC loaded with a javascript interpreter. Two of the input pins have been connected to push buttons. The board is powered by a 3V coin battery. The complete package is placed in an electric garage door key. A custom printed one may be easier to fit. 
The program that adds the functionality to the buttons is also added to the repository.
