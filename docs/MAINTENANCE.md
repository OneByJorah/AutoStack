# Maintenance

## Restart stack

```bash
docker compose restart
```

## Update images

```bash
docker compose pull
docker compose up -d
```

## Backup Honcho memory

```bash
tar czf honcho-backup.tgz /home/j1admin/docker/j1-stack-deploy/honcho
```
