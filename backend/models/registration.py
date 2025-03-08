from pydantic import BaseModel

# Validé
class RegistrationInitResponse(BaseModel):
    registration_id: str
    auth_url: str
    message: str

# Validé
class RegistrationComplete(BaseModel):
    registration_id: str
    auth_code: str