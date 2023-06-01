# py-rocketchat
Should be a collection of useful scripts

For now only includes rc_ownership_transfer.py
Which will transfer ownership of any owned users from one to another by accessing directly to the database.

1. Make sure to install the following packages:

        python -m pip install 'pymongo[srv]' python-dotenv

2. Set .env variables as per your environments and what you need to do.

        DB_URI=mongodb://mongodb:27017/?replicaSet=rs0
        RC_DB=rocketchat
        OLD_USER=rui
        NEW_USER=demo

2.1. Change the DB_URI to point to your mongo database so make sure its available for connection.

2.2. Set the name of your rocketchat database

2.3. Set the old user you want to transfer current room ownerships

2.4. Set the new user that should receive the transferred ownerships
