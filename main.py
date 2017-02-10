# Brandon Kupczyk (10/31/16)

import configparser
from threading import Thread
from json_decoder import json_decoder
import queue
import PBClient
import time
import PBAutoRespond


def main():
    """
    Initializes from Pushbullet.cfg found in the root dir and a new thread  Checks for a new message in the queue and
    responds to it if need be.
    """
    config = configparser.ConfigParser()
    config.read('PBAutoRespond.cfg')

    try:
        my_api_key = config.get('Configs', 'api_key')
        my_device_nickname = config.get('Configs', 'device_nickname')
        Vcard_file = config.get('Configs', 'Vcard_file')
        my_contact = config.get('Configs', 'your_name_on_your_device')
    except Exception:
        print('Not able to PBAutoRespond.cfg')
    print('Configs parsed succesfully')

    my_queue = queue.Queue(maxsize=0)
    PBsend = PBAutoRespond.PBAutoRespond(my_api_key, my_device_nickname, my_contact, Vcard_file)

    worker = Thread(target=get_PBAccess, args=(my_queue, my_api_key,))
    worker.setDaemon(True)
    worker.start()
    
    while True:
        if my_queue.qsize() != 0:
            d = my_queue.get(True)
            jd = json_decoder.decode(d)
            if jd.type == 'push':
                try:
                    if jd.push.type == 'sms_changed':
                        if len(jd.push.notifications) != 0:  # Notifications come as lists; if list isn't empty
                            message = jd.push.notifications.pop(0)
                            message_recieved(PBsend, my_contact, message.title, message.body)
                except Exception as e:
                    print('Exception: ' + str(e))
                    print('Not able to parse JSON from PushBullet')
                    raise

        time.sleep(2)


def get_PBAccess(the_queue, api_key):
    """
    Used to create a child thread to initialize the Pushbullet client where the queue gets filled.
    :param the_queue: This is the queue shared by the main thread and the child.
    :param api_key: The api key is a string found and imported from the config
    :return: Runs forever
    """
    pbc = PBClient.PBClient("wss://stream.pushbullet.com/websocket/" + api_key)
    pbc.init_queue(the_queue)
    pbc.Daemon = True
    pbc.connect()
    pbc.run_forever()


def message_recieved(PBsend, my_contact, sender, message):
    """
    This method is used to decide what to do when a message is received.
    :param PBsend: This is the PBAutoRespond object used to send messages.
    :param my_contact: This is found in the configs and should be a string with the name how it is found in the
    contacts on the device.
    :param sender: This is a string contact name from the contacts.
    :param message: The text of the message which is being sent.
    :return:
    """
    if sender == my_contact:
        if message[:11].lower() == 'setmessage:':
            PBsend.set_away_message(message[11:])
        if message.lower() == 'off':
            PBsend.set_ONOFF(False)
            print('trying to turn off service')
        if message.lower() == 'on':
            PBsend.set_ONOFF(True)
            print('trying to turn on service')
        elif message[:23].lower() == 'command not recognized.':
            return
        else:
            message = 'Command not recognized. Usage: setmessage: , on, off. add a message you would like to have' \
                      ' after setmessage:.'
            PBsend.send(my_contact, message)
            return
    try:
        PBsend.sendAwayMes(sender, message)
    except Exception as e:
        print('Exception: ' + str(e))


if __name__ == '__main__':
    main()
