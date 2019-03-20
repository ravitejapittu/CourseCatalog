from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Course, Base, MenuItem, User

engine = create_engine('sqlite:///coursedata.db')
"""Bind the engine to the metadata of the Base class so that the
declaratives can be accessed through a DBSession instance"""
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
"""A DBSession() instance establishes all conversations with the database
 and represents a "staging zone" for all the objects loaded into the
 database session object. Any change made against the objects in the
 session won't be persisted into the database until you call
 session.commit(). If you're not happy about the changes, you can
 revert all of them back to the last commit by calling
 session.rollback()"""
session = DBSession()
"""Create First User"""
User1 = User(name="Ravi Teja", email="ravitejapittu@gmail.com",
             picture='https://lh3.googleusercontent.com/'
             '-ktSKbvcydmA/AAAAAAAAAAI/'
             'AAAAAAAAY78/1Hr7lhAKhTg/s60-p-rw-no-il/photo.jpg')
session.add(User1)
session.commit()

"""Menu for Java"""
course1 = Course(user_id=1, name="Java")
session.add(course1)
session.commit()

menuItem1 = MenuItem(user_id=1, name="Core Java",
                     description='''Our core Java programming tutorial '
                     'is designed for students and working professionals.'
                     'Java is an object-oriented, class-based, concurrent,'
                     'secured and general-purpose '
                     'computer-programming language.'
                     ' It is a widely used robust technology.''',
                     price="1000",
                     picture="https://tinyurl.com/yyqe24ld",
                     course=course1)
session.add(menuItem1)
session.commit()

menuItem1 = MenuItem(user_id=1, name="Spring",
                     description='''This spring tutorial provides in-depth'
                     ' concepts of Spring Framework with'
                     ' simplified examples. '
                     'It was developed by Rod Johnson in 2003.'
                     ' Spring framework makes the easy development'
                     ' of JavaEE application. It is helpful'
                     ' for beginners and experienced persons.''',
                     price="2000",
                     picture="https://tinyurl.com/y4y6m7ub",
                     course=course1)
session.add(menuItem1)
session.commit()

menuItem1 = MenuItem(user_id=1, name="Spring Boot",
                     description='''Spring Boot Tutorial provides basic'
                     ' and advanced concepts of Spring Framework.'
                     ' Our Spring Boot Tutorial is designed'
                     ' for beginners and professionals both.'
                     'Spring Boot is a Spring module'
                     ' which provides RAD (Rapid Application Development)'
                     ' feature to Spring framework.'
                     'Our Spring Boot Tutorial includes'
                     ' all topics of Spring Boot such as features,'
                     ' project, maven project, starter project wizard,'
                     ' spring Initializr, cli, application, annotations,'
                     ' dm, properties, starters, actuator, jpa, jdbc etc.''',
                     price="2500",
                     picture="https://tinyurl.com/y2436bg7",
                     course=course1)
session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="JPA",
                     description='''JPA tutorial provides basic and advanced'
                     ' concepts of Java Persistence API.'
                     ' Our JPA tutorial is designed'
                     ' for beginners and professionals.'
                     'JPA is just a specification'
                     ' that facilitates object-relational'
                     ' mapping to manage relational'
                     ' data in Java applications.'
                     ' It provides a platform to work'
                     ' directly with objects instead of'
                     ' using SQL statements.''',
                     price="2000",
                     picture="https://tinyurl.com/y2wx2dn9",
                     course=course1)
session.add(menuItem2)
session.commit()

"""Menu for Python"""
course2 = Course(user_id=1, name="Python")
session.add(course2)
session.commit()

menuItem1 = MenuItem(user_id=1, name="Python",
                     description='''Python tutorial provides basic and
                     advanced concepts of Python.
                     Our Python tutorial is designed
                     for beginners and professionals.
                     Python is a simple, easy to learn,
                     powerful, high level and
                     object-oriented programming language.
                     Python is an interpreted scripting
                     language also. Guido Van Rossum
                     is known as the founder of
                     python programming. Our Python
                     tutorial includes all topics
                     of Python Programming such as
                     installation, control statements,
                     Strings, Lists, Tuples, Dictionary,
                     Modules, Exceptions, Date and Time,
                     File I/O, Programs,
                     etc. There are also given Python
                     interview questions to help you
                     better understand the Python Programming.''',
                     price="1000",
                     picture="https://tinyurl.com/y523styd",
                     course=course2)
session.add(menuItem1)
session.commit()


menuItem1 = MenuItem(user_id=1, name="Python with Django",
                     description='''Django is a Python-based free
                     and open-source web framework,
                     which follows the model-view-template
                     architectural pattern. It is maintained
                     by the Django Software Foundation,
                     an independent organization established
                     as a 501 non-profit. Django's primary
                     goal is to ease the creation of complex,
                     database-driven websites.''',
                     price="2500",
                     picture="https://tinyurl.com/yyu4mawe",
                     course=course2)
session.add(menuItem1)
session.commit()

menuItem1 = MenuItem(user_id=1, name="Python with Flask",
                     description='''Flask is a micro web framework
                     written in Python. It is classified
                     as a microframework because
                     it does not require particular
                     tools or libraries.
                     It has no database abstraction
                     layer, form validation, or any
                     other components where
                     pre-existing third-party libraries
                     provide common functions.''',
                     price="3000",
                     picture="https://tinyurl.com/y3dvr4q9",
                     course=course2)
session.add(menuItem1)
session.commit()

"""Menu for Cyber Security"""
course3 = Course(user_id=1, name="Cyber Security")
session.add(course3)
session.commit()

menuItem1 = MenuItem(user_id=1, name="Cyber Security",
                     description='''Cyber Security tutorial provides
                     basic and advanced concepts of Cyber
                     Security technology. Our Cyber Security
                     tutorial is designed for beginners
                     and professionals.
                     Our Cyber Security Tutorial
                     includes all topics of
                     Cyber Security such as
                     what is Cyber Security,
                     cyber security goals,
                     types of cyber attacks,
                     types of cyber attackers,
                     technology, e-commerce,
                     policies, digital signature,
                     cyber security tools,
                     security risk analysis,
                     challenges etc.''',
                     price="500",
                     picture="https://tinyurl.com/yxus7kuu",
                     course=course3)
session.add(menuItem1)
session.commit()

print("added menu items!")
