This is the main page that will be running on the resturant's computer.
Pages in this version:
1. Home page --> Just see all the unhandled requests
2. Settings page
    |-> Wifi settings
    |-> Menu setting page link
    |-> My Subscription
    |-> Password
    |-> Org name/id
    |-> Org allowed --> List of phone numbers supported  (V2)
3. Setup page
    |-> Setup SmartPad: Setup the table id and wifi details to the worker + unique code (or may be get the ip addresses)
    |-> Grps: --> grps + table id


Backend
1. Setup the smartpad
2. Register listerner request from waiter's app --> JWT based auth --> Subscription request from a grp.  (V2)
3. Receive the signals from the smartPad --> Validate that is it correct --> Update the state --> Assign it to grp --> Forward the state to subscribers.
