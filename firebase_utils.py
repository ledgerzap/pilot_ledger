import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
import datetime

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
        :type <class 'str'>
        :param user_uid: UID of organization's creater.
        :type: <class 'dict'>
        :return: organization's UID
        :rtype: <class 'str'>
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


class Deals(FirebaseSDK):
    def __init__(self):
        db = firestore.client()
        self.deals_ref = db.collection('deals')

    def add_deal(self, deal_type, customer_uid, original_bill, loan_amt, rate_of_interest, date_time, commitment_dt,
                 lending_type,
                 broker, deal_remark):
        """

        :param deal_type:
        :type deal_type:
        :param customer_uid:
        :type customer_uid:
        :param original_bill:
        :type original_bill:
        :param loan_amt:
        :type loan_amt:
        :param rate_of_interest:
        :type rate_of_interest:
        :param date_time:
        :type date_time:
        :param commitment_dt:
        :type commitment_dt:
        :param lending_type:
        :type lending_type:
        :param broker:
        :type broker:
        :param deal_remark:
        :type deal_remark:
        """
        total_gross_val = sum(items['gross_val'] for items in original_bill)
        total_weight = sum(items['item_weight'] for items in original_bill)
        deal_info = {
            'deal_type': deal_type,
            'customer_id': customer_uid,
            'original_bill': original_bill,
            'outstanding_bill': original_bill,
            'total_weight': total_weight,
            'original_total_gross': total_gross_val,
            'withdrawn_items': [],
            'outstanding_gross_amount': total_gross_val,
            'loan_amount': loan_amt,
            'interest_rate': rate_of_interest,
            'deal_date': date_time,
            'commitment_date': commitment_dt,
            'lending_type': lending_type,
            'broker': broker,
            'deal_remark': deal_remark,
            'deal_status': 0
        }
        deal_uid = self.add_to_firestore(deal_info, 'deals')
        customer_doc_ref = self.fetch_firestore('customer', customer_uid)
        customer_doc_ref.update({'deals': firestore.ArrayUnion([deal_uid])})
        return deal_uid

    def withdrawal(self, item_details, deal_uid):
        """
        Function top withdraw item from the deal. Item is removed and corresponding details are also updated.
        :param item_details: Details of item to be removed.
        :type item_details: <class 'dict'>
        :param deal_uid: Unique Id of deal
        :type deal_uid: <class 'str'>
        :return: None
        :rtype:None
        """
        deal = self.deals_ref.document(deal_uid)
        deal_dic = deal.get().to_dict()
        print(deal_dic)
        #print(type(deal_dic))
        """
        outstanding_gross_amount = deal_dic['outstanding_gross_amount']-item_details['gross_val']
        if outstanding_gross_amount==0:
            deal.update({'deal_status':1})
        #print(outstanding_gross_amount)
        deal.update({'outstanding_bill': firestore.ArrayRemove([item_details])})
        deal.update({'withdrawn_items': firestore.ArrayUnion([item_details])})
        deal.update({'outstanding_gross_amount': outstanding_gross_amount})
        """

    def edit_existing_deal(self, field, value, deal_uid):
        if field=="original_bill":
            bill_ref =
        deal_doc = self.deals_ref.document(deal_uid)
        deal_doc.update({'{}'.format(field): value})
        pass


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
    d = Deals()
    """
    d.add_deal(
        "mortgage",
        "mpXEygVCPJTuXZnMIHAl",
        [{'item_name': 'biscuit', 'item_type': 'gold', 'item_weight': 10, 'gross_val':50000, 'quantity':2},
         {'item_name': 'kada', 'item_type': 'silver', 'item_weight': 5, 'gross_val':15000 ,'quantity':1}],
        650000,
        0.1,
        str(datetime.datetime.now()),
        str(datetime.timedelta(days=300)),
        "cash",
        "mukesh",
        "deal done"
    )
    """
    item =  {'item_name': 'kada', 'item_type': 'silver', 'item_weight': 5, 'gross_val':15000}
    d.withdrawal(item, "iP7Thd5kGlw3SvFrOXCm")