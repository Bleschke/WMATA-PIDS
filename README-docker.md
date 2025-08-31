
# WMATA PIDS — Docker

## Build
```bash
docker build -t wmata-pids:latest .
```

## Run
```bash
# Option A: pass env var directly
docker run --rm -it -p 5000:5000 -e WMATA_API_KEY=YOUR_KEY wmata-pids:latest

# Option B: use a local .env file in this folder (also used by the app UI if you choose persist)
echo 'WMATA_API_KEY="YOUR_KEY"' > .env
docker compose up --build
```
Open: http://localhost:5000/?station=F02&tv=1
