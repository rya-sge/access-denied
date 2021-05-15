Générer une clé prévie RSA, par exemple pour chiffrer

openssl genrsa -out private.pem 2048



openssl rsa -in private.pem -pubout > public.pem



https://gist.github.com/Holger-Will/3edeea6855f1d69a5368871bce5ea926



Ex :

