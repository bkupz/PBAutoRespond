# Brandon Kupczyk (10/31/16)

from pushbullet import Pushbullet


class PBAutoRespond:
    """
    Thiis class is used to send actual messages to others using a prebuilt Pushbullet API
    https://pypi.python.org/pypi/pushbullet.py.
    """
    VCard_file = None
    pb = None
    devices = None
    device = None
    contacts = None
    my_contact = None
    unresponded_messages=None
    IO=None
    auto_respond_message='This person is away, this is an auto responce. The more you text the more messages you will get. Much love'

    def __init__(self, api_key, device_name, my_contact, contacts_VCard_file): #on init it uses calls to the PushBullet api to get the device you send texts with
        """
        This sets up contacts, the Python Pushbullet API, the device to use and the contact information.
        :param api_key: API key passed in from the configs as a string.
        :param device_name: Device name found in the configs as a string.
        :param my_contact: This is also found in the configs
        :param contacts_VCard_file:
        """
        self.VCard_file = contacts_VCard_file
        self.pb = Pushbullet(api_key)
        self.devices = self.pb.devices
        self.my_contact = my_contact
        
        count = 0
        for dev in self.devices:
            if dev.nickname == device_name:
                self.device = self.pb.devices[count]
                print(dev.nickname)
            count += 1
        if self.device == None:                         #if the device was not set then it would still be None
            raise AssertionError('The device that was passed on init was not in your device list')

        name = ''
        number = ''
        self.contacts = {}
        with open(self.VCard_file) as openfileobject:   # also on init contacts get generated from a vcf file
            for line in openfileobject:
                if line[:3] == 'FN:':
                    name = line[3:-1]
                if line[:14] == 'TEL;TYPE=CELL:':
                    number = line[14:-1]
                if line == 'END:VCARD\n':
                    if len(name) + len(number) >= 10 and len(number) >= 9:
                        self.contacts[name] = number

    def send(self, person, text):
        """
        This method makes it possible to send a general purpose message.
        :param person: This is a string of the person you are trying to send the message to from the contacts.
        :param text: This is a string of the message you are trying to return.
        """
        try:
            number = self.contacts[person]
            self.pb.push_sms(self.device, number, text)
            print('trying to send away message to ' + person)
        except Exception as e:
            number = self.contacts[self.my_contact]
            text = 'Could not send text to ' + person
            self.pb.push_sms(self.device, number, text)
            print('Could not send text to ' + person+ str(e))

    def sendAwayMes(self, person):                #sends an away message
        """
        This method sends the away message text; either default or user specified.
        :param person: This is a string of the person you are trying to send the message to from the contacts.
        :return: If it is set to off the program just returns.
        """
        if self.IO:
            return
        try:
            number = self.contacts[person]
            self.pb.push_sms(self.device, number, self.auto_respond_message)
            print('trying to send away message to ' + person)
        except Exception as e:
            number = self.contacts[self.my_contact]
            text = 'Could not send response to ' + person + '. Update Contacts \n'
            self.pb.push_sms(self.device, number, text)
            print(str(e))

    def set_away_message(self, message):                #called when I text setmessage: switch found in main
        """
        This method is called to set a custom message.
        :param message: This is the custom message you wish to set as a string.
        """
        self.auto_respond_message = message
        self.send(self.my_contact, 'Away message set to ' + message)

    def set_ONOFF(self, value):
        """
        This method is used to set the Auto_responder on or off.
        :param value: This is the Bool to set on or off.
        """
        self.IO = value
        if self.IO:
            self.send(self.my_contact, 'Auto-response is now on')
        if self.IO:
            self.send(self.my_contact, 'Auto-response is now off')
            print('turned off :(')
            
        

