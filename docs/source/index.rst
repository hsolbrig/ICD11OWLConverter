
ICD11 Compositional Grammar to OWL Conversion Tools
===================================================
This package contains tools designed to massage and manipulate ICD11 mapping files. It consists
of two packages:

:mod:`cgtoowl` Utility
-----------------------
The `cgtoowl` utility reads an OWL file and attempts to translate any SNOMED CT Compositional Grammar
expressions into OWL.  Everything in the input file is copied verbatim with the exception that the output format
may be different.  The targets of the form of (?s <http://who.int/field/Description.entity.en.Comments> ?t) are scanned
for the text: "(pre-coordinated)" or "(post-coordinated)" and, if found, URI's are stripped off of the end and the
result is sent to the SNOMED CT to OWL converter.  If the conversion is successful, the additional assertions are added
to the output document.

As an example, the following::

    <owl:Class rdf:about="http://id.who.int/icd/entity/435889652" xml:lang="en" icdf:reviewed="true">
        <rdfs:label>Myopericarditis</rdfs:label>
        <icdf:Description.entity.en.definition xml:lang="en">
             This is a combination of both myocarditis and pericarditis appearing in a single individual.
             Concomitant myopericarditis may develop in patients with pericarditis probably owing to direct
             extension of the inflammatory process.
        </icdf:Description.entity.en.definition>
        <rdfs:subClassOf rdf:resource="http://id.who.int/icd/entity/2099186145"/>
        <icdf:Description.entity.en.synonym xml:lang="en"> Perimyocarditis </icdf:Description.entity.en.synonym>
        <icdf:Description.entity.en.MapType>0/A</icdf:Description.entity.en.MapType>
        <icdf:Description.entity.en.Comments>
            11176009 Acute myopericarditis (disorder) to be child concept Expression
            (pre-coordinated) 50920009 | Myocarditis | + 3238004 | Pericarditis |
        </icdf:Description.entity.en.Comments>
    </owl:Class>

would generate the following output::

 <owl:Class rdf:about="http://id.who.int/icd/entity/435889652" xml:lang="en" icdf:reviewed="true">
        <rdfs:label>Myopericarditis</rdfs:label>
        <icdf:Description.entity.en.definition xml:lang="en">
             This is a combination of both myocarditis and pericarditis appearing in a single individual.
             Concomitant myopericarditis may develop in patients with pericarditis probably owing to direct
             extension of the inflammatory process.
        </icdf:Description.entity.en.definition>
        <rdfs:subClassOf rdf:resource="http://id.who.int/icd/entity/2099186145"/>
        <icdf:Description.entity.en.synonym xml:lang="en"> Perimyocarditis </icdf:Description.entity.en.synonym>
        <icdf:Description.entity.en.MapType>0/A</icdf:Description.entity.en.MapType>
        <icdf:Description.entity.en.Comments>
            11176009 Acute myopericarditis (disorder) to be child concept Expression
            (pre-coordinated) 50920009 | Myocarditis | + 3238004 | Pericarditis |
        </icdf:Description.entity.en.Comments>
        <rdfs:subClassOf>
            <owl:Class>
               <owl:intersectionOf rdf:parseType="Collection">
                  <rdf:Description rdf:about="http://snomed.info/id/3238004"/>
                  <rdf:Description rdf:about="http://snomed.info/id/50920009"/>
               </owl:intersectionOf>
            </owl:Class>
        </rdfs:subClassOf>
 </owl:Class>

If the *primitive* tag is "True" or::

   <owl:Class rdf:about="http://id.who.int/icd/entity/435889652" xml:lang="en" icdf:reviewed="true">
        <rdfs:label>Myopericarditis</rdfs:label>
        <icdf:Description.entity.en.definition xml:lang="en">
             This is a combination of both myocarditis and pericarditis appearing in a single individual.
             Concomitant myopericarditis may develop in patients with pericarditis probably owing to direct
             extension of the inflammatory process.
        </icdf:Description.entity.en.definition>
        <rdfs:subClassOf rdf:resource="http://id.who.int/icd/entity/2099186145"/>
        <icdf:Description.entity.en.synonym xml:lang="en"> Perimyocarditis </icdf:Description.entity.en.synonym>
        <icdf:Description.entity.en.MapType>0/A</icdf:Description.entity.en.MapType>
        <icdf:Description.entity.en.Comments>
            11176009 Acute myopericarditis (disorder) to be child concept Expression
            (pre-coordinated) 50920009 | Myocarditis | + 3238004 | Pericarditis |
        </icdf:Description.entity.en.Comments>
        <owl:equivalentClass>
            <owl:Class>
               <owl:intersectionOf rdf:parseType="Collection">
                  <rdf:Description rdf:about="http://snomed.info/id/3238004"/>
                  <rdf:Description rdf:about="http://snomed.info/id/50920009"/>
               </owl:intersectionOf>
            </owl:Class>
        </owl:equivalentClass>
   </owl:Class>

 otherwise.

Invocation
```````````
::

   usage: cgtoowl.py [-h] [-f] [-p PORT] -o OUT [-s] owlfile

   Generate OWL from Comments in an ICD-11 file

   positional arguments:
      owlfile               Input OWL file

   optional arguments:
      -h, --help            show this help message and exit
      -f, --fullydefined    Definitions are fully defined
      -p PORT, --port PORT  SCT Converter gateway port
      -o OUT, --out OUT     Output file
      -s, --shorturi        Shorten URI's for readability


:mod:`tagadder` Utility
------------------------
Contents:

.. toctree::
   :maxdepth: 2

.. automodule:: ICD11OWLConverter.cgtoowl
.. automodule:: ICD11OWLConverter.tagadder

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

