__version__ = '0.1.1'

import logging
import os
import re
import sys
import socket
from subprocess import check_output
import smtplib as _smtp
from emailahoy3.exceptions import UnableToVerifyException
from emailahoy3.exceptions import HostSystemNotSupportedException


DEBUG = True


__all__ = ['VerifyEmail', 'verify_email_address', 'query_mx']

MX_RE = re.compile('mail\sexchanger\s=\s(\d+)\s(.*)\.')
EMAIL_RE = re.compile('([\w\-\.+]+@\w[\w\-]+\.+[\w\-]+)')
NOT_FOUND_KEYWORDS = [
    "does not exist",
    "doesn't exist",
    "doesn't have",
    "doesn't handle",
    "unknown user",
    "user unknown",
    "disabled",
    "discontinued",
    "unavailable",
    "unknown",
    "invalid",
    "typos",
    "unnecessary spaces",
]

UNVERIFIABLE_KEYWORDS = [
    "block",
    "block list",
    "spam",
    "spammer",
    "isp",
    "weren't sent",
    "not accepted",
    "Spamhaus",
    "suspicious",
    "Denied by policy",
    "banned sending IP",
    "sender.office.com"
]


def query_mx(host):
    """Returns all MX records of a given domain name

    Args:
        host (str): The hostname of the email address.

    Returns:
        List of email exchangers.

    Raises:
        HostSystemNotSupportedException.
    """
    mail_exchangers = []
    addr = {}

    # The 'which nslookup' will not work in Windows systems
    if os.name != "nt":
        # Get the existence of nslookup
        fout = check_output(['which', 'nslookup']).decode()
        cmd = fout.strip()
        if cmd != '':
            # Get the text from the nslookup when querying the mail exchanger
            fout = check_output([cmd, '-query=mx', host]).decode().splitlines()
            for line in fout:
                mx = MX_RE.search(line.lower())
                if mx:
                    mail_exchangers.append((eval(mx.group(1)), mx.group(2)))

            if mail_exchangers:
                mail_exchangers.sort()
    else:
        raise HostSystemNotSupportedException()
    return mail_exchangers


class VerifyEmail(object):
    """Verify if email exists"""
    EMAIL_FOUND = 1
    EMAIL_NOT_FOUND = 0
    UNABLE_TO_VERIFY = -1

    def connect(self, hostname, timeout=5):
        """Returns a server connection or None given a hostname"""
        try:
            socket.gethostbyname(hostname)
            server = _smtp.SMTP(timeout=timeout)
            code, resp = server.connect(hostname)
            if code == 220:
                return server
        except:
            pass
        return None

    def unverifiable(self, resp):
        """Return true if email is not verifiable """
        return any(a in str(resp).lower() for a in UNVERIFIABLE_KEYWORDS)

    def nonexistent(self, resp):
        """Return true if email is not found """
        return any(a in str(resp).lower() for a in NOT_FOUND_KEYWORDS)

    def verify(
            self,
            email,
            from_host='example.com',
            from_email='verify@example.com'
        ):
        """Verifies wether an email address exists

        Args:
            email (str): Email to verify.
            from_host (str): Host to be used to verify.
            from_email (str): Email to be used to verify.

        Return:
            bool.

        Raises:
            HostSystemNotSupportedException.
            UnableToVerifyException.
        """
        logging.basicConfig(level=logging.DEBUG)

        if not EMAIL_RE.search(email):
            logging.error(f"'{email}' is not a valid email")
            return self.EMAIL_NOT_FOUND

        try:
            hostname = email.strip().split('@')[1]
            socket.gethostbyname(hostname)
            mail_exchangers = query_mx(hostname)
        except Exception as e:
            logging.error(e)
            raise e

        logging.debug(f"Found mail exchangers: {mail_exchangers}")
        for i, mx in enumerate(mail_exchangers):
            mx_name = mx[1]
            logging.debug("-----------------------------------------")
            logging.debug(f"Testing {mx_name} (#{i})...")

            logging.debug(f"\tConnecting to {mx_name}")
            server = self.connect(mx_name)

            if not server:
                logging.error("\tCould not get connected to server.")
                continue

            if DEBUG:
                server.set_debuglevel(1)

            logging.debug("\tDo helo...")
            try:
                code, resp = server.helo(mx_name)
                if code != 250:
                    if not self.unverifiable(resp):
                        raise UnableToVerifyException()
                    continue
            except:
                pass

            logging.debug("\tDo mail:")
            try:
                code, resp = server.mail(from_email)
                logging.debug(f"Code: {code}")
                logging.debug(f"Response: {resp}")
                if code != 250:
                    if not self.unverifiable(resp):
                        raise UnableToVerifyException()
                    continue
            except:
                pass

            try:
                logging.debug("\tDo rcpt:")
                code, resp = server.rcpt(email)
                logging.debug(f"\t\tCode: {code}")
                logging.debug(f"\t\tResponse: {resp}")

                if code != 250:
                    if self.nonexistent(resp):
                        return self.EMAIL_NOT_FOUND
                    elif self.unverifiable(resp):
                        raise UnableToVerifyException()
                    else:
                        continue
            except:
                pass

            try:
                logging.debug("\tDo data:")
                code, resp = server.data('Ahoy. Are you there? Testing my python3 port of the package ;) {0}.{0}'.format(_smtp.CRLF))
                logging.debug(f"\t\tCode: {code}")
                logging.debug(f"\t\tResponse: {resp}")
                if code != 250:
                    if self.nonexistent(resp):
                        return self.EMAIL_NOT_FOUND
                    elif self.unverifiable(resp):
                        raise UnableToVerifyException()
                elif code == 250:
                    return self.EMAIL_FOUND
            except:
                pass

        raise UnableToVerifyException()


# given an email it returns True if it can tell it exist or False
def  verify_email_address(
        email,
        from_host='i3visio.com',
        from_email='verify@i3visio.com'
    ):
    """A quick email verification fuction

    Args:
        email (str): Email to verify.
        from_host (str): Host to be used to verify.
        from_email (str): Email to be used to verify.

    Returns:
        int. 1 for existing emails; 0, for non existing and
            -1 when it is impossible to verify.
    """
    e = VerifyEmail()

    try:
        status = e.verify(email, from_host, from_email)
        if status == e.EMAIL_FOUND:
            return 1
    except Exception:
        return -1
    return 0


if __name__ == "__main__":
    # if verify_email_address('un33kvu@gmail.com', 'djanguru.djanguru.net', 'verify@djanguru.net'):
    # if verify_email_address('un33ksssddsdsd333vu@gmail.com', 'djanguru.net', 'verify@djanguru.net'):
    # if verify_email_address('un33kvu@yahoo.com', 'djanguru.net', 'verify@djanguru.net'):
    # if verify_email_address('un33ksssddsdsd333vu@yahoo.com', 'djanguru.net', 'verify@djanguru.net'):
    # if verify_email_address('un33ksssddsdsd333vu@cnn.com', 'djanguru.net', 'verify@djanguru.net'):
    # if verify_email_address('vman@outsourcefactor.com', 'djanguru.net', 'verify@djanguru.net'):
    status = verify_email_address('asfsadfasfsdf@gmail.com', 'i3visio.com', 'sayhello@i3visio.com')
    if status == 1:
        print("Email found!")
    elif status == 0:
        print("Email not found!")
    else:
        print("Email could not be verified!")
