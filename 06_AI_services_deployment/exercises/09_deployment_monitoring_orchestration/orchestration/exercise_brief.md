Lo scopo dell'esercitazione di oggi è quello di utilizzare l'operatore
di branching (if/else) nel DAG di airflow che abbiamo realizzato assieme
nelle lezioni pratiche.

In particolare basterà verificare che la task load_dataset ritorno
effettivamente un percoso oppure, se dovesse ritornare un percorso
nullo, fai fallire il dag e lancia una eccezzione in python che spiega
quanto accaduto.
