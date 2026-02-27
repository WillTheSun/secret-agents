def _caesar_shift(text, shift):
    result = []
    for char in text.upper():
        if char.isalpha():
            result.append(chr(((ord(char) - 65 + shift) % 26) + 65))
        else:
            result.append(char)
    return ''.join(result)


def encrypt_message(plaintext, shift):
    return _caesar_shift(plaintext, shift)


def decrypt_message(ciphertext, shift):
    decrypted = _caesar_shift(ciphertext, -shift)
    return f"Unencrypted message: {decrypted}"
