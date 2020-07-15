import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore

"""
Generate private key file for service account
Project Settings -> Service account -> Generate Private Key
"""


class FirebaseSDK(object):
    """
    A generic messenger for firebase administration
    Utilised for pushing and fetching the firebase firestore db
    """
    def __init__(self, key):
        """
        :param key: A credential initialized from a JSON certificate key file.
        """
        cred = credentials.Certificate(key)
        firebase_admin.initialize_app(cred)

    def create_user_using_email_pass(self, name, email, password, contact):
        """
        Create a new user and return the UID of newly created user
        :param name: User's propername, class <str>
        :param email: string
        :param password: string
        :param contact: number
        :return: UID of created user
        """
        # Todo: Same user error handling.
        user_data = {
            'name': name,
            'email': email,
            'password': password,
            'contact': contact,
            'organizations': []
        }
        user = auth.create_user(email=email, password=password)
        self.add_to_firestore(user_data, 'users', user.uid)
        return user.uid

    def add_to_firestore(self, data, collection, doc=None):
        """
        Push Data to firestore, if doc not provided uses auto generated key
        :param data: dict
        :param collection: string
        :param doc: string
        :return: document Id of generated data
        """
        db = firestore.client()
        ref = db.collection(collection).document(doc)
        ref.set(data)
        return ref.id

    def signin_using_email_pass(self, email, password):
        """
        # Todo: add authentication
        :param email:
        :param password:
        :return: user document
        """
        user = auth.get_user_by_email(email)
        db = firestore.client()
        users_ref = db.collection('users')
        doc = users_ref.document(user.uid)
        return doc

    def fetch_firestore(self, collection, document=None):
        """
        Fetches reference to firestore. Reference to collection if document is not given
        :param collection: string
        :param document: string
        :return: collection or document reference to firestore
        """
        db = firestore.client()
        collection_ref = db.collection(collection)
        if document:
            doc_ref = collection_ref.document(document)
            return doc_ref
        else:
            return collection_ref

    def add_customer(self, name, contact, address, father_name, org_uid, introducer=None):
        """
        Add a new customer for your organization and adds the customer id in your organizations' customer array
        :param name: string
        :param contact: number
        :param address: string
        :param father_name: string
        :param org_uid: string
        :param introducer: None or existing customer
        :param deals: list of deals of a customer
        :return: uid of customer
        """
        customer_details = {
            'name': name,
            'contact': contact,
            'father_name': father_name,
            'address': address,
            'introducer': introducer,
            'deals': []
        }
        customer_uid = self.add_to_firestore(customer_details, 'customer')
        # print(type(customer_uid))
        doc_ref = self.fetch_firestore('organizations', org_uid)
        doc_ref.update({'customer': firestore.ArrayUnion([customer_uid])})
        return customer_uid

    def add_organization(self, name, user_uid):
        """
        Creates a new organization.
        :param name: string
        :param user_uid: string
        :return: organization's unique id
        """
        org_details = {
            'name': name,
            'super_user': user_uid,
            'customer': [],
            'users': []
        }
        org_uid = self.add_to_firestore(org_details, 'organizations')
        user_doc_ref = self.fetch_firestore('users', user_uid)
        user_doc_ref.update({'organizations': firestore.ArrayUnion([org_uid])})
        return org_uid

if __name__ == '__main__':

    app = FirebaseSDK('ledgerzap-firebase.json')
    """
    user_data = {
        'name':'mudit',
        'contact': 7424,
        'email': "m@g.com",
        'password': "admin123"
        }
    """

    user_uid = app.create_user_using_email_pass('mudit', 'mohit@ledgerzap.com', 'admin123', 7424961361)
    org_uid = app.add_organization('kaeiter', user_uid)
    app.add_customer('mudit', 7424961361, 'khargone', 'mukesh', org_uid)
