import os
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import close_all_sessions

from models import Base, User, Product, Price, user_tracked_products_table

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


recreate_database()
s = Session()

user = User(name="Santiago")
polera = Product(name="polera legacy", url="www.paris.cl", users=[user])
audi = Product(name="audifonos", url="www.paris.cl/audi", users=[user])

s.add(user)
s.add(polera)
s.add(audi)

s.commit()

new_price = Price(product_id=audi.id, value=199, datetime=datetime.now())
newest_price = Price(product_id=audi.id, value=100)
s.add(new_price)
s.add(newest_price)

s.commit()

# # user = s.query(User).first()
# # s.execute(user_tracked_products_table.insert().values([user.id, polera.id]))
# # user.tracked_products.append(polera)
# # s.commit()

# print(user.name, user.products)

# s.close()

close_all_sessions()
