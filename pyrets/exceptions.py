#encoding:utf-8


class RetsException(Exception):
    def __init__(self, reply_code, reply_text):
        self.reply_code = reply_code
        self.reply_text = reply_text


class RetsNotLoginException(RetsException):
    def __init__(self, reply_text):
        RetsException.__init__(self, reply_code=20037, reply_text)


class RetsNotSupportException(RetsException):
    def __init__(self, reply_text):
        RetsException.__init__(self, reply_code=20203, reply_text)



exception_mapping = {
    "20037": RetsNotLoginException,
    "20203": RetsNotSupportException
}

def raise_rets_exception(reply_code, reply_text):
    if reply_code == "0":
        return
    if reply_code in exception_mapping:
        raise exception_mapping[reply_code](reply_text)
    raise RetsException(reply_code, reply_text)