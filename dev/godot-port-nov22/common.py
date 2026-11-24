import re
def T(s):
    """4-space indentation -> tabs (GDScript), leading whitespace only."""
    out=[]
    for line in s.split('\n'):
        m=re.match(r'^((?:    )*)',line); n=len(m.group(1))//4
        out.append('\t'*n+line[4*n:])
    return '\n'.join(out)
class F:
    def __init__(self,path): self.path=path; self.s=open(path).read()
    def rep(self,a,b,n=1,raw=False):
        if not raw: a,b=T(a),T(b)
        c=self.s.count(a); assert c==n,(self.path.split('/')[-1],c,a[:120]); self.s=self.s.replace(a,b)
    def save(self): open(self.path,'w').write(self.s)
