#!/usr/bin/xgawk -f

@load xml
@include xmlcopy

XMLDECLARATION {
    XmlCopy();
    printf("\n");
}

XMLSTARTELEM == "set" {
    XmlCopy();
    printf("\n");
}

XMLSTARTELEM == "seg" {
    delete attrs;
    for (i in XMLATTR)
        attrs[i] = XMLATTR[i];
}

XMLSTARTELEM == "source" {
    inSource = 1;
}

XMLSTARTELEM == "translation" {
    printf("<seg");
    for (i in attrs)
        printf(" %s=\"%s\"", i, attrs[i]);
    printf(">\n");
    printf("\t\t\t<source>%s</source>\n\t\t\t", sourceText);
    XmlCopy();
}

XMLCHARDATA {
    if (inSource) {
        sourceText = $0;
        gsub("<", "\\&lt;", sourceText);
        gsub(">", "\\&gt;", sourceText);
    } else # Must be a translation
        XmlCopy()
}

XMLENDELEM == "translation" {
    printf("</translation>\n\t\t</seg>\n");
}

XMLENDELEM == "source" {
    inSource = 0;
}

XMLENDELEM == "set" {
    XmlCopy();
}
