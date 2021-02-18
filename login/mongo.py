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
client = pymongo.MongoClient("mongodb+srv://" + username + ":" + password + "@cluster0.3ihx5.mongodb.net/?retryWrites=true&w=majority")
pymongo.MongoClient()

# Create database for User

# db and collections of user:
user = client['AmongUSTH']
u_info = user['User_info']
u_login = user['Login_info']
u_stu = user['Student']
u_lec = user['Lecturer']

# db and collections of book
book_db = client['AmongUSTH']
book  = book_db['Book_data']

# db and collections of interaction: vote and comment.
vote = client['Vote']
comment = client['Comment']


class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def register(id_, name, email, student_id, profile_pic):
        if u_info.find_one({'Email' : email}):
            print('Existed!')
        else: 
            mdict = {'UID' : id_, 'Student_ID' : student_id, 'Fullname' : name, 'Email' : email, 'Profile_pic' : profile_pic, 'role' : 'member'}
            u_info.insert_one(mdict)

    def get(id_):
        return u_info.find_one({"UID": id_})

    def get_by_itself(self):
        return u_info.find_one({"username": self.username})
    
    def account_existed(id_):
        if u_login.find_one({'UID' : id_}):
            return True
        return False

    def add_major(id_, major):
        item = u_info.find_one({'UID' : id_})
        u_info.update_one(item, {'$set': {'major' : major}})

    def is_USTHer(email):
        if re.match(r"[a-zA-Z\-\.0-9]+[@][s]?[t]?.?usth.edu.vn", email):
           return True
        return False
    
    def add_info_stu(id_, usth_id, major, schoolYear):
        mdict = {'UID' : id_, 'USTH_ID' : usth_id, 'Major': major, 'SchoolYear' : schoolYear}
        u_stu.insert_one(mdict)

    def login(bcrypt, username, password):
        mdict = u_login.find_one({'UserName' : username}, {'UserName' :1,'Hashed_password' :1})
        # print(str(mdict))
        # print(str(mdict["Hashed_password"]))
        check = bcrypt.check_password_hash(mdict["Hashed_password"], password)
        if check:
            return User(username)
        return None

    def add_info_lec(id_, department):
        mdict = {'UID' : id_, 'Department' : department}
        u_lec.insert_one(mdict)

    def add_login_info(id_, username, hased_password):
        now = datetime.now()
        mdict = {'UID' : id_, 'UserName' : username, "Hashed_password": hased_password, 'Last_active' : now}  
        u_login.insert_one(mdict)

    def get_profile_pic(id_):
        mdict = u_info.find_one({'UID' : id_}, {'Profile_pic' : 1, '_id' : 0})
        return mdict['Profile_pic']

    def get_name(id_):
        mdict = u_info.find_one({'UID' : id_}, {'Fullname' : 1, '_id' : 0})
        return mdict['Fullname']

    def get_email(id_):
        mdict = u_info.find_one({'UID' : id_}, {'Email' : 1, '_id' : 0})
        return mdict['Email']

    def get_id(username):
        mdict = u_login.find_one({'UserName' : username}, {"UID": 1, "_id" : 0})
        return mdict['UID']
    
    def set_last_active(id_):
        now = datetime.now()
        u_login.update_one({'UID' : id_}, {'$set' : {'Last_active' : str(now)}})

    def get_last_active(id_):
        return u_login.find_one({'UID' : id_})['Last_active']

# User.get_user_all()
class Book():
    def post_book(id_, book_name, type_, subject, author, description, page_number, front_link):
        if book.find_one({'book_name' : book_name}):
            print('Existed')
            pass
        else:
            link =  'https://drive.google.com/file/d/' + id_ + '/view?usp=sharing'
            mdict = {'BID' : id_, 'book_name' : book_name, 'type' : type_, 'subject' : subject, 'author' : author, 'description' : description, 'page_number' : page_number, 'link' : link, 'front' : front_link, 'download' : int('0'), 'upvote' : int('0'), 'downvote' : int('0')}
            try:
                book.insert_one(mdict)
            except:
                print("Insert failed")
    
    def count_download(id_):
        return book.update_one({'BID' : id_}, { '$inc': {'download': 1} })
        
    def upvote(id_):
        return book.update_one({'BID' : id_}, { '$inc': {'upvote': 1} })

    def upvote_(id_):
        return book.update_one({'BID' : id_}, { '$inc': {'upvote': -1} })    
            
    def downvote(id_):
        book.update_one({'BID' : id_}, { '$inc': {'downvote': 1} })

    def downvote_(id_):
        book.update_one({'BID' : id_}, { '$inc': {'downvote': -1} })

    def get_file_name(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['book_name']

    def get_type(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['type']

    def get_subject(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['subject']

    def get_author(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['author']

    def get_description(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['description']

    def get_link(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['link']

    def get_front(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['front']

    def get_page_number(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['page_number']

    def get_upvote(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['upvote']

    def get_downvote(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['downvote']

    def get_download(id_):
        mdict = book.find_one({'BID' : id_})
        return mdict['download']

    def set_status(id_, status):
        book.update_one({'BID' : id_}, {'$set' : {'status' : status}})
# Book.get_book_all()
class Vote():
    def __init__(self, up, down):
        self.up = up
        self.down = down

    def make_decision(_id, up, down):
        if vote.find_one({"_id" : _id}):
            print ("Existed")
            pass
        else :
            mdict = {'BID':_id,'up':up,'down':down}
            try:
                vote.insert_one(mdict)
            except:
                print("Insert failed")

    def get_up(id_):
        mdict = vote.find_one({'BID' : id_}, {'up' : 1, '_id' : 0})
        return mdict['up']

    def get_down(id_):
        mdict = vote.find_one({'BID' : id_}, {'down' : 1, '_id' : 0})
        return mdict['down']                        

class Comment():
    def post_comment(id_, user_id,book_id,content,comment_time):
        if comment.find_one({'content': user_id}):
            print('Existed')
            pass
        else :
            comment_time = datetime.now()
            comment_time_date = comment_time.day() + '/' + comment_time.month()
            mdict = {'_id':id_,'book_id':book_id,'user_id':user_id,'content':content,'date' :comment_time_date}
            try:
                comment.insert_one(mdict)
            except:
                print("Comment: Insert failed")

    def get_content(id_):
        mdict = book.find_one({'_id' : id_}, {'content' : 1, '_id' : 0})
        return mdict['content']
        
    def get_file(id_):
        mdict = u_login.find_one({'UID' : id_}, {'file' : 1, '_id' : 0})
        return mdict['file']

    def get_comment_time(id_):
        mdict = u_login.find_one({'_id' : id_}, {'comment_time' : 1, '_id' : 0})
        return mdict['comment_time']
    
    def delete_comment(id_):
        mdict = book.find_one({'_id' : id_})
        comment.delete_one(mdict)

class Admin():
    def is_admin(id_):
        mdict = u_info.find_one({'UID' : id_})
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
        cursor = u_info.find({})
        num = 0
        for document in cursor:
            num += 1
        return num

    def get_all_id():
        arr = []
        cursor = u_login.find({})
        for doc in cursor:
            arr.append(doc['UID'])
        return arr

    def is_online(id_):
        cursor = u_login.find_one({'UID' : id_})
        now = datetime.now()
        status = ''
        time_long = ''
        unit = ''
        hour = None
        minute = None
        last_active = datetime.strptime(cursor['Last_active'], '%Y-%m-%d %H:%M:%S.%f')
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
                if minute == 0:
                    status = 'Active'
                elif minute != 0:
                    time_long = minute

        if status != '':
            return status
        elif time_long != '':
            return str(time_long) + ' ' + unit + ' ago'

    def total_online():
        cursor = u_login.find({})
        num = 0
        for doc in cursor:
            id_ = doc['UID']
            if Admin.is_online(id_) == 'Active':
                num += 1
        return num