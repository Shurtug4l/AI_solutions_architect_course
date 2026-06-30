Nell'utilizzo delle github actions ti sarà sicuramente utile la
possibilità di utilizzare delle passwords, api keys ecc.

Lo scopo dell'esercitazione è quello di creare una github action che
altro non fa che leggere un secret e "provare" a stamparlo nei log della
pipeline; dico provare poiché github di default impedisce di stampare
secret e quindi stamperà al suo posto degli asterischi (redacted).
