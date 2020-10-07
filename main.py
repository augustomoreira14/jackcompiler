from JackTokenizer import JackTokenizer
from xml.sax.saxutils import escape
import sys

try:

    jtk = JackTokenizer(sys.argv[1])

    print("<tokens>")

    while(jtk.hasMoreTokens()):
        tokenType = jtk.tokenType()
        print("<" + tokenType + ">" + escape(jtk.getToken()) + "</" + tokenType + ">")
        jtk.advance()

    print("</tokens>")
    
except FileNotFoundError:
    print("File not found.")

