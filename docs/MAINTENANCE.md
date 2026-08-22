# Maintenance

## Restart stack

```bash
docker compose restart
```

## Update stack

```bash
docker compose pull
docker compose up -d
```

## Backup Honcho memory

```bash
tar czf honcho-backup.tgz /opt/autostack/honcho
```
