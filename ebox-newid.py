#!/usr/bin/python2.7

import sqlite3, os, sys


# Extract Keys from a given file and row

def findKey(fileList, row):
    newKeyTemp = fileList[row].replace(' ', '')
    newKeyTemp2 = newKeyTemp.replace('"', '')

    if 'publicKey' in newKeyTemp2:
        newKeyTemp3 = newKeyTemp2.replace('publicKey:', '')
    if 'privateKey' in newKeyTemp2:
        newKeyTemp3 = newKeyTemp2.replace('privateKey:', '')
    if 'ipv6' in newKeyTemp2:
        newKeyTemp3 = newKeyTemp2.replace('ipv6:', '')
    
    newKeyTemp4 = newKeyTemp3.replace('\n', '')
    newKey = newKeyTemp4.replace(',', '')
    #print("newKey return value ", newKey)
    return newKey


print("""\nYour actual ID will be renewed. Dont forget to inform your inbound Connections.\nIts stongly advised to create a Backup of the System first!\n
After generating and assigning the new ID you will get disconnected for ca. 30 Min.\nJust wait, the Connection will then be established with your new Identity.\n
If something goes wrong consider renaming the backup '/box/settings.sqlite.sosbackup'\nto '/box/settings.sqlite' and replace the existing one.\n""")


choice = raw_input("Do you want to continue? y/N ")

if choice == 'N' or choice == '': 
    print("Quit...")
    sys.exit()

elif choice == 'y':
    # read actual privateKey, publicKey and IPv6 in settings.sqlite 
    try:        
        os.system("cp -a /box/settings.sqlite /box/settings.sqlite.sosbackup")
        print("Reading Database 'settings.sqlite...'")
        db = sqlite3.connect("/box/settings.sqlite")
                
    except:
        print("Failed to read Database 'settings.sqlite'!\nQuit")
        sys.exit()

    c = db.cursor()

    print("Creating new ID... ")
 
    #Reading the actual values and assigning to variables
    #Actual Public Key
    
    c.execute("SELECT value from app_option WHERE key='private_key'")
    i = list(c)
    rec = i[0]
    actualPrivateKey = rec[0]
    

    #Actual Private Key
    c.execute("SELECT value from app_option WHERE key='public_key'")
    i = list(c)
    rec = i[0]
    actualPublicKey = rec[0]

    #Actual IPv6 Address
    c.execute("SELECT value from app_option WHERE key='ipv6'")
    i = list(c)    
    rec = i[0]
    actualIPv6Key = rec[0]
  

    # Create a new cjdroute.conf file with new privateKey,publicKey, IPv6
    try:
        os.system("/usr/sbin/cjdroute --genconf > /box/newid_tmp")
        os.system("chmod 775 /box/newid_tmp")
        newIdTmpFile = open("/box/newid_tmp")
        fileList = newIdTmpFile.readlines()

        # New PublicKey
        newPublicKey = findKey(fileList, 6)
        #print("NewPublicKey", newPublicKey)
                
        # New PrivateKey
        newPrivateKey = findKey(fileList, 3)
        #print("newPrivateKey", newPrivateKey)
    
        # New IPv6
        newIPv6Key = findKey(fileList, 7)
        #print("newIPv6", newIPv6Key)
        
    except:
        print("Creation of new ID failed! Please check your installation.")
        sys.exit()

    print(" ")
    print("------------------------------------------------------------------------------------")
    print("Actual Public Key: " + actualPublicKey)
    print("New Public Key:    " + newPublicKey)
    print("------------------------------------------------------------------------------------")
    print("Actual Private Key: " + actualPrivateKey)
    print("New Private Key:    " + newPrivateKey)
    print("------------------------------------------------------------------------------------")
    print("Actual IPv6 Address: " + actualIPv6Key)
    print("New IPv6 Address:    " + newIPv6Key)
    print("------------------------------------------------------------------------------------")
    
    # Inserting new values into the database 'settings.sqlite'
    dbUpdatePublicKey = "UPDATE app_option SET value=" + "'" + newPublicKey + "'" + " WHERE key=" + "'" + "public_key" + "'" + ""
    c.execute(dbUpdatePublicKey)
    dbUpdatePrivateKey = "UPDATE app_option SET value=" + "'" + newPrivateKey + "'" + " WHERE key=" + "'" + "private_key" + "'" + ""
    c.execute(dbUpdatePrivateKey)
    dbUpdateIPv6Key = "UPDATE app_option SET value=" + "'" + newIPv6Key + "'" + " WHERE key=" + "'" + "ipv6" + "'" + ""
    c.execute(dbUpdateIPv6Key)

    # Write the DB
    db.commit()
    # Close cursor and DB
    c.close()
    db.close()

    # Init with new ID
    os.system("cfengine-apply")
    print("")
    print("DONE!")

    try:
        newIdTmpFile.close()
        os.system("rm -rf /box/newid_tmp")
    except:
        print("Temporary config 'newid_tmp' not deleted. Delete it manually!")
    
else:
    print("Input not valid.")
    sys.exit()
