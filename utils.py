import requests


def email(user_id, otp):
    jsonInput = {
        "from": "Admin <admin@loopme.in>",
        "to": user_id,
        "subject": "Welcome to LoopMe ",
        "html": "your otp is <b>{}</b>".format(otp)
    }
    res = requests.post('https://winmail.herokuapp.com/mail', None, jsonInput)
    print res.text


if __name__ == '__main__':
    email('winster.jose@amadeus.com', '123456')