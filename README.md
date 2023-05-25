# Terminal Messages

Terminal-based messaging application written in Python


## Methods

Here is a list of methods for the client/server and how they work.  

- ### Login

    Used to "login" to an account.  
    
    Essentially confirms username & password and return corresponding user data. The private key is also decrypted client-side using the password, ***which is the key to reading messages that are recieved.***  
    
    So even if someone were to gain access to the database or see data being sent back and forth, unless they know the password they do not have the private key to read messages.  

    The only data sent between the **Server** & **Client** is stuff anyone would be able to access anyways and holds no real value. This includes your username, hashes & salts for passwords, public key, and the encrypted private key.  

    Here is the logic behind it:

    > **Client:** Connect to server & send login command *` login <username> `* & await response.

    > **Server:** Connect to *MySQL Database* & fetch *`stored_hash`* & *`stored_salt`* where *`username = <username>`*.
    >- If nothing is returned, the user does not exist. This will stop the method and close the connection, telling the client that the username does not exist.  
    >  
    > Send *`stored_salt`* to **Client** & await response.

    > **Client:** Hash *`password`* using *`stored_salt`* from server. Send *`client_hash`* to **Server** & await response.

    > **Server:** Confirm *`client_hash`* matches *`stored_hash`*.
    >- If they don't match, the password was incorrect. This will stop the method and close the connection, telling the client that the password was wrong.  
    >  
    > Fetch *`display_name`*, *`public_key`*, & *`encrypted_private_key`* from database. Send to **Client** & close connection.

    > **Client:** Generate *`fernet_key`* using hash from *`password`* & *`client_hash`*. This will only be the correct key if the password is correct. Decrypt *`encrypted_private_key`* & return a *`User`* object with the corresposing attributes.

- ### Create Account

    > Here is where I will explain the create account method

