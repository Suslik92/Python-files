#from picamera import PiCamera
from time import sleep
from transitions import Machine
import random

class Matter(object):
    def say_hello(self): print("hello, new state!")
    def say_goodbye(self): print("goodbye, old state!")
    def on_enter_Start(self): print("We've just entered state A!")

lump = Matter()

# Same states as above, but now we give StateA an exit callback
states = ['Start', 'Initial', 'Measurement', 'Verification', 'Passed', 'Failed', 'Awaiting_Reply']

transitions = [
    { 'trigger': 'TrigToStart', 'source': 'Initial', 'dest': 'Start' },
    { 'trigger': 'System_Ready', 'source': 'Initial', 'dest': 'Measurement' },
    { 'trigger': 'Measurement_Complete', 'source': 'Measurement', 'dest': 'Verification' },
    { 'trigger': 'Verification_Successful', 'source': 'Verification', 'dest': 'Passed' },
    { 'trigger': 'Verification_Failed', 'source': 'Verification', 'dest': 'Failed' }
    { 'trigger': 'SMS_Sent', 'source': 'Failed', 'dest': 'Awaiting_Reply' }
    #Success to restart
    #Failed to restart
]

machine = Machine(lump, states=states, transitions = transitions, initial='Initial')

# Callbacks can also be added after initialization using
# the dynamically added on_enter_ and on_exit_ methods.
# Note that the initial call to add the callback is made
# on the Machine and not on the model.
#machine.on_enter_gas('say_hello')

# Test out the callbacks...
#machine.set_state('solid')
#lump.sublimate()

lump.melt()
print (lump.state)
