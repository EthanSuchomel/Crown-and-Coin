# Not shipped: a tiny stand-in for Supabase's REST API (the games table only), for testing online play.
import json, sys, re, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qsl, unquote
rows = {}; lock = threading.Lock(); log = open(sys.argv[2], 'w') if len(sys.argv) > 2 else None
def match(row, k, v):
    if k == 'or':
        parts = v.strip('()').split(',')
        return any(match(row, *p.split('.', 1)) for p in parts)
    op, val = v.split('.', 1)
    if op == 'eq': return str(row.get(k)) == val
    if op == 'is' and val == 'null': return row.get(k) is None
    raise Exception('op ' + op)
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _q(self):
        u = urlsplit(self.path); assert u.path == '/rest/v1/games', u.path
        q = parse_qsl(u.query, keep_blank_values=True)
        f = [(k, v) for k, v in q if k not in ('select', 'order', 'limit')]
        sel = dict(q).get('select', '*')
        return f, sel, dict(q)
    def _send(self, code, data=None):
        b = json.dumps(data).encode() if data is not None else b''
        self.send_response(code); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def _body(self):
        n = int(self.headers.get('Content-Length', 0)); return json.loads(self.rfile.read(n) or b'null')
    def _pick(self, r, sel): return dict(r) if sel == '*' else {k: r.get(k) for k in sel.split(',')}
    def _auth(self):
        if self.headers.get('apikey') != 'testkey': self._send(401, {'message': 'no key'}); return False
        return True
    def _l(self, m): 
        if log: log.write(m + ' ' + unquote(self.path)[:110] + '\n'); log.flush()
    def do_GET(self):
        if not self._auth(): return
        f, sel, q = self._q(); self._l('GET')
        with lock:
            out = [self._pick(r, sel) for r in rows.values() if all(match(r, k, v) for k, v in f)]
        if 'order' in q: out.sort(key=lambda r: r.get('updated') or 0, reverse=True)
        self._send(200, out)
    def do_POST(self):
        if not self._auth(): return
        d = self._body(); self._l('POST')
        with lock:
            if d['code'] in rows: return self._send(409, {'message': 'duplicate'})
            r = {'guest': None, 'winner': None}; r.update(d); rows[d['code']] = r
        self._send(201, [r])
    def do_PATCH(self):
        if not self._auth(): return
        f, sel, q = self._q(); d = self._body(); self._l('PATCH rev=%s cur=%s' % (d.get('rev'), d.get('cur')))
        with lock:
            hit = [r for r in rows.values() if all(match(r, k, v) for k, v in f)]
            for r in hit: r.update(d)
            out = [dict(r) for r in hit]
        self._send(200, out)
    def do_DELETE(self):
        if not self._auth(): return
        f, sel, q = self._q(); self._l('DELETE')
        with lock:
            for c in [c for c, r in rows.items() if all(match(r, k, v) for k, v in f)]: del rows[c]
        self._send(204)
ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1])), H).serve_forever()
