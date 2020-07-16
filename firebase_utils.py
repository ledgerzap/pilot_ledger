import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore

"""
Generate private key file for service account
Project Settings -> Service account -> Generate Private Key
"""
# Todo : optimize queries: add collection ref in init.

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
        :param name: User's propername, <class 'str'>
        :param email: User's email, <class 'str'>
        :param password: User's password, <class 'str'>
        :param contact: User's contact number, <class 'int'>
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
        Takes the data and pushes it to cloud firestore, if document is not provided document key is automatically
        generated.
        :param data to be pushed, <class 'dict'>
        :param collection: name of collection in cloud firestore, <class 'str'>
        :param doc: name of document in the collection, <class 'str'>
        :return: Document Id of generated data
        """
        db = firestore.client()
        ref = db.collection(collection).document(doc)
        ref.set(data)
        return ref.id

    def signin_using_email_pass(self, email, password):
        """
        SignIn function, creates a session for the signed in user.
        # Todo: add authentication
        :param email: User's email, <class 'str'>
        :param password: User's password, <class 'str'>
        :return: User's UID, <class 'str'>
        """
        user = auth.get_user_by_email(email)
        db = firestore.client()
        users_ref = db.collection('users')
        doc = users_ref.document(user.uid)
        return doc.id

    def fetch_firestore(self, collection, document=None):
        """
        Fetches a reference to cloud's firestore's document or collection.
        :param collection: Name of thr collection in firestore, <class 'str'>
        :param document: Document's name in collection
        :return: Reference to the collection or document.
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
        Add customer to the firestore's customer collection and adds the customer UID in the organization details.
        :param name: Name of the customer, <class 'str'>
        :param contact: Contact number of the customer, <class 'str'>
        :param address: Address of the customer, <class 'str'>
        :param father_name: Customer's father's name
        :param org_uid: UID of organization who adding the customer, <class 'str'>
        :param introducer: introducer of customer either from organization's customers or no one, <class 'NoneTypr'> or
               <class 'str'>
        :return: UID of customer
        """
        customer_details = {
            'name': name,
            'contact': contact,
            'father_name': father_name,
            'address': address,
            'introducer': introducer,
            'organization': org_uid,
            'deals': [],
            'bank_accounts': []
        }
        customer_uid = self.add_to_firestore(customer_details, 'customer')
        doc_ref = self.fetch_firestore('organizations', org_uid)
        doc_ref.update({'customer': firestore.ArrayUnion([customer_uid])})
        return customer_uid

    def add_organization(self, name, user_uid):
        """
        Makes a new organization with a UID and adds it into user's organizations list.
        :param name: Name of organizations
        :param user_uid: UID of organization's creater.
        :return: organization's UID
        """
        org_details = {
            'name': name,
            'super_user': user_uid,
            'customer': [],
            'users': [],
            'item_categories': [],
            'item_name': []
        }
        org_uid = self.add_to_firestore(org_details, 'organizations')
        user_doc_ref = self.fetch_firestore('users', user_uid)
        user_doc_ref.update({'organizations': firestore.ArrayUnion([org_uid])})
        return org_uid

    def add_deal(self, deal_type, customer_uid, original_bill, loan_amt, rate_of_interest, date_time, commitment_dt, lending_type,
                 broker, deal_remark):
        total_gross_val = sum(items['gross_val'] for items in original_bill)
        deal_info = {
            'deal_type': deal_type,
            'customer_id': customer_uid,
            'original_bill': original_bill,
            'outstanding_bill': original_bill,
            'withdrawn_items': [],
            'original_total_gross': total_gross_val,
            'outstanding_gross_amount': original_bill,
            'loan_amount': loan_amt,
            'interest_rate': rate_of_interest,
            'deal_date': date_time,
            'commitment_date': commitment_dt,
            'lending_type': lending_type,
            'broker': broker,
            'deal_remark': deal_remark
        }
        deal_uid = self.add_to_firestore(deal_info, 'deals')
        customer_doc_ref = self.fetch_firestore('customer', customer_uid)
        customer_doc_ref.update({'deals': firestore.ArrayUnion([deal_uid])})



if __name__ == '__main__':

    app = FirebaseSDK('ledgerzap-firebase.json')
    """
    user_data = {
        'name':'mudit',
        'contact': 7424,
        'email': "m@g.com",
        'password': "admin123"
        }
    

    user_uid = app.create_user_using_email_pass('mudit', 'mohit@ledgerzap.com', 'admin123', 7424961361)
    org_uid = app.add_organization('kaeiter', user_uid)
    app.add_customer('mudit', 7424961361, 'khargone', 'mukesh', org_uid)
    """
