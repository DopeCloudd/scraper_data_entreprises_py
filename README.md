## Lancer le workflow

```bash
python main.py \
  --input-format json \
  --input-file data/etablissements-20251215.json \
  --output-format json \
  --output-file output.json
```

## Accélérer le scraping

- `--workers N` lance N navigateurs Chrome en parallèle (1 = séquentiel).
- Ajoute `--headless` pour masquer les fenêtres Chrome lorsque plusieurs workers tournent.
