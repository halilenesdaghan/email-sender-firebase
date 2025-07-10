# src/firebase_client.py (Revize Edilmiş Tam Hali)
import os
import firebase_admin
from firebase_admin import credentials, firestore
from config.settings import FIREBASE_CONFIG_PATH
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FirebaseClient:
    """
    Firestore ile etkileşim kurmak için bir istemci.
    Sadece e-posta görevleri oluşturur.
    """
    def __init__(self):
        try:
            if not os.path.exists(FIREBASE_CONFIG_PATH):
                raise FileNotFoundError(f"Firebase yapılandırma dosyası bulunamadı: {FIREBASE_CONFIG_PATH}")
            
            # Sadece bir kere başlatıldığından emin ol
            if not firebase_admin._apps:
                cred = credentials.Certificate(FIREBASE_CONFIG_PATH)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase istemcisi başarıyla başlatıldı.")
            
            self.db = firestore.client()

        except Exception as e:
            logger.error(f"Firebase istemcisi başlatılırken hata oluştu: {e}")
            raise

    def add_email_task(self, recipient: str, subject: str, body: str) -> str:
        """
        Firestore'daki 'email_tasks' koleksiyonuna yeni bir görev ekler.
        
        Args:
            recipient (str): E-posta alıcısı.
            subject (str): E-posta konusu.
            body (str): E-posta içeriği.
            
        Returns:
            str: Oluşturulan Firestore dokümanının ID'si.
        """
        try:
            task_data = {
                'recipient': recipient,
                'subject': subject,
                'body': body,
                'createdAt': firestore.SERVER_TIMESTAMP
            }
            # 'email_tasks' koleksiyonuna yeni bir doküman ekle
            doc_ref = self.db.collection('email_tasks').add(task_data)[1]
            logger.info(f"E-posta görevi başarıyla Firestore'a eklendi. Görev ID: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Firestore'a e-posta görevi eklenirken hata: {e}")
            raise