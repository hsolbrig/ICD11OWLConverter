ICD11OWLConverter
=================

Gateway to the CG to OWL Java tools.  Used as a batch converter and an online gateway.

This has been tested using Python 3.4.1 and requires the following packages:

isodate==0.5.1
py4j==0.8.2.1
pyparsing==2.0.3
rdflib==4.1.2

It also assumes that a py4j server image is running tha provides access to a modified version of
[Daniel Karlsson's SNOMEDCTParser](https://github.com/danka74/SnomedCTParser).  The modifications are:

1. A change to the SNOMEDCTOWLParser and SNOMEDCTParsorFactory to allow an external subject URI to be supplied.
2. An additional package that creates a py4j front end process and initializes a CGToOWL instances
3. A CGToOWL instances that exposes a parse method that takes a subject and a compositional grammar string and returns
the translation to OWL

Usage:
======
1.  Start the converter gateway:
    **java -jar javalib/SCTConverter.jar**
    
2.  Execute the converter:
    **python3 ICD11OWLConverter/converter.py -o {output file} {ICD11 OWL file}**
    

The output file will be a copy of the input file

