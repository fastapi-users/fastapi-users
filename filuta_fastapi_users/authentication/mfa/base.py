import random

def generate_otp_token(length=6):
    """Generate a random OTP of given length."""
    # Generate OTP using numbers 0-9
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

