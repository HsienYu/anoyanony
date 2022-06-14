from pytwinkle import Twinkle


def callback(event, *args):
    if event == "registration_succeeded":
        uri, expires = args
        print("registration succeeded, uri: %s, expires in %s seconds" %
              (uri, expires))
        # The module keeps the session, you havent to register
        # mTP.call("0935932247")
    if event == "new_msg":
        msg = args[0]
        print("new_msg!: "+str(msg))

    if event == "incoming_call":
        call = args[0]
        print("call: "+str(call))

    if event == "cancelled_call":
        line = args[0]
        print("call cancelled, line: %s" % (line))

    if event == "answered_call":
        call = args[0]
        print("answered: %s" % (str(call)))

    if event == "ended_call":
        line = args[0]
        print("call ended, line: %s" % (line))


if __name__ == "__main__":
    mTP = Twinkle(callback)
    mTP.run()
