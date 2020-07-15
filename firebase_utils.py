import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore

"""
Generate private key file for service account
Project Settings -> Service account -> Generate Private Key
"""


class firebase_sdk():
    def __init__(self, key):
        """
        A credential initialized from a JSON certificate key file.
        """
        cred = credentials.Certificate(key)
        firebase_admin.initialize_app(cred)

    def create_user_using_email_pass(self, user_data):
        """
        Creates user, adds user data to database
        :param user_data: dict
        :return: None
        """
        # Todo: Same user error handling.
        user = auth.create_user(email=user_data['email'], password=user_data['password'])
        collection = 'users'
        doc = user.uid
        self.add_to_firestore(user_data, collection, doc)

    def add_to_firestore(self, data, collection, doc=None):
        """
        Push Data to firestore, if doc not provided uses auto generated key
        :param data: dict
        :param collection: string
        :param doc: string
        :return: None
        """
        db = firestore.client()
        ref = db.collection(collection).document(doc)
        ref.set(data)
        print(ref.id)

    def signin_using_email_pass(self, email, password):
        """
        # Todo: returns uid - doc.id
        :param email:
        :param password:
        :return:
        """
        user = auth.get_user_by_email(email)
        db = firestore.client()
        users_ref = db.collection('users')
        doc = users_ref.document(user.uid)
        return doc.id



app = firebase_sdk('firebase-sdk.json')
"""
user_data = {
    'name':'mudit',
    'contact': 7424,
    'email': "m@g.com",
    'password': "admin123"
    }
"""
