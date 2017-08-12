import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from locksmith import Locksmith

def test_locksmith():
    test_client = Locksmith(os.environ['VAULT_TOKEN'], 'https://vault.dev.bookmark.services')
    TESt_STRING = 'hello world!'
    ciphertext = test_client.encrypt(TESt_STRING)
    plaintext = test_client.decrypt(ciphertext)

    assert TESt_STRING == plaintext
