import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

# Módulos:
from database import get_funcionario_by_email

load_dotenv("../.env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# --- CONFIGURAÇÕES DE SEGURANÇA ---
SECRET_KEY = os.getenv("SECRET_KEY", "uma_chave_secreta_padrao_se_nao_definida")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# CORREÇÃO: O valor do .env é uma string, precisa ser convertido para inteiro.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 1440 min = 24 horas

# --- FUNÇÕES DE SEGURANÇA ---

# CORREÇÃO 1: Nome da função corrigido de 'verifiy_password' para 'verify_password'.
# CORREÇÃO 2: Adicionado o 'return' que estava faltando.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # CORREÇÃO: O nome do parâmetro é 'algorithm', com 'm' no final.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_funcionario_by_email(email)
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin" or current_user.get("status") != "active":
        raise HTTPException(status_code=403, detail="Permissões insuficientes")
    return current_user

async def get_current_active_funcionario(current_user: dict = Depends(get_current_user)):
    if current_user.get("status") != "active":
        raise HTTPException(status_code=403, detail="Usuário inativo")
    return current_user