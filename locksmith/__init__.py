import base64
from threading import Thread
import time

import hvac

class Locksmith(object):
    """
    Class for fetching database credentials from Vault.
    Can also be used to encrypt/decrypt string values.

    This class will automatically renew the token provided and
    refresh any leases created as a result of fetching credentials.

    This renewal process takes place in a separate thread that
    is set to run every hour.
    """
    def __init__(self, token, host):
        """
        Initializes a new Locksmith object and starts a
        new renewal thread.
        :param token: The token to use when connecting to vault.
        :param host: The host for the Vault client.
        """
        self.token = token
        self.client = hvac.Client(url=host, token=token)
        self.leases = []

        thread = Thread(target=self.__refresh__)
        thread.setDaemon(True)
        thread.start()

    def get_credentials(self, role_name):
        """
        Fetches database credentials given a role name. These credentials
        will have their lease renewed every hour.
        :param role_name: The name of the database role to fetch credentials for.
        :return: A tuple containing a username and password for connecting to the database.
        """
        self.client.renew_token(self.token)
        response = self.client.read('/database/creds/{}'.format(role_name))
        self.leases.append(response['lease_id'])
        return response['data']['username'], response['data']['password']

    def encrypt(self, plaintext, key='bookmark'):
        """
        Encrypts a string for use when communicating between services.
        :param plaintext: The plaintext string to encrypt.
        :param key: The transport key to use when encrypting. This defaults to "bookmark".
        :return: A ciphertext for the provided plaintext. This can be passed to Locksmith#decrypt.
        """
        b64 = base64.b64encode(plaintext.encode()).decode('utf-8')
        response = self.client.write('/transit/encrypt/{}'.format(key), plaintext=b64)
        return response['data']['ciphertext']

    def decrypt(self, ciphertext, key='bookmark'):
        """
        Decrypts a given ciphertext using the given transport key.
        :param ciphertext: The ciphertext to decrypt.
        :param key: The transport key to use when decrypting. This defaults to "bookmark".
        :return: A decrypted plaintext version of the ciphertext.
        """
        response = self.client.write('/transit/decrypt/{}'.format(key), ciphertext=ciphertext)
        return base64.b64decode(response['data']['plaintext']).decode('utf-8')

    def __refresh__(self):
        """
        Infinitely loops, refreshing tokens and leases on a one hour timer.
        """
        def refresh():
            self.client.renew_token(self.token)

            increment_time = 60 * 60 # 1 hour = 3600 seconds

            for lease in self.leases:
                self.client.write('/sys/leases/renew', lease_id=lease, increment_time=increment_time)

        sleep_time = 60 * 60 # 1 hour = 3600 seconds

        while True:
            refresh()
            time.sleep(sleep_time)
