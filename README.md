Data-migrator: a declarative data migrator
==========================================

Data-migrator is a simple data-migration package for python lovers. It is declarative language in django-esc style for table drive data transformations, set up as an open and extensive system.


Example
-------

Core of data-migrator is the unix pipe and filter paradigm to build data transformers. Source data is read from the database or some other source. It is piped to a filter written in data-migrator which emits for example SQL insert statements, after which this can be piped to a target client.

The most simple single datapump in mysql for example is written like:

```bash
$ mysqldump -u [uname] -p[pass] source_db table  | mysql target_db
```

In this case mysqldump will export the table as SQL statements and the new database will process them.
Now if you want to do something extra and repeatable with respect to the data, you could use all kinds of unix filtering with sed, awk, or other favorite poison.
Hard to imagine what Pythonista's would do especially if extra columns or something are needed. The basic packages are quite strong and one would setup something like:

```bash
$ mysql source_db -E 'select * from table' -B  | python my_filter.py | mysql target_db
```

With `my_filter.py` written as something like:

```python

import sys, csv

reader = csv.DictReader(sys.stdin)

for row in reader:
	print 'INSERT INTO `table` (a,b) VALUES ("%(a)s", %(b)s)' % row
```

To see the options for manipulation is left as an exercise to the reader, but do accept that as soon things become just a little more complex (think: splitting in two tables, column reverses, renaming of columns, mixing, joining, filtering, transforming), more declarative support is helpful. That is why we came up with `data-migrator`. One could simply replace this with:

```python
from data_migrator import models, transform
from data_migrator.emitters import MySQLEmitter

def parse_b(v):
	if v == 'B':
		return 'transformed_B'
	else:
		return v.lower()

class Result(models.Model):
	id   = models.IntField(pos=0) # keep id
	uuid = models.UUIDField()     # generate new uuid4 field
	# replace NULLs and trim
	a    = models.StringField(pos=1, default='NO_NULL', max_length=5, null='NULL', replace=lambda x:x.upper())
	# parse this field
	b    = models.StringField(pos=2, parse=parse_b, name='my_b')

	class Meta:
		table_name = 'new_table_name'

Result(a='my a', b='my b').save()

if __name__ == "__main__":
	transform.Transformer(models=[Result], emitter=MySQLEmitter).process()

	assert(len(Result.objects) > 1)
```

And have a nice self explaining transformer which will generate something like:

```SQL
# transformation for Result to table new_table_name
# input headers: id,a,b
# stats: in=10,dropped=0,out=10

SET SQL_SAFE_UPDATES = 0; -- you need this to delete without WHERE clause
DELETE FROM `new_table_name`;
ALTER TABLE `new_table_name` AUTO_INCREMENT = 1;

INSERT INTO `new_table_name` (`id`, `uuid`, `a`, `my_b`) VALUES (0, "ac7100b9-c9ad-4069-8ca5-8db1ebd36fa3", "MY A", "my b");
INSERT INTO `new_table_name` (`id`, `uuid`, `a`, `my_b`) VALUES (1, "38211712-0eb2-4433-b28f-e3fe33492e7a", "NO_NULL", "some value");
INSERT INTO `new_table_name` (`id`, `uuid`, `a`, `my_b`) VALUES (2, "a3478903-aed9-462c-8f47-7a89013bc6ea", "CHOPP", "transformed_B");

...
```

Overview
--------

Core in the data-migrator is the declarative definition of the target model. Indeed in a django-esc way. Columns of the target table are defined as fields and each field has many settings. The Field is a definition of what to perform scanning, transforming and emitting the record. Output is abstracted into an extensible set of output writers. The whole is controlled with a standard transformer engine.

The scan-emit loop is the basis the data-migrator. Once everything is setup, by default the transformer will read stdin and send every csv row to the model for scanning. Out of the box the fields define a scan loop:

1. **select** the specified column from the row.
1. **null** test if not allowed and replace by default.
1. **validate** the input (if validator is provided).
1. **parse** the input (if parser is provided).
1. **store** as native python value (aka NULL=>None).

Once all fields are parsed, the resulting object can be checked for `None` or uniqueness. It can be dropped or the filter can fail because of violations. This are all declarative settings on the Model through the Meta settings.
Otherwise the record is saved and (accessible by `Model.objects.all()`) is emitted. This is based on a dedicated emitter, like the MySQL `INSERT` statement generator. Emitting provides some of the following features:

1. **trim** if string and max_length is set (note the full string is stored in the intermediate object!).
1. **validate** the output (if output_validate is provided).
1. **replace** the value with some output string (if provided).
1. **write** in a dedicated format as dictated by the emitter.

For more details about the transformer, see the documentation and the examples.

Installation
------------

To install data-migrator, simply use pip:

	$ pip install data-migrator

Contribute
----------

If you'd like to contribute, simply fork `the repository`, commit your
changes to the **develop** branch (or branch off of it), and send a pull
request. Make sure you add yourself to AUTHORS.
