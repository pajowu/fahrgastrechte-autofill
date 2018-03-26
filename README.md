# Fahrgastrechte Autofill [WIP]

Ein kleines Programm um das Fahrgastrechte-Formular der DB einfacher auszufüllen. Derzeit noch recht unfertig.

## Nutzung

Benötigt werden `npyscreen` und `fdfgen`, zB via

```
pip3 install -r requirements.txt
```

Danach einfach

```
python3 fahrgastrechte.py
```

Dort das Formular ausfüllen (nicht benötigte Felder leer lassen) und dann auf der letzten Seite "Generate Form" betätigen.

Danach wird eine Datei `fahrgastrechte_[AKTUELLES DATUM].pdf` erstellt.

### Nutzung mit Docker

Um die Anwendung in einem eigenen Container laufen zu lassen, in dem alle Abhängigkeiten automatisch installiert sind, folgende Kommandos verwenden:

```
docker build -t fahrgastrechte-app .
docker run -it --rm -v $(pwd):/usr/src/app -w /usr/src/app fahrgastrechte-app
```

## Features

### Stammdaten speichern

Nach dem Ausfüllen werden die Daten auch in der Datei `fields.json` gespeichert.
Wenn diese in `defaults.json` umbenannt wird, werden die Daten beim Start des Programms eingelesen und als Stanard-Werte für die Felder genommen (zB nützlich für Kontodaten und Adresse)

### Daten aus Buchung importieren

Daten aus Buchung können importiert werden.
Dafür muss die Buchungsnummer und der Nachname mit den Kommandozeilenparametern `--auftragsnummer` und `--nachname` angegeben werden.

```
python3 fahrgastrechte.py --auftragsnummer ABC123 --nachname Mustermensch
```
