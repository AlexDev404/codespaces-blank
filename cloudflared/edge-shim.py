import asyncio, base64, os, sys
from urllib.parse import urlparse

LISTEN_PORT = 7844
TARGET = os.environ.get("EDGE_TARGET", "region1.v2.argotunnel.com:7844")
proxy = urlparse(os.environ["HTTPS_PROXY"])

async def pipe(r, w):
    try:
        while data := await r.read(65536):
            w.write(data)
            await w.drain()
    except Exception:
        pass
    finally:
        w.close()

async def handle(cr, cw):
    pr, pw = await asyncio.open_connection(proxy.hostname, proxy.port)
    hdr = f"CONNECT {TARGET} HTTP/1.1\r\nHost: {TARGET}\r\n"
    if proxy.username:
        cred = base64.b64encode(f"{proxy.username}:{proxy.password or ''}".encode()).decode()
        hdr += f"Proxy-Authorization: Basic {cred}\r\n"
    pw.write((hdr + "\r\n").encode())
    await pw.drain()
    status = await pr.readuntil(b"\r\n\r\n")
    if b" 200" not in status.split(b"\r\n")[0]:
        print("proxy refused:", status.split(b"\r\n")[0], file=sys.stderr)
        cw.close(); pw.close(); return
    await asyncio.gather(pipe(cr, pw), pipe(pr, cw))

async def main():
    srv = await asyncio.start_server(handle, "127.0.0.1", LISTEN_PORT)
    print(f"shim listening on 127.0.0.1:{LISTEN_PORT} -> {TARGET} via proxy", flush=True)
    await srv.serve_forever()

asyncio.run(main())
