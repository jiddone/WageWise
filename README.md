# WageWise

## Installazione dipendenze

Da root del progetto:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Avvio applicazione

Da root del progetto:

```powershell
.\start.ps1
```

In alternativa, senza script di supporto:

```powershell
.\venv\Scripts\python.exe .\main.py
```

Il virtual environment corretto e' `venv`. `.venv` non esiste piu'.

Se vuoi attivarlo manualmente in PowerShell, il percorso corretto e' questo:

```powershell
& .\venv\Scripts\Activate.ps1
```