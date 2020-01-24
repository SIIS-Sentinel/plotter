# Install pscopg2

Make sure OpenSSL is install with Brew. Type `export LDFLAGS="-L/usr/local/opt/openssl/lib"`, and then install `pyscopg2` with `pip` or `pipenv`.

# Allow remote connection to PostgreSQL

* Edit the `/etc/postgresql/11/main/postgresql.conf` file to change `listen_addresses` to be `*`
* Edit `/etc/postgresql/11/main/pg_hba.conf` to add `host all all md5` at the end
* Restart the server
* Make sure to use the actual IP of the server to connect to it (and not a `.local` address)