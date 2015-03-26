#-*-coding:utf8;-*-

def is_owner(request, user_id):
    try:
        if request.myuser.id == int(user_id):
            return True
        else:
            return False
    except:
        return False
    