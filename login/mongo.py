import pymongo
#from login.User import User as usr
from flask_login import UserMixin
import json
import re
from datetime import datetime

dat = json.load(open('login/mongo.json'))
data = dat
username = data['read_write'][0]['username']
password = data['read_write'][0]['password']
client = pymongo.MongoClient("mongodb+srv://" + username + ":" + password +
                             "@cluster0.3ihx5.mongodb.net/?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
pymongo.MongoClient()

# Create database for User

# db and collections of user:
db = client['AmongUSTH']
user = db['User_info']

# db and collections of book
book = db['Book_data']
# db and collections of interaction: vote and comment.
vote = db['Vote']
comment = client['AmongUSTH']['Comment']


class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def register(id_, name, email, student_id, profile_pic, password):
        if user.find_one({'Email': email}):
            print('Existed!')
        else:
            username = email.split(".")[1].split("@")[0]
            hashed_password = password
            mdict = {'_id': id_, 'Student_ID': student_id, 'Fullname': name, 'Email': email, 'Profile_pic': profile_pic,
                     'role': 'member', 'UserName': username, 'Hashed_password': hashed_password, 'Last_active': None}
            user.insert_one(mdict)

    def get(id_):
        return user.find_one({"_id": id_})

    def get_by_itself(self):
        return user.find_one({"username": self.username})

    def account_existed(id_):
        if user.find_one({'_id': id_}):
            return True
        return False

    def is_USTHer(email):
        if re.match(r"[a-zA-Z\-\.0-9]+[@][s]?[t]?.?usth.edu.vn", email):
            return True
        return False

    def login(bcrypt, username, password):
        mdict = user.find_one({'UserName': username}, {
                              'UserName': 1, 'Hashed_password': 1})
        if mdict:
            check = bcrypt.check_password_hash(
                mdict["Hashed_password"], password)
            if check:
                return User(username)

        return None

    def add_login_info(id_, username, hased_password):
        now = datetime.now()
        new_value = {'UserName': username,
                     "Hashed_password": hased_password, 'Last_active': now}
        user.update_one({'_id': id_}, {'$set', new_value})

    def get_profile_pic(id_):
        mdict = user.find_one({'_id': id_})
        return mdict['Profile_pic']

    def get_name(id_):
        mdict = user.find_one({'_id': id_})
        return mdict['Fullname']

    def get_email(id_):
        mdict = user.find_one({'_id': id_})
        return mdict['Email']

    def get_id(username):
        mdict = user.find_one({'UserName': username})
        return mdict['_id']

    def set_last_active(id_):
        now = datetime.now()
        user.update_one({'_id': id_}, {'$set': {'Last_active': str(now)}})

    def get_last_active(id_):
        return user.find_one({'_id': id_})['Last_active']

# User.get_user_all()


class Book():
    def post_book(id_, book_name, type_, subject, author, description, page_number, front_link):
        if book.find_one({'book_name': book_name}):
            print('Existed')
        else:
            link = 'https://drive.google.com/file/d/' + id_ + '/view?usp=sharing'
            mdict = {'_id': id_, 'book_name': book_name, 'type': type_, 'subject': subject, 'author': author, 'description': description,
                     'page_number': int(page_number), 'link': [link], 'front': front_link, 'download': int('0'), 'upvote': [], 'downvote': []}
            try:
                book.insert_one(mdict)
            except:
                print("Insert failed")

    def count_download(id_):
        return book.update_one({'_id': id_}, {'$inc': {'download': 1}})

    def get_file_name(id_):
        mdict = book.find_one({'_id': id_}, {"book_name": 1})
        return mdict['book_name']

    def get_type(id_):
        mdict = book.find_one({'_id': id_}, {"type": 1})
        return mdict['type']

    def get_subject(id_):
        mdict = book.find_one({'_id': id_}, {"subject": 1})
        return mdict['subject']

    def get_author(id_):
        mdict = book.find_one({'_id': id_}, {"author": 1})
        return mdict['author']

    def get_description(id_):
        mdict = book.find_one({'_id': id_}, {'description': 1})
        return mdict['description']

    def get_link(id_):
        mdict = book.find_one({'_id': id_}, {'link': 1})
        return mdict['link']

    def get_front(id_):
        mdict = book.find_one({'_id': id_}, {'front': 1})
        return mdict['front']

    def get_page_number(id_):
        mdict = book.find_one({'_id': id_}, {'page_number': 1})
        return mdict['page_number']

    def get_download(id_):
        mdict = book.find_one({'_id': id_}, {"download": 1})
        return mdict['download']

    def set_status(id_, status):
        book.update_one({'BID': id_}, {'$set': {'status': status}})

    def get_book(id_):
        return book.find_one({"_id": id_})

    def get_all_materials(type_of_material="Book"):
        mdict = book.find({"type": type_of_material})
        return mdict

    def append_link(id_, new_file_id):
        link = 'https://drive.google.com/file/d/' + new_file_id + '/view?usp=sharing'
        book.update_one({'_id': id_}, {'$push': {'link': link}})

    def upvote(id_, user_id):
        book.update_one({'_id': id_}, {'$push': {'upvote': user_id}})

    def upvote_(id_, user_id):
        book.update_one({'_id': id_}, {'$pull': {'upvote': user_id}})

    def downvote_(id_, user_id):
        book.update_one({'_id': id_}, {'$pull': {'downvote': user_id}})

    def downvote(id_, user_id):
        book.update_one({'_id': id_}, {'$push': {'downvote': user_id}})

    def get_up(id_):
        mdict = book.find_one({'_id': id_})
        return mdict['upvote']

    def get_down(id_):
        mdict = book.find_one({'_id': id_})
        return mdict['downvote']


class Comment():
    def post_comment(user_id, book_id, content):
        if comment.find_one({'content': user_id}):
            print('Existed')
            pass
        else:
            seq = Comment.total_comment()
            comment_time = datetime.now()
            mdict = {'_id': seq + 1, 'book_id': book_id, 'user_id': user_id,
                     'content': content, 'time': str(comment_time)}
            try:
                comment.insert_one(mdict)
            except:
                print("Comment: Insert failed")

    def get_content(_id):
        mdict = comment.find_one({'_id': _id})
        return mdict['content']

    def get_comment_author(_id):
        mdict = comment.find_one({'_id': _id})
        return mdict['user_id']

    def get_comment_time(_id):
        mdict = comment.find_one({'_id': _id})
        return mdict['time']

    def delete_comment(_id):
        mdict = comment.find_one({'_id': _id})
        comment.delete_one(mdict)

    def get_all_comment(_id):
        return comment.find({'book_id': _id})

    def total_comment():
        seq = 0
        for cursor in comment.find():
            seq += 1
        return seq


class Admin():
    def is_admin(id_):
        mdict = user.find_one({'_id': id_})
        if mdict['role'] == 'admin':
            return True
        return False

    def total_materials():
        cursor = book.find({})
        num = 0
        for document in cursor:
            num += 1
        return num

    def total_users():
        cursor = user.find({})
        num = 0
        for document in cursor:
            num += 1
        return num

    def get_all_id():
        arr = []
        cursor = user.find({})
        for doc in cursor:
            arr.append(doc['_id'])
        return arr

    def is_online(id_):
        cursor = user.find_one({'_id': id_})
        now = datetime.now()
        status = ''
        time_long = ''
        unit = ''
        hour = None
        minute = None
        last_active = datetime.strptime(
            cursor['Last_active'], '%Y-%m-%d %H:%M:%S.%f')
        time = now - last_active
        if time.days > 0:
            time_long = time.days
            unit = 'day(s)'
        elif time.days == 0:
            hour = int(time.seconds/3600)
            unit = 'hour(s)'
            if hour >= 1:
                time_long = hour
            elif hour < 1:
                minute = int(time.seconds/60)
                unit = 'minute(s)'
                if minute <= 3:
                    status = 'Active'
                elif minute != 0:
                    time_long = minute - 3

        if status != '':
            return status
        elif time_long != '':
            return str(time_long) + ' ' + unit + ' ago'

    def total_online():
        cursor = user.find({})
        num = 0
        for doc in cursor:
            id_ = doc['_id']
            if Admin.is_online(id_) == 'Active':
                num += 1
        return num


if __name__ == "__main__":
    # a = book.find()
    # print(a['BID'])
    print(User.get('105528251893670234146'))
