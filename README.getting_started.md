Software defined infrastructure
--------------------------------------

The Piksel Managed Cloud Framework is designed on the principle that declarative
infrastructure design should be simple, and should work the same across all
development environments.  This framework allows you to declare, once, what the
infrastructure requirements of an application are, and then deploy that
infrastructure to any of a number of virtualization platforms and cloud providers.

High level overview
--------------------------------------

The starting point is the design of your application infrastructure, or 'stack'.
You write a definition of your infrastructure in any of several declarative
languages.  Although the YAML syntax is best supported, we also provide support
for the legacy C4 AWSFW XML syntax.

Your stack config is parsed and turned into an internal data structure by the
parser classes.  The internal data structure is then run through schema validation
classes to ensure that the data returned by the parser is syntactically correct,
contains all required data, and contains no unknown data types.

Then the internal data structure is run through a policy layer that applies
defaults to missing data points and ensures that field values are within
allowed parameters.  This is useful to ensure that instance sizes are one of
the values that are available as reserved instances, for example.

Finally, the data is run through an output layer, where it is transformed into
the structure necessary to communicate with a target API (in the case of public
cloud providers) or a JSON representation for inspection before deployment, and
so on.

Writing a config
--------------------------------------
There is sample config used as validators under tests/data/yaml/ that can be used
as a starting point, or you can examine the schemas directly under pmcf/schemas.

The YAML config format should correspond exactly to the internal data schema,
so the schema can be used as a reference for allowed fields.



