# WageWise

Applicazione desktop per la gestione consapevole dello stipendio mensile.  
Costruita con **Python 3.11** e **PyQt6** — funziona completamente offline, senza account né cloud.

---

## Requisiti di sistema

| Componente | Versione minima |
|---|---|
| Python | 3.11 |
| pip | qualsiasi versione recente |
| Sistema operativo | Windows 10+, macOS 12+, Linux (distro moderna) |

---

## Primo avvio (sviluppo)

### 1. Clona o scarica il progetto

```bash
git clone <url-repository>
cd WageWise
```

### 2. Crea il virtual environment

```bash
python -m venv venv
```

### 3. Attiva il virtual environment

**Windows:**
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 5. Avvia l'applicazione

```bash
py main.py
```

Al primo avvio, l'app crea automaticamente la cartella dati con i file JSON di default:

| Sistema operativo | Percorso dati |
|---|---|
| Windows | `%LOCALAPPDATA%\WageWise\data\` |
| macOS | `~/Library/Application Support/WageWise/data/` |
| Linux | `~/.local/share/WageWise/data/` |

---

## Struttura del progetto

```
WageWise/
├── main.py                  → Entry point
├── requirements.txt         → Dipendenze Python
├── assets/
│   └── style.qss            → Stylesheet globale Qt
├── core/
│   ├── app_state.py         → Stato globale singleton (AppState)
│   ├── period.py            → Logica calcolo periodi stipendiali
│   └── validators.py        → Validazioni input
├── models/
│   ├── storage.py           → Layer I/O JSON
│   ├── settings_model.py    → Impostazioni app
│   ├── model_model.py       → Modelli di distribuzione budget
│   ├── salary_model.py      → Storico stipendi
│   └── expense_model.py     → Registro spese
├── views/
│   ├── main_window.py       → Finestra principale
│   ├── dashboard_view.py    → Pagina 1: Dashboard
│   ├── expenses_view.py     → Pagina 2: Registro Spese
│   └── history_view.py      → Pagina 3: Storico
├── controllers/
│   ├── dashboard_ctrl.py    → Logica Pagina 1
│   ├── expenses_ctrl.py     → Logica Pagina 2
│   └── history_ctrl.py      → Logica Pagina 3
└── components/
    ├── sidebar.py           → Barra di navigazione laterale
    ├── category_card.py     → Card categoria con barra residuo
    ├── budget_progress_bar.py → Barra verde/giallo/rosso
    ├── pie_chart.py         → Grafico a torta (QtCharts)
    ├── bar_chart.py         → Grafico a barre raggruppate (QtCharts)
    ├── line_chart.py        → Grafico a linee (QtCharts)
    └── alert_banner.py      → Banner avvisi inline
```

---

## Build eseguibile (distribuzione)

Per generare un `.exe` standalone (Windows):

```bash
pyinstaller --onefile --windowed --name "WageWise" --icon=assets/icon.ico --add-data "assets;assets" main.py
```

L'eseguibile viene generato in `dist/WageWise.exe` e può essere distribuito direttamente senza installazione di Python.

> **Nota:** su macOS/Linux il separatore in `--add-data` è `:` invece di `;`.

---

## Dipendenze

| Pacchetto | Uso |
|---|---|
| `PyQt6` | Framework UI |
| `PyQt6-Charts` | Grafici a torta, barre e linee |
| `pyinstaller` | Build eseguibile standalone |

Nessuna dipendenza esterna aggiuntiva. La libreria standard Python (`json`, `uuid`, `datetime`, `pathlib`, `calendar`) copre tutto il resto.

---

## Dati locali

I file JSON nella cartella dati **non vengono inclusi nel repository** (`.gitignore`).  
La struttura viene ricreata automaticamente ad ogni primo avvio su una nuova macchina.

Per fare un backup manuale dei propri dati, è sufficiente copiare l'intera cartella `WageWise/data/` dal percorso di sistema.
