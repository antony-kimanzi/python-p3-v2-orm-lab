from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    # 6. Setting year property with validation
    @property
    def year(self):
        return self._year
    # 6. Validating the year property
    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer")
        # 7. Added validation rule
        if value < 2000:
                raise ValueError("Year must be greater than or equal to 2000")
        self._year = value

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    # 2. immplemented save method
    def save(self):
        """Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of the new row.
        Save the object in the local dictionary using the row's primary key as the dictionary key."""
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self


    # 1. updated the create method
    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (year, summary, employee_id))
        CONN.commit()
        review = cls(year, summary, employee_id, CURSOR.lastrowid)
        cls.all[review.id] = review
        return review
    
    # 1. updated the instance_from_db method
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        review = cls(row[1], row[2], row[3], row[0])  # Ensure correct order of columns
        return review

    # 3. Update find_by_id method
    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance corresponding to the table row matching the specified primary key."""
        sql = """
            SELECT *
            FROM reviews
            WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        # If a matching row is found, return an instance of Review; otherwise, return None
        return cls.instance_from_db(row) if row else None

# 4.fixed the update method
    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

# 5. Fixed the delete method
    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute."""
        sql = """
            DELETE FROM reviews
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        
        # Remove the instance from the local dictionary
        if self.id in type(self).all:
            del type(self).all[self.id]
        
        # Reset the id attribute to None
        self.id = None



    # 1. updated the get all method
    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # 8. property for summary with validation
    
    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str):
            raise ValueError("Summary must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Summary cannot be empty")
        self._summary = value

    # 9. employee_id property with validation
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Employee ID must be an integer")
        # Check if the employee_id exists in the Employee table
        sql = "SELECT id FROM employees WHERE id = ?"
        result = CURSOR.execute(sql, (value,)).fetchone()
        if not result:
            raise ValueError(f"Employee ID {value} does not exist in the database")
        self._employee_id = value