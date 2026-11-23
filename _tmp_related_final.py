import json
import subprocess
import time
import urllib.request

RC = (
    r"C:\Users\Jim\AppData\Local\Microsoft\WinGet\Packages"
    r"\taizod1024.redis-windows-fork_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\Redis-8.10.2-Windows-x64-msys2\redis-cli.exe"
)
LOG = (
    r"C:\Users\Jim\AppData\Local\Temp\zcode-bash-TQILCI"
    r"\sess_84fb7e89-bd37-401d-bd46-7ad46b41f2d1"
    r"\call_85a9bf7744b6464a98989821-stdout.log"
)


def cli(*args):
    out = subprocess.run([RC, *args], capture_output=True, text=True)
    return out.stdout.strip()


def detail(nid):
    with urllib.request.urlopen(f"http://127.0.0.1:8049/api/news/detail?id={nid}") as r:
        d = json.loads(r.read())
    data = d.get("data") or {}
    related = data.get("relatedNews") or []
    first = related[0]["id"] if related else None
    return f"views={data.get('views')} related_count={len(related)} first_related={first}"


def news_query_count():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         f"(Select-String -Path '{LOG}' -Pattern 'FROM news ').Count"],
        capture_output=True, text=True)
    return out.stdout.strip()


cli("FLUSHDB")
print("1st id=1:", detail(1), "| news queries:", news_query_count())
print("keys:", cli("KEYS", "*"))
time.sleep(0.5)
print("2nd id=1:", detail(1), "| news queries:", news_query_count())
time.sleep(0.5)
print("3rd id=1:", detail(1), "| news queries:", news_query_count())
print("keys:", cli("KEYS", "*"))
print("TTL news:related:1:1:", cli("TTL", "news:related:1:1"))
