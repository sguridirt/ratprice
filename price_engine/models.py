class Product(object):
    def __init__(self, doc_id, name, url):
        self.doc_id = doc_id
        self.name = name
        self.url = url

    @staticmethod
    def from_dict(doc_id, source):
        return Product(doc_id, source["name"], source["URL"])

    def to_dict(self):
        return {"name": self.name, "URL": self.url}

    def __repr__(self):
        return f"Product(doc_id={self.doc_id}, name={self.name}, url={self.url})"


class Price(object):
    def __init__(self, number, datetime):
        self.number = number
        self.datetime = datetime

    @staticmethod
    def from_dict(source):
        return Price(source["number"], source["datetime"])

    def to_dict(self):
        return {"number": self.number, "datetime": self.datetime}

    def __repr__(self):
        return f"Price(number={self.number}, datetime={self.datetime})"


class User(object):
    def __init__(self, name, email, telegramId):
        self.name = name
        self.email = email
        self.telegramId = telegramId

    @staticmethod
    def from_dict(source):
        return User(source["name"], source["email"], source["telegramId"])

    def to_dict(self):
        return {"name": self.name, "email": self.email, "telegramId": self.telegramId}

    def __repr__(self):
        return (
            f"User(name={self.name}, email={self.email}, telegramId={self.telegramId})"
        )
