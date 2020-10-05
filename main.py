from JackTokenizer import JackTokenizer
from xml.sax.saxutils import escape

jtk = JackTokenizer('Main.jack')

print("<tokens>")

while(jtk.hasMoreTokens()):
    tokenType = jtk.tokenType()
    print("<" + tokenType + ">" + escape(jtk.getToken()) + "</" + tokenType + ">")
    jtk.advance()

print("</tokens>")

