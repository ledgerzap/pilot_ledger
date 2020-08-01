import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
from firebase_admin import exceptions
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
        self.db = firestore.client()
        self.user_ref = self.db.collection('users')


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
        try:
            user = auth.create_user(email=email, password=password)
        except exceptions.AlreadyExistsError:
            return "USER ALREADY EXIST"
        except ValueError:
            return "Password must be a string at least 6 characters long"
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
        ref = self.db.collection(collection).document(doc)
        ref.set(data)
        return ref.id

    def signin_using_email_pass(self, email, password):
        """
        Signs in the user using the firebase authentication and creates a session for the signed in user.
        :param email: User's email, <class 'str'>
        :param password: User's password, <class 'str'>
        :return: User's UID, <class 'str'>
        """
        try:
            user = auth.get_user_by_email(email)
        except exceptions.NotFoundError:
            return "USER NOT FOUND"

        user_doc_ref = self.user_ref.document(user.uid)
        user_dict = user_doc_ref.get().to_dict()
        passwd = user_dict['password']
        if passwd == password:
            return user.uid
        else:
            return "INCORRECT PASSWORD"



    def fetch_firestore(self, collection, document=None):
        """
        Fetches a reference to cloud's firestore's document or collection.
        :param collection: Name of thr collection in firestore, <class 'str'>
        :param document: Document's name in collection
        :return: Reference to the collection or document.
        """
        collection_ref = self.db.collection(collection)
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
        :param introducer: introducer of customer either from organization's customers or no one, <class 'NoneType'> or
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
            'deals': [],
            'customer': [],
            'users': [],
            'item_categories': [],
            'item_name': []
        }
        org_uid = self.add_to_firestore(org_details, 'organizations')
        user_doc_ref = self.fetch_firestore('users', user_uid)
        user_doc_ref.update({'organizations': firestore.ArrayUnion([org_uid])})
        return org_uid


    def fetch_orgs(self, user_uid):
        org_ref = self.db.collection('organizations')
        user_doc = self.db.collection('users').document(user_uid)
        user_dict = user_doc.get().to_dict()
        org_uids = user_dict['organizations']
        names = []
        for uid in org_uids:
            org_dict = org_ref.document(uid).get().to_dict()
            names.append(org_dict['name'])
        return names

    def fetch_deals(self, org_uid):
        org_ref = self.db.collection('organizations').document(org_uid)
        org_dict = org_ref.get().to_dict()
        org_deals = org_dict['deals']
        curr_deals = []
        for deal_uid in org_deals:
            deal_ref = self.db.collection('deals').document(deal_uid)
            deal_dict = deal_ref.get().to_dict()
            curr_deals.append(deal_dict['outstanding_bill'])
        return curr_deals



class Deals(FirebaseSDK):
    def __init__(self):
        self.deals_ref = self.db.collection('deals')
        self.org_ref = self.db.collection('organizations')
        self.users_ref = self.db.collection('users')
        self.customer_ref = self.db.collection('customer')

    def add_deal(self, deal_type, customer_uid, original_bill, loan_amt, rate_of_interest, date_time, commitment_dt,
                 lending_type, broker, deal_remark, bank_acc=None):
        """
        :param deal_type: The type of deal (mortgage or non-m)
        :type deal_type: <class 'str'>
        :param customer_uid: The unique ID of customer
        :type customer_uid: <class 'str'>
        :param original_bill: List of dictionary where each item of list is a bill composed of item_name, item_type,
                              quantity, weight and gross value.
        :type original_bill: <class 'list'>
        :param loan_amt: Amount of money loaned.
        :type loan_amt: <class 'float'>
        :param rate_of_interest: Rate of interest on the deal
        :type rate_of_interest: <class 'float'>
        :param date_time: Date and time when the deal was signed
        :type date_time: <class 'datetime'>
        :param commitment_dt: Commitment datetime of the customer.
        :type commitment_dt: <class 'datetime'>
        :param lending_type: Lending type of the loaned amount (Bank Account/ Cash)
        :type lending_type: <class 'str'>
        :param bank_acc: Bank Account of customer, if amount loaned in bank account
        :type: <class 'str'>
        :param broker: The user of organization who signed the deal
        :type broker: <class 'str'>
        :param deal_remark: Remark or final notes on the deal.
        :type deal_remark: <class 'str'>
        """
        total_gross_val = sum(items['gross_val'] for items in original_bill)
        total_weight = sum(items['item_weight'] for items in original_bill)
        item_names = [items['item_name'] for items in original_bill]
        item_types = [items['item_types'] for items in original_bill]
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
            'bank_account': bank_acc,
            'broker': broker,
            'deal_remark': deal_remark,
            'deal_status': 0
        }
        deal_uid = self.add_to_firestore(deal_info, 'deals')
        customer_doc = self.customer_ref.document(customer_uid)
        customer_doc.update({'deals': firestore.ArrayUnion([deal_uid]),
                             'bank_accounts': firestore.ArrayUnion([bank_acc])})
        customer_dict = customer_doc.get().to_dict()
        org_doc = self.org_ref.document(customer_dict['organization'])
        org_doc.update({'deals': firestore.ArrayUnion([deal_uid]),
                        'item_name': firestore.ArrayUnion([item_names]),
                        'item_categories': firestore.ArrayUnion([item_types])})
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
        # print(type(deal_dic))
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
        if field == "original_bill":
            pass
            # BILL Quantity type
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
    item = {'item_name': 'kada', 'item_type': 'silver', 'item_weight': 5, 'gross_val': 15000}
    d.withdrawal(item, "iP7Thd5kGlw3SvFrOXCm")
