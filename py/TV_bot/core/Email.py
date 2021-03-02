from .ImapClient import ImapClient
import os
import sys
import smtplib
from email.message import EmailMessage


class EmailScanner:
    def __init__(self):
        try:
            self.c_dir = os.path.dirname(__file__)
            with open(os.path.join(self.c_dir, "../../config.txt")) as key_file:
                _, _, self.username, self.pw = key_file.read().splitlines()
            self.imap = ImapClient(recipient=self.username)
            self.messages = None
            self.imap.login()

        except FileNotFoundError:
            print("no config file found, please create one or make sure its in the working directory... \nexiting")
            sys.exit(0)

        except ConnectionError:
            print(f'error instantiating email: could not connect to exchange')

    def send_report(self, data, receiver=None, subject="Trade executed"):
        try:
            """ data to be sent here should include trade execution details
            and should be passed directly from the order return"""
            # contacts = ["algotrader161@gmail.com"] #  used in case of a mailing list
            msg = EmailMessage()
            msg['Subject'] = subject
            msg["From"] = self.username
            if receiver is not None:
                msg["To"] = receiver
            else:
                msg["To"] = self.username
            if isinstance(data, dict):  # this checks if we have trade parameters to access
                if "error" in data:
                    data.pop("error")
                    msg['Subject'] = data['name']
                    msg.set_content(f'Tried to execute trade but failed with the following message:\n'
                                    f'{data["message"]}')

                elif "insufficient" in data:
                    msg.set_content(f'Tried to execute trade but failed with the following message:\n'
                                    f'{data}')
                else:
                    msg.set_content(f'{subject} with the following details:\n'
                                    f'Symbol: {data["symbol"]}\n'
                                    f'Direction: {data["side"]}\n'
                                    f'Order type: {data["type"]}\n'
                                    f'Size: {data["amount"]}'
                                    f'executed at {data["price"]} ')
            else:
                msg.set_content(f'An activity has taken place with the following details:\n{data}')

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.username, self.pw)

                smtp.send_message(msg=msg)
        except Exception as e:
            print(f'Encountered error sending report {e.__traceback__} with the following arguments:{e.args}')
