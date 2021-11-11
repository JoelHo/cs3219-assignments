from main import db
from main import Permission

db.create_all()

# Permissions as bits, i.e.
# CAN_READ = 1
# CAN_WRITE = 2
# CAN_DELETE = 4
# CAN_ADMIN = 8

db.session.add(Permission(bit=1, name='CAN_READ'))
db.session.add(Permission(bit=2, name='CAN_WRITE'))
db.session.add(Permission(bit=4, name='CAN_DELETE'))
db.session.add(Permission(bit=8, name='CAN_ADMIN'))
db.session.commit()
