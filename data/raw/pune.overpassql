[out:json][timeout:90];
(
 nwr["name"]["shop"]["shop"!~"^(vacant|no|closed|disused)$"]["addr:street"](18.4,73.73,18.65,73.99);
 nwr["name"]["amenity"~"^(restaurant|cafe|fast_food|pharmacy|bank|dentist|clinic|fuel|bar|pub|ice_cream)$"]["addr:street"](18.4,73.73,18.65,73.99);
 nwr["name"]["shop"]["shop"!~"^(vacant|no|closed|disused)$"]["addr:full"](18.4,73.73,18.65,73.99);
 nwr["name"]["amenity"~"^(restaurant|cafe|fast_food|pharmacy|bank|dentist|clinic|fuel|bar|pub|ice_cream)$"]["addr:full"](18.4,73.73,18.65,73.99);
);
out tags;
