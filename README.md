# Fahrgastrechte Autofill [WIP]

Ein kleines Programm um das Fahrgastrechte-Formular der DB einfacher auszufüllen.

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

### Daten aus ICE Portal importieren

Die Daten zum aktuellen Zug können automatisch aus dem ICE Portal importiert werden.
Dabei ist es sowohl möglich, die planmäßige Abfahrt als auch die tatsächliche und planmäßige Ankunft einzutragen.
Um die Abfahrtsdaten einzutragen, muss ggf der Startbahnhof mit dem Kommandozeilenparameter `--from-stop` oder `-f` und ggf der Zielbahnhof mit `--to-stop` oder `-t` angegeben werden.
Statt des vollen Namens des Bahnhofs kann auch die evaNr angegeben werden.

```
python3 fahrgastrechte.py --from-stop "Berlin Hbf" --to-stop "Leipzig Hbf"
```

## Nutzung: CLI

Benötigt werden `pdftk` sowie die Python-Module `npyscreen`, `requests`, `fdfgen` und `beautifulsoup4`, diese können zB via

```
pip3 install -r requirements.txt
```

installiert werden. `pdftk` sollte am besten aus den Paketquellen der jewieligen Distro installiert werden.

Danach einfach

```
python3 fahrgastrechte.py
```

## Nutzung: `tkinter`

Alternativ steht auch ein graphischeres Interface zur Verfügung.

Benötigt werden `pdftk` sowie die Python-Module `requests`, `fdfgen` und `beautifulsoup4`, diese können zB via

```
pip3 install -r requirements-tkinter.txt
```

installiert werden. `pdftk` sollte am besten aus den Paketquellen der jewieligen Distro installiert werden.

Danach einfach

```
python3 fahrgastrechte-tkinter.py
```

## Nutzung

Dort das Formular ausfüllen (nicht benötigte Felder leer lassen) und dann auf der letzten Seite "Generate Form" betätigen.

Danach wird eine Datei `fahrgastrechte_[AKTUELLER TIMESTAMP].pdf` erstellt.

## Nutzung: CLI mit Docker

Um die Anwendung in einem eigenen Container laufen zu lassen, in dem alle Abhängigkeiten automatisch installiert sind, folgende Kommandos verwenden:

```
docker build -t fahrgastrechte-app .
docker run -it --rm -v $(pwd):/usr/src/app -w /usr/src/app fahrgastrechte-app
```

# Copyright

Die `Scrollable`-Klasse in fahrgastrechte_tkinter.py basiert auf <https://stackoverflow.com/a/47985165>.
