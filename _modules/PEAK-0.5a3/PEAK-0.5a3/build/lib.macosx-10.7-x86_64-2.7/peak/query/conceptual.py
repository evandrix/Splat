"""Queries based on Concept Filters

 Implement query objects similar to the ConQuer conceptual query language;
 see http://www.orm.net/queries.html for papers.

 Queries are expressed as logical conditions over traversals of a fact
 graph, where facts are mapped to aspects of a relational schema.


 Implementation Notes

  * NOT(FEATURE('x')) should translate to 'x IS NULL' if 'x' is a one-to-one
    feature, or 'parent NOT IN (SELECT ...)' if 'x' is a one-to-many feature.

"""
