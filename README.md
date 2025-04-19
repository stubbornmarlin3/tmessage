# Terminal Messages

Terminal-based messaging application written in Python


## Methods

Here is a list of methods for the client/server and how they work.  

- ### Login

    Used to "login" to an account.  
    
    Essentially confirms username & password and return corresponding user data. The private key is also decrypted client-side using the password, ***which is the key to reading messages that are recieved.***  
    
    So even if someone were to gain access to the database or see data being sent back and forth, unless they know the password they do not have the private key to read messages.  

    The only data sent between the **Server** & **Client** is stuff anyone would be able to access anyways and holds no real value. This includes your username, hashes & salts for passwords, public key, and the encrypted private key.  

