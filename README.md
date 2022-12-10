# ypareo-api

## Build

```bash
docker build -t ypareo-api .
```

## Run

```bash
docker run -d -e YPAREO_USER=your_username -e YPAREO_PASS=your_password -e YPAREO_DOMAIN=your_domain -e DISCORD_WEBHOOK=your_webhook ypareo-api
```
