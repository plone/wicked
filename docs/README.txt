------------
:: wicked ::
------------

--> wiki style flavor without the bad wiki aftertaste <--


What::
------

 wicked is a framework addition to Archetypes to allow developers to add
 wiki-ish behavior to AT content objects via a schema field.



Guiding Principals::
--------------------

 - Easy link based creation of content

 - Easy intuitive linking of content by explicit wiki links

 - Simple reference system for relating interlinked content (ie. backlinks)

 - Wiki style linking should not be limited to a single content type



Examples::
----------

 wicked ships w/ two example content types. please note, these are examples for 
 demonstration purposes only. These example maybe installed using CMFQuickInstaller. 


 - IronicWiki:

   a barebones content type consisting of a single WikiField using 

  
 - WickedDoc:

   a subclass of ATCT Document using a WikiField for it's primary field


Field::
-------

 The WikiField is the emphasis of the product. Take it and use it in you're own product type.  
 Subclass it. Patch over ATCT's document's schema with it. This is what wicked is about.


 Linking::

  The wicked is very simple.  
  All links are specified by enclosing content text in double
  parentheses.  ex:

  ((This is a wicked link))

 see DETAILS.txt for more on link resolution

Credits
-------

 Authors:  Whit Morriss
           Rob Miller
	   Anders Pearson 

 Concepts: Alexander Limi
           Benjamin Saller
	   Alberto Berti

wicked uses ObjectRealms' Bricolite product as a model and borrows heavily
from it.
