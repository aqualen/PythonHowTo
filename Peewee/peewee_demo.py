"""
Simple examples of using peewee to interact with sqlite3 database.
"""

import os

import peewee as pw
from loguru import logger

# peewee_demo.db will be the physical db stored on local disk.
# we create a new instance every time the program runs, so delete any existing first...
file = 'peewee_demo.db'
if os.path.exists(file):
    os.remove(file)

db = pw.SqliteDatabase(file)


class BaseModel(pw.Model):
    logger.info("allows db to be defined or changed in just one place.")

    # wire up our business classes to the 'db' variable
    # thus, all model classes should inherit from BaseModel
    class Meta:
        database = db


class Person(BaseModel):
    """
         This class defines Person, which maintains details of someone
         for whom we want to research career to date.
     """
    logger.info("notice pewee data types, primary_key, optionality, constraints")

    person_name = pw.CharField(primary_key=True, max_length=30)
    lives_in_town = pw.CharField(max_length=40)
    nickname = pw.CharField(max_length=20, null=True)

    logger.info("We can add methods here, as well...")

    def show(self):
        logger.info(f"name: {self.person_name}, town: {self.lives_in_town}, nick: {self.nickname}")


class Job(BaseModel):
    job_name = pw.CharField(primary_key=True, max_length=30)
    start_date = pw.DateField(formats='YYYY-MM-DD')
    end_date = pw.DateField(formats='YYYY-MM-DD')

    salary = pw.DecimalField(max_digits=7, decimal_places=2)

    # there must be a Person entry for every person_employed...
    person_employed = pw.ForeignKeyField(Person, related_name='was_filled_by', null=False)


if __name__ == '__main__':
    print("Welcome to PythonHowTo: Peewee!")

    db.connect()
    db.execute_sql("PRAGMA foreign_keys = ON;")  # Required for sqlite
    db.create_tables([Job, Person])  # simply pass a list of classes we want tables for

    people = [("Andrew", "Sumner", "Andy"),
              ("Peter", "Seattle", None),
              ("Susan", "Boston", "Beannie"),
              # ("Fred", "Dallas", None), would resolve job insert failure
              ("Fat Boy", "New Orleans", "Slim"),
              ("Peter", "Seattle", "Spare Pete"),
              ]

    for person in people:
        try:
            with db.transaction():
                new_person = Person.create(
                        person_name=person[0], lives_in_town=person[1],
                        nickname=person[2], )
                new_person.save()
        except Exception as exception:
            logger.error(f"Error creating person {person[0]}")
            logger.exception(exception)
            logger.error("Note that the db protected the data!")

    for person in Person:
        person.show()

    jobs = [
            ("Analyst", "2017-02-01", "2019-07-33", 34.999, "Andrew"),
            ("Developer", "2017-02-01", "2019-07-31", 34.999, "Fred"),
            ]

    for job in jobs:
        try:
            with db.transaction():
                new_job = Job.create(
                        job_name=job[0],
                        start_date=job[1],
                        end_date=job[2],
                        salary=job[3],
                        person_employed=job[4],
                        )
                new_job.save()
        except Exception as exception:
            # missing person will throw "FOREIGN KEY constraint failed"
            logger.error(f"Error creating job for job = {job[0]}")
            logger.exception(exception)
            logger.error("")

    logger.info("Is there a better way to close the db???")
    db.close()

    logger.info("Now open peewee_demo.db in Database explorer!")
