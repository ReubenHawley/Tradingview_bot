import email
import email.header
import imaplib
import os
import sys


class ImapClient:
    imap = None

    def __init__(self,
                 recipient,
                 server='imap.gmail.com',
                 use_ssl=True,
                 move_to_trash=True):
        # check for required param
        self.c_dir = os.path.dirname(__file__)
        with open(os.path.join(self.c_dir, "../../config.txt")) as key_file:
            _, _, _, self.pwd = key_file.read().splitlines()
        if not recipient:
            raise ValueError('You must provide a recipient email address')
        self.recipient = recipient
        self.use_ssl = use_ssl
        self.move_to_trash = move_to_trash
        self.recipient_folder = 'incoming_trades'
        self.password = self.pwd
        # instantiate our IMAP client object
        if self.use_ssl:
            self.imap = imaplib.IMAP4_SSL(server)
        else:
            self.imap = imaplib.IMAP4(server)

    def login(self):
        try:
            rv, data = self.imap.login(self.recipient, self.pwd)
        except (imaplib.IMAP4_SSL.error, imaplib.IMAP4.error) as err:
            print('LOGIN FAILED!')
            print(err)
            sys.exit(1)

    def logout(self):
        self.imap.close()
        self.imap.logout()

    def select_folder(self, folder):
        """
        Select the IMAP folder to read messages from. By default
        the class will read from the INBOX folder
        """
        self.recipient_folder = folder

    def get_messages(self, sender, subject=''):
        """
        Scans for email messages from the given sender and optionally
        with the given subject

        :param sender Email address of sender of messages you're searching for
        :param subject (Partial) subject line to scan for
        :return List of dicts of {'num': num, 'body': body}
        """
        if not sender:
            raise ValueError('You must provide a sender email address')

        # select the folder, by default INBOX
        resp, _ = self.imap.select(self.recipient_folder)
        if resp != 'OK':
            print(f"ERROR: Unable to open the {self.recipient_folder} folder")
            sys.exit(1)

        messages = []

        mbox_response, msgnums = self.imap.search(None, 'FROM', sender)
        if mbox_response == 'OK':
            for num in msgnums[0].split():
                retval, rawmsg = self.imap.fetch(num, '(RFC822)')
                if retval != 'OK':
                    print('ERROR getting message', num)
                    continue
                msg = email.message_from_bytes(rawmsg[0][1])
                msg_subject = msg["Subject"]
                if subject in msg_subject:
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            type = part.get_content_type()
                            disp = str(part.get('Content-Disposition'))
                            # look for plain text parts, but skip attachments
                            if type == 'text/plain' and 'attachment' not in disp:
                                charset = part.get_content_charset()
                                # decode the base64 unicode bytestring into plain text
                                body = part.get_payload(decode=True).decode(encoding=charset, errors="ignore")
                                # if we've found the plain/text part, stop looping thru the parts
                                break
                    else:
                        # not multipart - i.e. plain text, no attachments
                        charset = msg.get_content_charset()
                        body = msg.get_payload(decode=True).decode(encoding=charset, errors="ignore")
                    messages.append({'num': num, 'body': body})
        return messages

    def delete_message(self, msg_id):
        if not msg_id:
            return
        if self.move_to_trash:
            # move to executed trades folder
            self.imap.store(msg_id, '+X-GM-LABELS', '\\Trash')
            self.imap.expunge()
        else:
            self.imap.store(msg_id, '+FLAGS', '\\Deleted')
            self.imap.expunge()

