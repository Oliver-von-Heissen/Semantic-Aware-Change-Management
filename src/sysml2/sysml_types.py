# Documentation of types at https://modeldocs.sysml2.net/

sysml_types = [
    {
        "type": "Package",
        "definition": "A Package is a Namespace used to group Elements, without any instance-level semantics.",
        "attributes": {
            "@type": "Package",
            "name": "The name of the package"
        }
    },
    {
        "type": "PartDefinition",
        "definition": "A PartDefinition is an ItemDefinition of a Class of systems or parts of systems.",
        "attributes": {
            "@type": "PartDefinition",
            "name": "The name of the part definition",
            "owner": { "@id": "[the id of the owner of this element]" }
        }
    },
    {
        "type": "PartUsage",
        "definition": "A PartUsage is a usage of a PartDefinition to represent a system or a part of a system.",
        "attributes": {
            "@type": "PartUsage",
            "name": "The name of the part",
            "owner": { "@id": "[the id of the owner of this element]" }
        }
    },
    {
        "type": "PortDefinition",
        "definition": "PortDefinition defines a point at which external entities can connect to and interact with a system or part of a system.",
        "attributes": {
            "@type": "PortDefinition",
            "name": "The name of the port definition",
            "owner": { "@id": "[the id of the owner of this element]" }
        }
    },
    {
        "type": "PortUsage",
        "definition": "A PortUsage is a usage of a PortDefinition.",
        "attributes": {
            "@type": "PortUsage",
            "name": "The name of the port usage.",
            "owner": { "@id": "[the id of the owner of this element]" }
        }
    },
    {
        "type": "ConnectionDefinition",
        "definition": "A ConnectionDefinition is a PartDefinition that is also an AssociationStructure.",
        "attributes": {
            "@type": "ConnectionDefinition",
            "name": "The name of the connection definition",
        }
    },
    {
        "type": "ConnectionUsage",
        "definition": "A ConnectionUsage is a ConnectorAsUsage that is also a PartUsage. Nominally, if its type is a ConnectionDefinition, then a ConnectionUsage is a Usage of that ConnectionDefinition, representing a connection between parts of a system.",
        "attributes": {
            "@type": "ConnectionUsage",
            "name": "The name of the connection usage",
        }
    },
]
