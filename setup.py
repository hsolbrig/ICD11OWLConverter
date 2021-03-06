from distutils.core import setup

install_requires = [
    "rdflib",
    "py4j",
    "cherrypy",
    "routes"
]

setup(
    name='ICD11OWLConverter',
    version='0.0.1',
    packages=['ICD11OWLConverter'],
    url='',
    license='',
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    description='Front end for converting Compositional Grammar in ICD11 OWL constructs',
    requires=install_requires
)
