# doctocare-userUpdate
Contains the updateUser application, used to update the DocteGestio database.

## Dependencies
To run this program, you'll need to download and install some python modules.
To do that, open a console terminal and simply run the following commands.
First and foremost, install and upgrade the pip module manager:
* On MacOS & Linux :
```sh
sudo pip install -U pip
```
* On Windows :
```sh
python -m pip install -U pip
```

Install the psycopg2 package, to connect and use the database
``` sh
sudo pip install psycopg2
```
Install the oauth2client, to use the credentials from the Google Admin API
```sh
sudo pip install oauth2client
```

For more informations, please visit :
[Install pip]

[Install pip]:https://pip.pypa.io/en/stable/installing/

## Clone this repository
First, clone this repository to a local directory of your choice.
* In order to do that, open a terminal, then move to the directory of your choice using the 'cd' command :
```sh
cd [PATH-TO-THE-REPOSITORY]
```
* Then run :
```sh
git clone https://github.com/TChanet/doctocare-userUpdate.git
```

## Run the program
To run the program, open a terminal and move to the repository using the 'cd' command.
```sh
cd [PATH-TO-THE-REPOSITORY]/doctocare-userUpdate
```
Finally, simply run the following command :
``` sh
python updateUsers.py
```
Congratulations, your database is now up-to-date !
## Author
Thierry Chanet (DocteGestio)
