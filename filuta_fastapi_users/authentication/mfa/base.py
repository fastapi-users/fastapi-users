import random

async def generate_all_otps(record): 
    mfa_scopes = record.mfa_scopes
    
    if "email" in mfa_scopes and mfa_scopes["email"] == 0:
        email_token = generate_otp()
        
        

def generate_otp(length=6):
    """Generate a random OTP of given length."""
    # Generate OTP using numbers 0-9
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

