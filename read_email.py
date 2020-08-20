from ImapClient import ImapClient
import os
import re
import sys
import smtplib
from email.message import EmailMessage


def find(text):
    search_results = re.search(r"(?<=AAA).*?(?=ZZZ)", text)
    if search_results:
        found = search_results.group(0)
        return found


class EmailScanner:
    def __init__(self):
        try:
            self.c_dir = os.path.dirname(__file__)
            with open(os.path.join(self.c_dir, "config.txt")) as key_file:
                _, _, self.username, _ = key_file.read().splitlines()
            self.imap = ImapClient(recipient=self.username)
            self.messages = None
            self.imap.login()
            self.FetchEmails()
            self.message_total = None
        except FileNotFoundError:
            print("no config file found, please create one or make sure its in the working directory... \nexiting")
            sys.exit(0)

    def FetchEmails(self):
        try:
            self.messages = self.imap.get_messages(sender='noreply@tradingview.com')
            if self.messages is not None:
                return self.messages
            else:
                self.LogOut()
        except ConnectionError:
            print("Failed to connect. retrying...")
            self.FetchEmails()
        except Exception as e:
            print(f'Encountered error {e}')
            self.Send_report(e, f'{e.args}')

    def CountEmails(self):
        try:
            # Do something with the messages
            # returns the last message received
            latest_email = self.messages[-1]
            self.message_total = latest_email['num']  # decode("utf-8"))  # uses the body key in the latest email dict
            return self.message_total
        except IndexError:
            print("no valid trade execution parameters")
        except Exception as e:
            print(f'Encountered error {e}')
            self.Send_report(e, f'{e.args}')

    def email_scanner(self):
        try:
            # Do something with the messages
            # returns the last message received
            latest_email = self.messages[-1]
            alert = latest_email['body']  # uses the body key in the latest email dict
            results = find(alert)  # using the string parser search for trade parameters
            if results is not None and results != []:  # ensures we only accept valid trade parameters
                params = results.split()
                for counter, parameter in enumerate(params):  # create an index for list params
                    if isinstance(parameter, str):  # testing if parameter is str
                        params[counter] = parameter.upper()  # set the relevant index equal to the new uppercase value

                return params   # split all parameters into a list
            else:
                print("no valid trade execution parameters")
        except IndexError:
            print("no valid trade execution parameters")
        except Exception as e:
            print(f'Encountered error {e}')
            self.Send_report(e, f'{e.args}')

    def LogOut(self):
        self.imap.logout()

    @staticmethod
    def Send_report(data, subject="Trade executed",):
        """ data to be sent here should include trade execution details
        and should be passed directly from the order return"""
        # contacts = ["algotrader161@gmail.com"] #  used in case of a mailing list
        msg = EmailMessage()
        msg['Subject'] = subject
        msg["From"] = 'algotrader161@gmail.com'
        msg["To"] = 'algotrader161@gmail.com'
        if isinstance(data, dict):  # this checks if we have trade parameters to access
            if "error" in data:
                data.pop("error")
                msg['Subject'] = data['name']
                msg.set_content(f'Tried to execute trade but failed with the following message:\n'
                                f'{data["message"]}')
            else:
                data.pop("info")
                msg.set_content(f'{subject} with the following details:\n'
                                f'Symbol: {data["symbol"]}\n'
                                f'Direction: {data["side"]}\n'
                                f'Order type: {data["ordType"]}\n'
                                f'Size: {data["orderQty"]}'
                                f'executed at {data["price"]} ')
        else:
            msg.set_content(f'An activity has taken place with the following details:\n{data}')

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login('algotrader161@gmail.com', 'Computers161')

                smtp.send_message(msg=msg)
        except Exception as e:
            print(f'Encountered error {e}')
