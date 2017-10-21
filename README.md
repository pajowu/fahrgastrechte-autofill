# Fahrgastrechte Autofill [WIP]

Ein kleines Programm um das Fahrgastrechte-Formular der DB einfacher auszufüllen. Derzeit noch recht unfertig.

## Nutzung

Benötigt werden `npyscreen` und `fdfgen`, zB via

```
pip install -r requirements.txt
```

Danach einfach

```
python form.py
```

Dort das Formular ausfüllen (nicht benötigte Felder leer lassen) und dann auf der letzten Seite "Generate Form" betätigen.

Danach wird eine Datei `fahrgastrechte_[AKTUELLES DATUM].pdf` erstellt.

## Features

Nach dem Ausfüllen werden die Daten auch in der Datei `fields.json` gespeichert. Wenn diese in `defaults.json` umbenannt wird, werden die Daten beim Start des Programms eingelesen und als Stanard-Werte für die Felder genommen (zB nützlich für Kontodaten und Adresse)

