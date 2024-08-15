# Vaultwarden

### DATABASE_URL

When Use Vaultwarden with the mariadb database backend, the DATABASE_URL must be set, 
 (i.e. DATABASE_URL='mysql://<user>:<password>@mysql/vaultwarden[?ssl_mode=(disabled|required|preferred)&ssl_ca=/path/to/cart.(crt|pem)]').

and If your password contains special characters, you will need to use percentage encoding.
you can find on ![Wikipedia page for percent encoding](https://en.wikipedia.org/wiki/Percent-encoding#Percent-encoding_reserved_characters) 

### ADMIN_TOKEN

the ADMIN_TOKEN is used to access your administration page,after set this, the page will be available in the /admin subdirectory.

### HTTPS 

In order to ensure the proper operation of Vaultwarden, enabling HTTPS is very necessary, because the Bitwarden Web Vault uses a Web encryption API that most browsers only provide in the HTTPS environment.


## FAQ
