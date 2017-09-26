from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin
import json
import uuid
import os

# define profile.json constant, the file is used to
# save user name and password_hash
PROFILE_FILE = "/root/Desktop/vikit/vikit/webplatform/profiles.json"

class User(UserMixin):
    def __init__(self, username):
        self.username = username
        self.password_hash = self.get_password_hash()
        self.id = self.get_id()

    '''
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    '''

    '''
    @password.setter
    def password(self, password):
        """save user name, id and password hash to json file"""
        self.password_hash = generate_password_hash(password)
        with open(PROFILE_FILE, 'w+') as f:
            try:
                profiles = json.load(f)
            except ValueError:
                profiles = {}
            profiles[self.username] = [self.password_hash,
                                       self.id]
            f.write(json.dumps(profiles))
    '''

    def verify_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_password_hash(self):
        """try to get password hash from file.

        :return password_hash: if the there is corresponding user in
                the file, return password hash.
                None: if there is no corresponding user, return None.
        """
        try:
            with open(PROFILE_FILE) as f:
                user_profiles = json.load(f)
                user_info = user_profiles.get(self.username)
                if user_info is not None:
                    return user_info[0]
        except IOError,e:
            print e
            return None
        except ValueError:
            return None
        return None

    def get_id(self):
        """get user id from profile file, if not exist, it will
        generate a uuid for the user.
        """
        if self.username is not None:
            try:
                with open(PROFILE_FILE) as f:
                    user_profiles = json.load(f)
                    if self.username in user_profiles:
                        return user_profiles[self.username][1]
            except IOError:
                pass
            except ValueError:
                pass
        return unicode(uuid.uuid4())

    @staticmethod
    def get(user_id):
        """try to return user_id corresponding User object.
        This method is used by load_user callback function
        """
        if not user_id:
            return None
        try:
            with open(PROFILE_FILE) as f:
                user_profiles = json.load(f)
                for user_name, profile in user_profiles.iteritems():
                    if profile[1] == user_id:
                        return User(user_name)
        except:
            return None
        return None

    def change_passwd(self,old_password,new_password):
        if self.password_hash is None:
            return 'password hash has not been set'
        if check_password_hash(self.password_hash,old_password):
            new_password_hash=generate_password_hash(new_password)
            with open(PROFILE_FILE,'r+') as f:
                user_profiles=json.load(f)
                if self.username in user_profiles:
                    user_profiles[self.username][0]=new_password_hash
                    f.seek(0,os.SEEK_SET)
                    f.write(json.dumps(user_profiles))
                    return 'password changed'
                else:
                    return 'username false'
        else:
            return 'wrong old password'

    def add_user(self,username,password):
        if self.username is not 'admin':
            return 'only admin can add user'
        username = username
        password_hash = generate_password_hash(password)
        try:
            with open(PROFILE_FILE,'r+') as f:
                user_profiles = json.load(f)
                #f.truncate()
                if username in user_profiles:
                    return 'user existed'
                else:
                    id = unicode(uuid.uuid4())
                    user_profiles[username] = [password_hash,id]
                    f.seek(0,os.SEEK_SET)
                    f.write(json.dumps(user_profiles))
                    return 'add successfully'
        except Exception,e:
            print e

    def del_user(self,username):
        #only admin can del user
        if self.username is not 'admin':
            return 'only admin can del user'
        try:
            with open(PROFILE_FILE,'r+') as f:
                user_profiles = json.load(f)
                if username in user_profiles:
                    del user_profiles[username]
                    f.seek(0,os.SEEK_SET)
                    f.truncate()
                    f.seek(0,os.SEEK_SET)
                    f.write(json.dumps(user_profiles))
                    return 'del successfully'
                else:
                    return 'user is not existed'
        except Exception,e:
            print e


class Test(object):
    def add_user(self,username,password):
        username = username
        password_hash = generate_password_hash(password)
        try:
            with open(PROFILE_FILE,'r+') as f:
                user_profiles = json.load(f)
                #f.truncate()
                if username in user_profiles:
                    return 'user existed'
                else:
                    id = unicode(uuid.uuid4())
                    user_profiles[username] = [password_hash,id]
                    f.seek(0,os.SEEK_SET)
                    f.write(json.dumps(user_profiles))
                    return 'add successfully'
        except Exception,e:
            print e


if __name__=='__main__':
    atest=Test()
    print atest.add_user('admin','password')
    # print atest.add_user('conan','conan')
    # print atest.add_user('test','test')
    cur_user=User('admin')
    #print cur_user.change_passwd('new_password','password')
    print cur_user.add_user('test','test')
    print cur_user.add_user('test1','test1')
    print cur_user.add_user('test2','test2')
    print cur_user.del_user('test')
    #print cur_user.del_user('test')
    cur_user1=User('test1')
    print cur_user1.add_user('test3','test3')
    print cur_user1.del_user('test2')
